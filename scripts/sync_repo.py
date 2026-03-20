#!/usr/bin/env python3
"""Bidirectional git sync engine.

Syncs a local git repository with its remote on a schedule. Designed
to run unattended as a macOS LaunchAgent for iCloud-hosted folders.

Behavior:

- Force-download any iCloud-evicted files via ``brctl``.
- Commit and push local changes if present.
- Pull (merge) when remote is ahead.
- On conflict, keep ours and save theirs as ``_conflicted`` files.
- Push again if local is ahead after pull.
- Send a macOS notification on error.

Prerequisites (macOS):

- ``/usr/bin/git`` must have **Full Disk Access** in System Settings →
  Privacy & Security. Without it, ``git fetch`` intermittently fails with
  "Unable to read current working directory: Operation not permitted".

Environment variables (set via LaunchAgent plist):

- ``REPO_DIR`` -- Path to the local git repo (default: ``~/homeschool``).
- ``BRANCH`` -- Remote branch to sync (default: ``main``).
- ``LOGFILE`` -- Log output path
  (default: ``~/Library/Logs/homeschool-sync.log``).
"""

from __future__ import annotations

import fcntl
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(os.getenv("REPO_DIR", str(Path.home() / "homeschool")))
BRANCH = os.getenv("BRANCH", "main")
LOGFILE = Path(
    os.getenv("LOGFILE", str(Path.home() / "Library/Logs/homeschool-sync.log"))
)
GIT_TIMEOUT = 120
GIT_BIN = "/usr/bin/git" if Path("/usr/bin/git").exists() else "git"
MAX_LOG_LINES = 2000


def log(message: str) -> None:
    """Append a timestamped message to the log file.

    Args:
        message: Text to log.
    """
    timestamp = datetime.now().isoformat(timespec="seconds")
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    with LOGFILE.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")


def truncate_log() -> None:
    """Trim the log file to the most recent ``MAX_LOG_LINES`` lines."""
    if not LOGFILE.exists():
        return
    lines = LOGFILE.read_text().splitlines()
    if len(lines) > MAX_LOG_LINES:
        LOGFILE.write_text("\n".join(lines[-MAX_LOG_LINES:]) + "\n")


def notify_error(message: str) -> None:
    """Send a macOS notification with an error sound.

    No-op on non-Darwin platforms.

    Args:
        message: Notification body text.
    """
    if platform.system() != "Darwin":
        return
    safe_message = message.replace("\\", "\\\\").replace('"', '\\"')
    safe_title = REPO_DIR.name.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        [
            "osascript",
            "-e",
            (
                f'display notification "{safe_message}" '
                f'with title "{safe_title} sync error" '
                f'sound name "Basso"'
            ),
        ],
        capture_output=True,
    )


