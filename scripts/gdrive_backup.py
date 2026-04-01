#!/usr/bin/env python3
"""Google Drive backup wrapper around rclone.

Manages one-way archive backups (``rclone sync`` with ``--backup-dir``)
and two-way bisync (``rclone bisync``) from a single TOML config.

Config file: ``~/.config/gdrive-backup/config.toml``

Modes:

- ``archive`` -- Syncs source to ``{remote}/{name}/current/``, moving
  changed/deleted files to ``{remote}/{name}/archive/{date}/``.
  Supports retention-based pruning of old archives.
- ``bisync`` -- Two-way sync between source and remote using
  ``rclone bisync --resilient``.

CLI::

    gdrive_backup.py                  # run all backup sets
    gdrive_backup.py --mode archive   # run only archive sets
    gdrive_backup.py --mode bisync    # run only bisync sets
    gdrive_backup.py --only minetest  # run one named set
    gdrive_backup.py --list           # show configured sets
    gdrive_backup.py --dry-run        # pass --dry-run to rclone
    gdrive_backup.py --prune-only     # just clean old archives
"""

from __future__ import annotations

import argparse
import fcntl
import logging
import os
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

log = logging.getLogger("gdrive-backup")

DEFAULT_CONFIG = Path("~/.config/gdrive-backup/config.toml").expanduser()
LOCK_PATH = Path("/tmp/gdrive_backup.lock")
RCLONE_TIMEOUT = 600


@dataclass
class Defaults:
    """Global defaults from the ``[defaults]`` config section."""

    remote: str
    retain_days: int = 90
    notify_email: str = ""


@dataclass
class BackupSet:
    """A single ``[[backup]]`` entry."""

    name: str
    mode: str
    source: Path
    remote: str = ""
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)


@dataclass
class Config:
    """Parsed configuration."""

    defaults: Defaults
    backups: list[BackupSet]


def expand(value: str) -> str:
    """Expand environment variables and ``~`` in a string value."""
    return os.path.expandvars(os.path.expanduser(value))


def load_config(path: Path) -> Config:
    """Parse the TOML config file.

    Args:
        path: Path to the config file.

    Returns:
        Parsed Config with expanded paths.

    Raises:
        SystemExit: If the file is missing or malformed.
    """
    if not path.exists():
        raise SystemExit(f"Config not found: {path}")
    with path.open("rb") as f:
        raw = tomllib.load(f)

    defaults_raw = raw.get("defaults", {})
    if "remote" not in defaults_raw:
        raise SystemExit("Config missing [defaults].remote")

    defaults = Defaults(
        remote=expand(defaults_raw["remote"]),
        retain_days=defaults_raw.get("retain_days", 90),
        notify_email=expand(defaults_raw.get("notify_email", "")),
    )

    backups: list[BackupSet] = []
    for entry in raw.get("backup", []):
        for key in ("name", "mode", "source"):
            if key not in entry:
                raise SystemExit(f"Backup set missing required field: {key}")
        if entry["mode"] not in ("archive", "bisync"):
            raise SystemExit(
                f"Backup '{entry['name']}': mode must be 'archive' or 'bisync', "
                f"got '{entry['mode']}'"
            )
        backups.append(
            BackupSet(
                name=entry["name"],
                mode=entry["mode"],
                source=Path(expand(entry["source"])),
                remote=expand(entry.get("remote", "")),
                include=entry.get("include", []),
                exclude=entry.get("exclude", []),
            )
        )

    if not backups:
        raise SystemExit("Config has no [[backup]] sets defined")

    return Config(defaults=defaults, backups=backups)


def resolve_remote(backup: BackupSet, defaults: Defaults) -> str:
    """Return the effective remote for a backup set.

    Args:
        backup: The backup set.
        defaults: Global defaults.

    Returns:
        Remote string (e.g. ``"gdrive:backups/pi"``).
    """
    return backup.remote or defaults.remote


def build_filter_file(
    include: list[str], exclude: list[str]
) -> Path | None:
    """Write rclone filter rules to a temporary file.

    Args:
        include: Glob patterns to include.
        exclude: Glob patterns to exclude.

    Returns:
        Path to the temp filter file, or ``None`` if no filters needed.
    """
    if not include and not exclude:
        return None

    lines: list[str] = []
    for pattern in include:
        lines.append(f"+ {pattern}")
    for pattern in exclude:
        lines.append(f"- {pattern}")
    if include:
        lines.append("- **")

    fd, path_str = tempfile.mkstemp(
        prefix="gdrive_backup_filter_", suffix=".txt"
    )
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines) + "\n")
    return Path(path_str)


