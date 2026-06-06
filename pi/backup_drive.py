#!/usr/bin/env python3
"""Maintain one removable drive as bootable mirror plus linked snapshots."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import signal
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterable, Sequence
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path


DEFAULT_STATE_DIR = Path("/var/lib/pi-backup")
DEFAULT_MOUNT_ROOT = Path("/mnt/pi-backup")
DEFAULT_SOURCE_ROOT = Path("/run/pi-backup/source")
LOCK_PATH = Path("/run/lock/pi-backup.lock")

ROOT_EXCLUDES = (
    "/backup/***",
    "/boot/firmware/***",
    "/dev/***",
    "/lost+found",
    "/media/***",
    "/mnt/***",
    "/proc/***",
    "/run/***",
    "/sys/***",
    "/tmp/***",
    "/var/cache/apt/***",
    "/home/*/.cache/***",
    "/home/*/.local/share/Trash/***",
)


@dataclass(frozen=True)
class Config:
    """Machine-specific backup identity and retention settings."""

    disk_serial: str
    boot_label: str
    root_label: str
    retention: int = 4
    state_dir: Path = DEFAULT_STATE_DIR
    mount_root: Path = DEFAULT_MOUNT_ROOT

    @property
    def boot_mount(self) -> Path:
        return self.mount_root / "boot"

    @property
    def root_mount(self) -> Path:
        return self.mount_root / "root"

    @property
    def snapshots_dir(self) -> Path:
        return self.root_mount / "backup" / "snapshots"


@dataclass(frozen=True)
class Device:
    """A serial-verified disk and its expected partitions."""

    disk: Path
    boot: Path
    root: Path


@dataclass(frozen=True)
class MountLease:
    """A verified mount and whether this invocation created it."""

    device: Path
    target: Path
    created: bool


class BackupInterrupted(RuntimeError):
    """Raised when a termination request interrupts an active backup."""


def run_command(
    args: Sequence[str],
    *,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run one external command with logging and predictable text output."""
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(
        list(map(str, args)),
        check=check,
        text=True,
        capture_output=capture,
    )


def progress_log(verbosity: str, message: str) -> None:
    """Emit an immediate human-readable progress message when requested."""
    if verbosity != "quiet":
        print(f"pi-backup: {message}", flush=True)


def command_output(args: Sequence[str]) -> str:
    """Return stripped stdout from a successful command."""
    return run_command(args, capture=True).stdout.strip()


def require_root() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("must run as root")


def load_config() -> Config:
    """Load configuration from environment variables supplied by systemd."""
    required = {
        name: os.environ.get(name, "").strip()
        for name in (
            "PI_BACKUP_DISK_SERIAL",
            "PI_BACKUP_BOOT_LABEL",
            "PI_BACKUP_ROOT_LABEL",
        )
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"{', '.join(missing)} required")
    retention = int(os.environ.get("PI_BACKUP_RETENTION", "4"))
    if retention < 1:
        raise RuntimeError("PI_BACKUP_RETENTION must be at least 1")
    return Config(
        disk_serial=required["PI_BACKUP_DISK_SERIAL"],
        boot_label=required["PI_BACKUP_BOOT_LABEL"],
        root_label=required["PI_BACKUP_ROOT_LABEL"],
        retention=retention,
        state_dir=Path(os.environ.get("PI_BACKUP_STATE_DIR", DEFAULT_STATE_DIR)),
        mount_root=Path(os.environ.get("PI_BACKUP_MOUNT_ROOT", DEFAULT_MOUNT_ROOT)),
    )


def parse_lsblk(payload: str, serial: str) -> Path:
    """Select exactly one whole disk matching the configured serial."""
    devices = json.loads(payload)["blockdevices"]
    matches = [
        Path(device["path"])
        for device in devices
        if device.get("type") == "disk"
        and (device.get("serial") or "").strip() == serial
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one disk with serial {serial!r}; found {len(matches)}"
        )
    return matches[0]