def run_git(
    args: list[str], allow_fail: bool = False
) -> subprocess.CompletedProcess:
    """Run a git command in ``REPO_DIR``.

    Args:
        args: Git subcommand and arguments (e.g. ``["fetch", "origin"]``).
        allow_fail: When ``True``, don't raise on non-zero exit.

    Returns:
        The completed process result.

    Raises:
        SystemExit: On timeout (via ``fail``).
        subprocess.CalledProcessError: On non-zero exit when
            ``allow_fail`` is ``False``.
    """
    try:
        return subprocess.run(
            [GIT_BIN] + args,
            cwd=REPO_DIR,
            check=not allow_fail,
            text=True,
            capture_output=True,
            timeout=GIT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        fail(f"git {' '.join(args)} timed out after {GIT_TIMEOUT}s")
        raise  # unreachable, satisfies type checker


def fail(message: str, code: int = 1, detail: str = "") -> None:
    """Log an error, notify the user, and exit.

    Args:
        message: Error summary.
        code: Process exit code.
        detail: Additional context (e.g. git stderr).

    Raises:
        SystemExit: Always.
    """
    log(f"[ERROR] {message}")
    if detail:
        log(f"[DETAIL] {detail}")
    notify_error(message)
    raise SystemExit(code)


def acquire_lock() -> int:
    """Acquire an exclusive file lock to prevent concurrent runs.

    Uses a per-repo lockfile in ``/tmp``.

    Returns:
        The lock file descriptor.

    Raises:
        SystemExit: With code 0 if another instance holds the lock.
    """
    lock_path = Path(f"/tmp/sync_repo_{REPO_DIR.name}.lock")
    fd = os.open(str(lock_path), os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError:
        log("Another sync is already running. Skipping.")
        os.close(fd)
        raise SystemExit(0)


def ensure_repo() -> None:
    """Verify that ``REPO_DIR`` exists and is a git repository.

    Raises:
        SystemExit: If the directory or ``.git`` is missing.
    """
    if not REPO_DIR.exists():
        fail(f"REPO_DIR does not exist: {REPO_DIR}")
    if not (REPO_DIR / ".git").exists():
        fail(f"REPO_DIR is not a git repository: {REPO_DIR}")


def recover_dirty_state() -> None:
    """Abort any interrupted merge or rebase from a previous run."""
    if (REPO_DIR / ".git" / "MERGE_HEAD").exists():
        log("Found interrupted merge. Aborting it to start fresh.")
        run_git(["merge", "--abort"], allow_fail=True)
    rebase_dir = REPO_DIR / ".git" / "rebase-merge"
    rebase_apply = REPO_DIR / ".git" / "rebase-apply"
    if rebase_dir.exists() or rebase_apply.exists():
        log("Found interrupted rebase. Aborting it to start fresh.")
        run_git(["rebase", "--abort"], allow_fail=True)


def download_icloud_files() -> None:
    """Force-download any iCloud-evicted files in ``REPO_DIR``.

    Prevents ``git add`` from staging cloud-only placeholder stubs.
    No-op on non-Darwin platforms or if ``brctl`` is unavailable.
    """
    if platform.system() != "Darwin":
        return
    try:
        subprocess.run(
            ["brctl", "download", str(REPO_DIR)],
            capture_output=True,
            timeout=300,
        )
        log("iCloud download check completed.")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        log("brctl not available or timed out; skipping iCloud download.")


def has_uncommitted_changes() -> bool:
    """Check whether the working tree has uncommitted changes.

    Returns:
        ``True`` if ``git status --porcelain`` produces output.
    """
    result = run_git(["status", "--porcelain"], allow_fail=True)
    return bool(result.stdout.strip())


def get_commit_delta() -> tuple[int, int]:
    """Count commits ahead of and behind the remote tracking branch.

    Assumes ``git fetch`` has already been called this run.

    Returns:
        A ``(ahead, behind)`` tuple.
    """
    ahead = int(
        run_git(
            ["rev-list", "--count", f"origin/{BRANCH}..{BRANCH}"]
        ).stdout.strip()
    )
    behind = int(
        run_git(
            ["rev-list", "--count", f"{BRANCH}..origin/{BRANCH}"]
        ).stdout.strip()
    )
    return ahead, behind


def handle_merge_conflicts() -> None:
    """Resolve merge conflicts by keeping ours and saving theirs.

    For each unmerged file, checks out the local ("ours") version and
    writes the remote ("theirs") version to a ``_conflicted`` sibling.
    Handles all conflict types (UU, AA, DU, UD, DD).
    """
    result = run_git(
        ["diff", "--name-only", "--diff-filter=U"], allow_fail=True
    )
    if not result.stdout.strip():
        return
    conflicted = result.stdout.strip().splitlines()
    for file_path in conflicted:
        file_path = file_path.strip()
        src = REPO_DIR / file_path
        dst = src.with_name(src.stem + "_conflicted" + src.suffix)
        theirs = run_git(["show", f":3:{file_path}"], allow_fail=True)
        if theirs.returncode == 0 and theirs.stdout:
            dst.write_text(theirs.stdout)
            run_git(["add", str(dst)])
        run_git(["checkout", "--ours", file_path], allow_fail=True)
        run_git(["add", file_path])
    log(
        f"Resolved {len(conflicted)} conflict(s) "
        f"-- theirs saved as _conflicted files."
    )


def build_commit_message() -> str:
    """Build a timestamped commit message for auto-sync commits.

    Returns:
        A message in the form ``sync [YYYY-MM-DDTHH:MM]``.
    """
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return f"sync [{timestamp}]"


def sync() -> None:
    """Run a single bidirectional sync cycle.

    Commits and pushes local changes, fetches and merges remote
    changes, resolves any conflicts, and pushes the result. Acquires
    an exclusive lock so concurrent runs are skipped.
    """
    log("=== Starting sync ===")
    ensure_repo()
    lock_fd = acquire_lock()
    try:
        recover_dirty_state()
        download_icloud_files()

        if has_uncommitted_changes():
            log("Uncommitted changes found; committing and pushing...")
            run_git(["add", "-A"])
            try:
                run_git(["commit", "-m", build_commit_message()])
            except subprocess.CalledProcessError:
                log("Nothing to commit.")
            run_git(["push", "origin", BRANCH])
            log("Push completed.")

        run_git(["fetch", "origin"])
        ahead, behind = get_commit_delta()
        log(f"Commits ahead: {ahead}, behind: {behind}")

        if behind > 0:
            log("Pulling from remote...")
            try:
                run_git(["pull", "--no-rebase", "origin", BRANCH])
            except subprocess.CalledProcessError:
                log("Merge conflict during pull. Resolving conflicts.")
                handle_merge_conflicts()
                run_git(["commit", "--no-edit"], allow_fail=True)

        ahead, _ = get_commit_delta()
        if ahead > 0:
            log("Pushing after pull...")
            run_git(["push", "origin", BRANCH])
            log("Push completed.")

        log("=== Sync complete ===\n")
    finally:
        os.close(lock_fd)
    truncate_log()


def main() -> int:
    """Entry point. Catches unhandled exceptions and routes to ``fail``.

    Returns:
        Exit code (0 on success).
    """
    try:
        sync()
    except SystemExit:
        raise
    except subprocess.CalledProcessError as exc:
        fail(str(exc), detail=exc.stderr.strip())
    except Exception as exc:
        fail(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