def build_archive_cmd(
    backup: BackupSet,
    defaults: Defaults,
    today: str,
    dry_run: bool = False,
) -> list[str]:
    """Assemble the rclone sync command for archive mode.

    Args:
        backup: The backup set configuration.
        defaults: Global defaults.
        today: Date string for the archive dir (``YYYY-MM-DD``).
        dry_run: If ``True``, add ``--dry-run``.

    Returns:
        Complete rclone command as a string list.
    """
    remote = resolve_remote(backup, defaults)
    cmd = [
        "rclone",
        "sync",
        str(backup.source),
        f"{remote}/{backup.name}/current",
        "--backup-dir",
        f"{remote}/{backup.name}/archive/{today}",
        "--log-level",
        "INFO",
    ]
    if dry_run:
        cmd.append("--dry-run")

    filter_path = build_filter_file(backup.include, backup.exclude)
    if filter_path is not None:
        cmd.extend(["--filter-from", str(filter_path)])

    return cmd


def build_bisync_cmd(
    backup: BackupSet,
    defaults: Defaults,
    dry_run: bool = False,
) -> list[str]:
    """Assemble the rclone bisync command.

    Args:
        backup: The backup set configuration.
        defaults: Global defaults.
        dry_run: If ``True``, add ``--dry-run``.

    Returns:
        Complete rclone command as a string list.
    """
    remote = resolve_remote(backup, defaults)
    cmd = [
        "rclone",
        "bisync",
        str(backup.source),
        remote,
        "--resilient",
        "--recover",
        "--log-level",
        "INFO",
    ]
    if dry_run:
        cmd.append("--dry-run")

    filter_path = build_filter_file(backup.include, backup.exclude)
    if filter_path is not None:
        cmd.extend(["--filter-from", str(filter_path)])

    return cmd