def find_disk(serial: str) -> Path:
    payload = command_output(
        ["lsblk", "--json", "--paths", "--output", "PATH,TYPE,SERIAL"]
    )
    return parse_lsblk(payload, serial)


def device_for_label(label: str) -> Path:
    path = command_output(["blkid", "-L", label])
    if not path:
        raise RuntimeError(f"filesystem label {label!r} not found")
    return Path(path)


def parent_disk(partition: Path) -> Path:
    parent = command_output(["lsblk", "-no", "PKNAME", partition])
    if not parent:
        raise RuntimeError(f"cannot resolve parent disk for {partition}")
    return Path("/dev") / parent


def resolve_devices(config: Config) -> Device:
    """Resolve labels and prove both partitions belong to the serialled disk."""
    disk = find_disk(config.disk_serial)
    boot = device_for_label(config.boot_label)
    root = device_for_label(config.root_label)
    if parent_disk(boot) != disk or parent_disk(root) != disk:
        raise RuntimeError("backup labels do not belong to the configured disk")
    return Device(disk=disk, boot=boot, root=root)


def unmount_children(disk: Path) -> None:
    """Unmount any mounted partition belonging to the target disk."""
    payload = json.loads(
        command_output(
            [
                "lsblk",
                "--json",
                "--paths",
                "--output",
                "PATH,TYPE,MOUNTPOINTS",
                disk,
            ]
        )
    )
    for child in payload["blockdevices"][0].get("children", []):
        for mountpoint in child.get("mountpoints") or []:
            if mountpoint:
                run_command(["umount", mountpoint])


def prepare_drive(config: Config) -> Device:
    """Destructively create the fixed boot/root layout on the configured disk."""
    disk = find_disk(config.disk_serial)
    if str(disk).startswith("/dev/nvme"):
        raise RuntimeError(f"refusing to repartition NVMe device {disk}")

    unmount_children(disk)
    run_command(["wipefs", "--all", disk])
    run_command(["parted", "--script", disk, "mklabel", "gpt"])
    run_command(
        [
            "parted",
            "--script",
            disk,
            "mkpart",
            "boot",
            "fat32",
            "1MiB",
            "1025MiB",
        ]
    )
    run_command(["parted", "--script", disk, "set", "1", "boot", "on"])
    run_command(
        [
            "parted",
            "--script",
            disk,
            "mkpart",
            "root",
            "ext4",
            "1025MiB",
            "100%",
        ]
    )
    run_command(["partprobe", disk])
    run_command(["udevadm", "settle"])

    children = command_output(
        ["lsblk", "-nrpo", "PATH,TYPE", disk]
    ).splitlines()
    partitions = [
        Path(line.split()[0])
        for line in children
        if line.split()[1] == "part"
    ]
    if len(partitions) != 2:
        raise RuntimeError(f"expected two target partitions; found {len(partitions)}")

    run_command(["mkfs.vfat", "-F", "32", "-n", config.boot_label, partitions[0]])
    run_command(
        ["mkfs.ext4", "-F", "-m", "0", "-L", config.root_label, partitions[1]]
    )
    checked = run_command(["e2fsck", "-f", "-p", partitions[1]], check=False)
    if checked.returncode not in (0, 1, 2):
        raise RuntimeError(f"e2fsck failed with status {checked.returncode}")
    run_command(["udevadm", "settle"])
    return resolve_devices(config)