def check_first_run(backup: BackupSet, defaults: Defaults) -> bool:
    """Detect whether this is the first run for an archive backup set.

    Args:
        backup: The backup set.
        defaults: Global defaults.

    Returns:
        ``True`` if no ``current/`` directory exists on the remote.
    """
    if backup.mode != "archive":
        return False
    remote = resolve_remote(backup, defaults)
    try:
        result = subprocess.run(
            ["rclone", "lsf", f"{remote}/{backup.name}/current/"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        log.warning("Timed out checking remote for '%s'; assuming first run.", backup.name)
        return True
    return result.returncode != 0 or not result.stdout.strip()


def run_backup(
    backup: BackupSet,
    defaults: Defaults,
    dry_run: bool = False,
) -> bool:
    """Execute a single backup set.

    Args:
        backup: The backup set to run.
        defaults: Global defaults.
        dry_run: If ``True``, pass ``--dry-run`` to rclone.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    if not backup.source.exists():
        log.error("Source does not exist: %s", backup.source)
        return False

    today = date.today().isoformat()
    if backup.mode == "archive":
        cmd = build_archive_cmd(backup, defaults, today, dry_run)
    else:
        cmd = build_bisync_cmd(backup, defaults, dry_run)

    log.info("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=RCLONE_TIMEOUT,
        )
        if result.stdout:
            log.info("%s", result.stdout.rstrip())
        if result.returncode != 0:
            log.error(
                "rclone failed for '%s': %s",
                backup.name,
                result.stderr.rstrip(),
            )
            return False
        log.info("Completed '%s' successfully.", backup.name)
        return True
    except subprocess.TimeoutExpired:
        log.error(
            "rclone timed out for '%s' after %ds", backup.name, RCLONE_TIMEOUT
        )
        return False


def list_archive_dates(
    backup: BackupSet, defaults: Defaults
) -> list[date]:
    """List existing archive dates on the remote.

    Args:
        backup: The backup set.
        defaults: Global defaults.

    Returns:
        Sorted list of archive dates found.
    """
    remote = resolve_remote(backup, defaults)
    archive_path = f"{remote}/{backup.name}/archive/"

    result = subprocess.run(
        ["rclone", "lsf", "--dirs-only", archive_path],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return []

    dates: list[date] = []
    for line in result.stdout.strip().splitlines():
        dirname = line.strip().rstrip("/")
        try:
            dates.append(date.fromisoformat(dirname))
        except ValueError:
            continue
    return sorted(dates)


def prune_archives(
    backup: BackupSet, defaults: Defaults, retain_days: int
) -> None:
    """Delete archive directories older than ``retain_days``.

    Only applies to archive-mode backup sets.

    Args:
        backup: The backup set.
        defaults: Global defaults.
        retain_days: Number of days to retain.
    """
    if backup.mode != "archive":
        return

    remote = resolve_remote(backup, defaults)
    archive_path = f"{remote}/{backup.name}/archive/"
    cutoff = date.today() - timedelta(days=retain_days)

    for archive_date in list_archive_dates(backup, defaults):
        if archive_date < cutoff:
            target = f"{archive_path}{archive_date.isoformat()}"
            log.info("Pruning old archive: %s", target)
            subprocess.run(
                ["rclone", "purge", target],
                capture_output=True,
                timeout=60,
            )


def notify_failure(email: str, failures: list[str]) -> None:
    """Send a failure notification via neomutt.

    Args:
        email: Recipient email address.
        failures: Backup set names that failed.
    """
    if not email or not failures:
        return
    subject = f"gdrive-backup: {len(failures)} set(s) failed"
    body = (
        f"The following backup sets failed on {date.today().isoformat()}:\n\n"
        + "\n".join(f"  - {name}" for name in failures)
        + "\n\nCheck logs: journalctl -t gdrive-backup\n"
    )
    try:
        subprocess.run(
            ["neomutt", "-s", subject, "--", email],
            input=body,
            text=True,
            capture_output=True,
            timeout=30,
        )
        log.info("Failure notification sent to %s", email)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        log.error("Failed to send notification: %s", exc)


def acquire_lock() -> int:
    """Acquire an exclusive file lock to prevent concurrent runs.

    Returns:
        The lock file descriptor.

    Raises:
        SystemExit: If another instance holds the lock.
    """
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError:
        log.info("Another instance is running. Skipping.")
        os.close(fd)
        raise SystemExit(0)


def list_backups(config: Config) -> None:
    """Print configured backup sets to stdout.

    Args:
        config: Parsed configuration.
    """
    for b in config.backups:
        remote = resolve_remote(b, config.defaults)
        print(f"  {b.name:20s}  {b.mode:8s}  {b.source} -> {remote}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Parsed namespace.
    """
    parser = argparse.ArgumentParser(
        description="Google Drive backup wrapper around rclone.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to config file (default: %(default)s)",
    )
    parser.add_argument(
        "--only",
        metavar="NAME",
        help="Run only the named backup set",
    )
    parser.add_argument(
        "--mode",
        choices=("archive", "bisync"),
        help="Run only backup sets of this mode",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Pass --dry-run to rclone",
    )
    parser.add_argument(
        "--prune-only",
        action="store_true",
        help="Only prune old archives, don't run backups",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_sets",
        help="List configured backup sets and exit",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code: 0 on success, 1 if any backup failed.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )

    args = parse_args(argv)
    config = load_config(args.config)

    if args.list_sets:
        list_backups(config)
        return 0

    lock_fd = acquire_lock()
    try:
        sets = config.backups
        if args.only:
            sets = [b for b in sets if b.name == args.only]
            if not sets:
                log.error("No backup set named '%s'", args.only)
                return 1
        if args.mode:
            sets = [b for b in sets if b.mode == args.mode]
            if not sets:
                log.info("No %s sets to run.", args.mode)
                return 0

        if args.prune_only:
            for backup in sets:
                prune_archives(
                    backup, config.defaults, config.defaults.retain_days
                )
            return 0

        failures: list[str] = []
        for backup in sets:
            log.info("=== %s (%s) ===", backup.name, backup.mode)
            if not run_backup(backup, config.defaults, args.dry_run):
                failures.append(backup.name)
            prune_archives(
                backup, config.defaults, config.defaults.retain_days
            )

        if failures:
            log.error("Failed sets: %s", ", ".join(failures))
            notify_failure(config.defaults.notify_email, failures)
            return 1
        return 0
    finally:
        os.close(lock_fd)


if __name__ == "__main__":
    raise SystemExit(main())