def mounted_source(target: Path) -> str:
    """Return the source mounted at target, or an empty string when unused."""
    completed = run_command(
        ["findmnt", "-nro", "SOURCE", "--mountpoint", target],
        capture=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def mounted_identity(target: Path) -> str:
    """Return the major:minor identity mounted at target, if any."""
    completed = run_command(
        ["findmnt", "-nro", "MAJ:MIN", "--mountpoint", target],
        capture=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def device_identity(device: Path) -> str:
    """Return the stable major:minor identity for a block device."""
    identity = command_output(["lsblk", "-dnro", "MAJ:MIN", device])
    if not identity:
        raise RuntimeError(f"cannot resolve device identity for {device}")
    return identity


def mounted_targets(identity: str) -> list[Path]:
    """Return all mount targets backed by a device identity."""
    completed = run_command(
        ["findmnt", "-rn", "-o", "TARGET,MAJ:MIN"],
        capture=True,
        check=False,
    )
    if completed.returncode not in (0, 1):
        raise RuntimeError("cannot enumerate current mounts")
    targets: list[Path] = []
    for line in completed.stdout.splitlines():
        fields = line.rsplit(maxsplit=1)
        if len(fields) == 2 and fields[1] == identity:
            targets.append(Path(fields[0]))
    return targets


def parse_mount_targets(payload: str) -> list[Path]:
    """Flatten findmnt JSON into absolute mount targets."""
    targets: list[Path] = []

    def visit(filesystems: Iterable[dict[str, object]]) -> None:
        for filesystem in filesystems:
            target = filesystem.get("target")
            if isinstance(target, str) and target.startswith("/"):
                targets.append(Path(target))
            children = filesystem.get("children")
            if isinstance(children, list):
                visit(children)

    filesystems = json.loads(payload).get("filesystems", [])
    if isinstance(filesystems, list):
        visit(filesystems)
    return targets


def nested_mount_excludes() -> tuple[str, ...]:
    """Exclude every currently mounted subtree from the root capture."""
    payload = command_output(["findmnt", "--json", "--output", "TARGET"])
    patterns = {
        f"{target}/***"
        for target in parse_mount_targets(payload)
        if target != Path("/")
    }
    return tuple(sorted(patterns))


def merged_excludes(*groups: Iterable[str]) -> tuple[str, ...]:
    """Combine exclusion policy without duplicate rsync rules."""
    return tuple(dict.fromkeys(item for group in groups for item in group))


def mount_action(
    *,
    target_identity: str,
    expected_identity: str,
    other_targets: Sequence[Path],
) -> str:
    """Plan an idempotent target mount without silently taking ownership."""
    if target_identity:
        if target_identity == expected_identity:
            return "reuse"
        raise RuntimeError("mountpoint is occupied by an unexpected device")
    if other_targets:
        rendered = ", ".join(map(str, other_targets))
        raise RuntimeError(f"expected device is already mounted at {rendered}")
    return "mount"


def mount_device(
    device: Path,
    target: Path,
    *,
    verbosity: str = "quiet",
) -> MountLease:
    """Mount the expected device or safely reuse an existing correct mount."""
    target.mkdir(parents=True, exist_ok=True)
    expected_identity = device_identity(device)
    target_identity = mounted_identity(target)
    other_targets = [
        path for path in mounted_targets(expected_identity) if path != target
    ]
    try:
        action = mount_action(
            target_identity=target_identity,
            expected_identity=expected_identity,
            other_targets=other_targets,
        )
    except RuntimeError as exc:
        raise RuntimeError(f"{target}: {exc}") from exc
    if action == "reuse":
        progress_log(verbosity, f"reusing {device} mounted at {target}")
        return MountLease(device=device, target=target, created=False)

    progress_log(verbosity, f"mounting {device} at {target}")
    run_command(["mount", device, target])
    if mounted_identity(target) != expected_identity:
        with suppress(subprocess.CalledProcessError):
            unmount(target)
        raise RuntimeError(f"{target} was not mounted from expected device {device}")
    return MountLease(device=device, target=target, created=True)


def unmount(target: Path) -> None:
    run_command(["umount", target])


def mount_source_view(
    target: Path,
    *,
    verbosity: str = "quiet",
) -> MountLease:
    """Create a read-only non-recursive bind view that omits nested mounts."""
    target.mkdir(parents=True, exist_ok=True)
    if mounted_source(target):
        raise RuntimeError(f"source-view mountpoint already in use: {target}")
    progress_log(verbosity, f"creating read-only root view at {target}")
    run_command(["mount", "--bind", "/", target])
    try:
        run_command(["mount", "-o", "remount,bind,ro", target])
    except Exception:
        with suppress(subprocess.CalledProcessError):
            unmount(target)
        raise
    return MountLease(device=Path("/"), target=target, created=True)


def rsync_args(
    source: Path,
    destination: Path,
    *,
    excludes: Iterable[str] = (),
    link_dest: Path | None = None,
    verbosity: str = "quiet",
) -> list[str]:
    """Build the common metadata-preserving rsync invocation."""
    args = [
        "rsync",
        "-aHAX",
        "--numeric-ids",
        "--one-file-system",
        "--delete",
        "--delete-delay",
    ]
    if verbosity != "quiet":
        args.extend(
            [
                "--human-readable",
                "--info=progress2,stats2",
            ]
        )
        if verbosity == "noisy":
            args.append("--itemize-changes")
    else:
        args.append("--info=stats2")
    for pattern in excludes:
        args.extend(["--exclude", pattern])
    if link_dest is not None:
        args.extend(["--link-dest", link_dest])
    args.extend([f"{source}/", f"{destination}/"])
    return args


def run_rsync(args: Sequence[str], *, context: str) -> str | None:
    """Run rsync, tolerating only live-source files that vanished."""
    completed = run_command(args, check=False)
    if completed.returncode == 0:
        return None
    if completed.returncode == 24:
        return f"{context}: source files vanished during capture"
    raise subprocess.CalledProcessError(completed.returncode, list(args))


def rsync_compare_args(
    source: Path,
    destination: Path,
    *,
    excludes: Iterable[str] = (),
) -> list[str]:
    """Build a dry-run comparison that emits only detected differences."""
    args = [
        "rsync",
        "-aHAXn",
        "--numeric-ids",
        "--one-file-system",
        "--delete",
        "--itemize-changes",
    ]
    for pattern in excludes:
        args.extend(["--exclude", pattern])
    args.extend([f"{source}/", f"{destination}/"])
    return args


def boot_mirror_rsync_args(
    source: Path,
    destination: Path,
    *,
    dry_run: bool = False,
    verbosity: str = "quiet",
) -> list[str]:
    """Build a FAT-compatible boot mirror copy or comparison."""
    args = [
        "rsync",
        "-rtn" if dry_run else "-rt",
        "--delete",
        "--delete-delay",
        "--modify-window=1",
    ]
    if dry_run:
        args.append("--itemize-changes")
    elif verbosity != "quiet":
        args.extend(
            [
                "--human-readable",
                "--info=progress2,stats2",
            ]
        )
        if verbosity == "noisy":
            args.append("--itemize-changes")
    else:
        args.append("--info=stats2")
    args.extend([f"{source}/", f"{destination}/"])
    return args


def snapshot_names(paths: Iterable[Path]) -> list[str]:
    """Return completed snapshot directory names in chronological order."""
    valid = [
        path.name
        for path in paths
        if path.is_dir()
        and not path.name.endswith(".partial")
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{6}", path.name)
    ]
    return sorted(valid)


def retention_deletions(names: Sequence[str], keep: int) -> list[str]:
    """Select only snapshots older than the newest retention window."""
    return list(names[: max(0, len(names) - keep)])


def remove_partial_snapshots(snapshots_dir: Path) -> None:
    """Remove incomplete snapshots left by interruption or failed transfer."""
    if not snapshots_dir.exists():
        return
    for path in snapshots_dir.iterdir():
        if path.is_dir() and path.name.endswith(".partial"):
            shutil.rmtree(path)


def verify_staged_snapshot(snapshot: Path) -> None:
    """Validate a captured snapshot before it enters the canonical chain."""
    for required in (
        snapshot / "root" / "etc" / "fstab",
        snapshot / "root" / "etc" / "debian_version",
        snapshot / "boot-firmware" / "config.txt",
        snapshot / "boot-firmware" / "cmdline.txt",
    ):
        if not required.exists():
            raise RuntimeError(f"required snapshot path missing: {required}")

    modules = snapshot / "root" / "lib" / "modules" / os.uname().release
    if not modules.is_dir():
        raise RuntimeError(f"current kernel modules missing from snapshot: {modules}")


def create_snapshot(
    config: Config,
    now: dt.datetime,
    source_root: Path,
    root_excludes: Iterable[str],
    *,
    verbosity: str = "quiet",
) -> tuple[Path, list[str]]:
    """Create an atomic linked snapshot of root and boot filesystems."""
    config.snapshots_dir.mkdir(parents=True, exist_ok=True)
    remove_partial_snapshots(config.snapshots_dir)
    names = snapshot_names(config.snapshots_dir.iterdir())
    previous = config.snapshots_dir / names[-1] if names else None
    name = now.strftime("%Y-%m-%dT%H%M%S")
    partial = config.snapshots_dir / f"{name}.partial"
    final = config.snapshots_dir / name
    partial.mkdir()

    warnings: list[str] = []
    try:
        root_link = previous / "root" if previous else None
        root_args = rsync_args(
            source_root,
            partial / "root",
            excludes=root_excludes,
            link_dest=root_link,
            verbosity=verbosity,
        )
        for pass_number in (1, 2):
            progress_log(verbosity, f"root capture pass {pass_number}/2")
            warning = run_rsync(
                root_args,
                context=f"root pass {pass_number}",
            )
            if warning:
                warnings.append(warning)

        boot_link = previous / "boot-firmware" if previous else None
        boot_args = rsync_args(
            Path("/boot/firmware"),
            partial / "boot-firmware",
            link_dest=boot_link,
            verbosity=verbosity,
        )
        for pass_number in (1, 2):
            progress_log(verbosity, f"boot capture pass {pass_number}/2")
            warning = run_rsync(
                boot_args,
                context=f"boot pass {pass_number}",
            )
            if warning:
                warnings.append(warning)

        verify_staged_snapshot(partial)
        partial.rename(final)
    except Exception:
        shutil.rmtree(partial, ignore_errors=True)
        raise
    return final, warnings


def prune_snapshots(config: Config) -> None:
    """Apply retention only after the new snapshot and mirror are verified."""
    names = snapshot_names(config.snapshots_dir.iterdir())
    for old_name in retention_deletions(names, config.retention):
        shutil.rmtree(config.snapshots_dir / old_name)


def replace_root_argument(cmdline: str, root_uuid: str) -> str:
    """Render cmdline.txt with exactly one target-root UUID."""
    tokens = cmdline.strip().split()
    root_token = f"root=UUID={root_uuid}"
    replaced = False
    rendered: list[str] = []
    for token in tokens:
        if token.startswith("root="):
            if not replaced:
                rendered.append(root_token)
                replaced = True
            continue
        rendered.append(token)
    if not replaced:
        rendered.append(root_token)
    return " ".join(rendered) + "\n"


def render_fstab(boot_uuid: str, root_uuid: str) -> str:
    """Render the minimal fstab required by the bootable mirror."""
    return (
        "proc /proc proc defaults 0 0\n"
        f"UUID={boot_uuid} /boot/firmware vfat defaults 0 2\n"
        f"UUID={root_uuid} / ext4 defaults,noatime 0 1\n"
    )


def filesystem_uuid(device: Path) -> str:
    return command_output(["blkid", "-s", "UUID", "-o", "value", device])


def atomic_write(path: Path, content: str) -> None:
    """Replace a file without modifying any snapshot hard-linked to the old inode."""
    temporary = path.with_name(f".{path.name}.pi-backup.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.chmod(path.stat().st_mode)
    temporary.replace(path)


def refresh_mirror(
    config: Config,
    devices: Device,
    snapshot: Path,
    *,
    verbosity: str = "quiet",
) -> None:
    """Refresh the bootable mirror strictly from the completed snapshot."""
    write_mirror_state(config, status="updating", snapshot=snapshot)
    run_command(
        rsync_args(
            snapshot / "root",
            config.root_mount,
            excludes=ROOT_EXCLUDES,
            link_dest=snapshot / "root",
            verbosity=verbosity,
        )
    )
    run_command(
        boot_mirror_rsync_args(
            snapshot / "boot-firmware",
            config.boot_mount,
            verbosity=verbosity,
        )
    )

    boot_uuid = filesystem_uuid(devices.boot)
    root_uuid = filesystem_uuid(devices.root)
    target_fstab = config.root_mount / "etc" / "fstab"
    atomic_write(target_fstab, render_fstab(boot_uuid, root_uuid))

    target_cmdline = config.boot_mount / "cmdline.txt"
    atomic_write(
        target_cmdline,
        replace_root_argument(target_cmdline.read_text(encoding="utf-8"), root_uuid),
    )


def write_mirror_state(config: Config, *, status: str, snapshot: Path) -> None:
    """Record whether the bootable mirror is being updated or verified."""
    path = config.root_mount / "backup" / "mirror-state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    payload = {
        "status": status,
        "snapshot": snapshot.name,
        "updated": dt.datetime.now().astimezone().isoformat(),
    }
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_state(
    config: Config,
    *,
    status: str,
    started: dt.datetime,
    finished: dt.datetime,
    snapshot: Path | None = None,
    phase: str = "",
    message: str = "",
    warnings: Sequence[str] = (),
) -> None:
    config.state_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": status,
        "started": started.isoformat(),
        "finished": finished.isoformat(),
        "snapshot": snapshot.name if snapshot else "",
        "phase": phase,
        "message": message,
        "warnings": list(warnings),
    }
    temporary = config.state_dir / "last-run.json.tmp"
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(config.state_dir / "last-run.json")
    if status == "success":
        shutil.copy2(
            config.state_dir / "last-run.json",
            config.state_dir / "last-success.json",
        )


def verify_mirror(config: Config, devices: Device, snapshot: Path) -> None:
    """Fail unless the bootable mirror matches the canonical snapshot."""
    expected_mounts = {
        str(config.boot_mount): str(devices.boot),
        str(config.root_mount): str(devices.root),
    }
    for target, expected_source in expected_mounts.items():
        source = mounted_source(Path(target))
        if Path(source).resolve() != Path(expected_source).resolve():
            raise RuntimeError(f"{target} is mounted from unexpected source {source}")

    for required in (
        config.boot_mount / "config.txt",
        config.boot_mount / "cmdline.txt",
        config.root_mount / "etc" / "fstab",
    ):
        if not required.exists():
            raise RuntimeError(f"required backup path missing: {required}")

    root_uuid = filesystem_uuid(devices.root)
    cmdline = (config.boot_mount / "cmdline.txt").read_text(encoding="utf-8")
    if f"root=UUID={root_uuid}" not in cmdline:
        raise RuntimeError("target cmdline.txt does not reference target root UUID")

    mirror_probe = config.root_mount / "etc" / "debian_version"
    snapshot_probe = snapshot / "root" / "etc" / "debian_version"
    if not mirror_probe.samefile(snapshot_probe):
        raise RuntimeError("bootable mirror is not hard-linked to the current snapshot")

    root_compare = run_command(
        rsync_compare_args(
            snapshot / "root",
            config.root_mount,
            excludes=(*ROOT_EXCLUDES, "/etc/fstab"),
        ),
        capture=True,
    )
    if root_compare.stdout.strip():
        raise RuntimeError("bootable root mirror differs from completed snapshot")

    boot_compare = run_command(
        boot_mirror_rsync_args(
            snapshot / "boot-firmware",
            config.boot_mount,
            dry_run=True,
        ),
        capture=True,
    )
    boot_differences = [
        line
        for line in boot_compare.stdout.splitlines()
        if not line.rstrip().endswith(" cmdline.txt")
    ]
    if boot_differences:
        raise RuntimeError("boot mirror differs from completed snapshot")

    free_bytes = shutil.disk_usage(config.root_mount).free
    if free_bytes < 10 * 1024**3:
        raise RuntimeError("less than 10 GiB remains on backup root")


def write_probe(path: Path) -> None:
    """Prove a mounted target is writable before beginning a long transfer."""
    probe = path / ".pi-backup-write-probe"
    try:
        probe.write_text("probe\n", encoding="ascii")
        with probe.open("rb") as handle:
            os.fsync(handle.fileno())
    finally:
        probe.unlink(missing_ok=True)


def verify_capacity(config: Config, source_root: Path) -> None:
    """Require recovery headroom and enough space for an initial full snapshot."""
    reserve = 10 * 1024**3
    completed = (
        snapshot_names(config.snapshots_dir.iterdir())
        if config.snapshots_dir.exists()
        else []
    )
    required = reserve
    if not completed:
        required += shutil.disk_usage(source_root).used
    available = shutil.disk_usage(config.root_mount).free
    if available < required:
        raise RuntimeError(
            f"insufficient backup space: need {required} bytes, have {available}"
        )


def offline_boot_check(devices: Device) -> None:
    """Check FAT metadata only when the device is no longer mounted."""
    identity = device_identity(devices.boot)
    targets = mounted_targets(identity)
    if targets:
        print(
            "pi-backup: skipping offline boot check; device remains mounted at "
            + ", ".join(map(str, targets)),
            file=sys.stderr,
        )
        return
    run_command(["fsck.vfat", "-n", devices.boot])


def install_signal_handlers() -> None:
    """Turn normal service termination into a cleanup-aware exception."""

    def interrupt(signum: int, _frame: object) -> None:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        raise BackupInterrupted(f"received {signal.Signals(signum).name}")

    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)


def run_backup(config: Config, *, verbosity: str = "quiet") -> None:
    """Run snapshot, mirror, validation, state recording, sync, and unmount."""
    started = dt.datetime.now().astimezone()
    install_signal_handlers()
    devices: Device | None = None
    snapshot: Path | None = None
    warnings: list[str] = []
    leases: list[MountLease] = []
    failure: Exception | None = None
    interrupted = False
    phase = "resolve-devices"
    progress_log(verbosity, f"starting backup at {started.isoformat()}")
    progress_log(verbosity, f"phase: {phase}")
    write_state(
        config,
        status="running",
        started=started,
        finished=started,
        phase=phase,
    )
    try:
        devices = resolve_devices(config)
        phase = "mount-targets"
        progress_log(
            verbosity,
            f"target disk {devices.disk}: boot={devices.boot}, root={devices.root}",
        )
        progress_log(verbosity, f"phase: {phase}")
        write_state(
            config,
            status="running",
            started=started,
            finished=dt.datetime.now().astimezone(),
            phase=phase,
        )
        leases.append(
            mount_device(devices.root, config.root_mount, verbosity=verbosity)
        )
        leases.append(
            mount_device(devices.boot, config.boot_mount, verbosity=verbosity)
        )
        leases.append(
            mount_source_view(DEFAULT_SOURCE_ROOT, verbosity=verbosity)
        )
        write_probe(config.root_mount)
        write_probe(config.boot_mount)
        verify_capacity(config, DEFAULT_SOURCE_ROOT)
        root_excludes = merged_excludes(ROOT_EXCLUDES, nested_mount_excludes())
        if verbosity == "noisy":
            print("pi-backup: root exclusions:", flush=True)
            for pattern in root_excludes:
                print(f"  {pattern}", flush=True)

        phase = "create-snapshot"
        progress_log(verbosity, f"phase: {phase}")
        write_state(
            config,
            status="running",
            started=started,
            finished=dt.datetime.now().astimezone(),
            phase=phase,
        )
        snapshot, capture_warnings = create_snapshot(
            config,
            started,
            DEFAULT_SOURCE_ROOT,
            root_excludes,
            verbosity=verbosity,
        )
        warnings.extend(capture_warnings)
        phase = "refresh-mirror"
        progress_log(verbosity, f"canonical snapshot: {snapshot.name}")
        progress_log(verbosity, f"phase: {phase}")
        refresh_mirror(config, devices, snapshot, verbosity=verbosity)
        phase = "verify"
        progress_log(verbosity, f"phase: {phase}")
        run_command(["sync"])
        verify_mirror(config, devices, snapshot)
        write_mirror_state(config, status="verified", snapshot=snapshot)
        phase = "retention"
        progress_log(verbosity, f"phase: {phase}")
        prune_snapshots(config)
    except Exception as exc:
        failure = exc
        interrupted = isinstance(exc, BackupInterrupted)
    finally:
        run_command(["sync"], check=False)
        cleanup_errors: list[str] = []
        for lease in reversed(leases):
            if not lease.created:
                continue
            try:
                progress_log(verbosity, f"unmounting {lease.target}")
                unmount(lease.target)
            except subprocess.CalledProcessError as exc:
                cleanup_errors.append(f"failed to unmount {lease.target}: {exc}")
        if cleanup_errors:
            cleanup_message = "; ".join(cleanup_errors)
            failure = RuntimeError(
                f"{failure}; {cleanup_message}" if failure else cleanup_message
            )

    if failure is None and devices is not None:
        phase = "offline-check"
        progress_log(verbosity, f"phase: {phase}")
        try:
            offline_boot_check(devices)
        except Exception as exc:
            failure = exc

    if failure is not None:
        status_value = "interrupted" if interrupted else "failed"
        write_state(
            config,
            status=status_value,
            started=started,
            finished=dt.datetime.now().astimezone(),
            snapshot=snapshot,
            phase=phase,
            message=str(failure),
            warnings=warnings,
        )
        progress_log(verbosity, f"backup failed during {phase}: {failure}")
        raise failure

    for warning in warnings:
        progress_log(verbosity, f"warning: {warning}")
    progress_log(verbosity, "backup completed successfully")
    write_state(
        config,
        status="success",
        started=started,
        finished=dt.datetime.now().astimezone(),
        snapshot=snapshot,
        phase="complete",
        warnings=warnings,
    )


def status(config: Config) -> int:
    """Print the latest state and fail unless the latest run succeeded."""
    state_path = config.state_dir / "last-run.json"
    if not state_path.exists():
        print("No backup run has been recorded.")
        return 1
    content = state_path.read_text(encoding="utf-8")
    print(content, end="")
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return 1
    return 0 if payload.get("status") == "success" else 1


def locked(action: Callable[[], object]) -> None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        action()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--progress",
        action="store_true",
        help="print phase changes plus aggregate rsync progress and statistics",
    )
    verbosity.add_argument(
        "-v",
        "--noisy",
        action="store_true",
        help="print phase changes, changed files, and aggregate rsync progress",
    )
    parser.add_argument(
        "command",
        choices=("prepare", "run", "status"),
        help="prepare erases/layouts the disk; run performs the complete backup",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config()
    if args.command == "status":
        return status(config)

    require_root()
    verbosity = "noisy" if args.noisy else "progress" if args.progress else "quiet"
    action = (
        (lambda: prepare_drive(config))
        if args.command == "prepare"
        else (lambda: run_backup(config, verbosity=verbosity))
    )
    locked(action)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"pi-backup: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
