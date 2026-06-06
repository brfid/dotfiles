#!/usr/bin/env python3
"""Maintain one removable drive as a directly bootable system mirror."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import signal
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


DEFAULT_STATE_DIR = Path("/var/lib/pi-backup")
DEFAULT_MOUNT_ROOT = Path("/mnt/pi-backup")
DEFAULT_SOURCE_ROOT = Path("/run/pi-backup/source")
LOCK_PATH = Path("/run/lock/pi-backup.lock")
RESERVE_BYTES = 10 * 1024**3
DPKG_LOCK_PATHS = (
    Path("/var/lib/dpkg/lock-frontend"),
    Path("/var/lib/dpkg/lock"),
)

MIRROR_EXCLUDES = (
    "/backup/***",
    "/boot/firmware/***",
    "/dev/***",
    "/etc/fstab",
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
    "/home/*/.bun/install/cache/***",
    "/home/*/.cargo/registry/cache/***",
    "/home/*/.npm/_cacache/***",
    "/home/*/.npm/_npx/***",
    "/home/*/src/**/.venv/***",
    "/home/*/src/**/node_modules/***",
    "/home/*/src/**/target/***",
)

RUNTIME_DIRECTORIES = (
    "boot/firmware",
    "dev",
    "media",
    "mnt",
    "proc",
    "run",
    "sys",
    "tmp",
)

Verbosity = Literal["quiet", "progress", "noisy"]


@dataclass(frozen=True)
class Config:
    disk_serial: str
    boot_label: str
    root_label: str
    state_dir: Path = DEFAULT_STATE_DIR
    mount_root: Path = DEFAULT_MOUNT_ROOT

    @property
    def boot_mount(self) -> Path:
        return self.mount_root / "boot"

    @property
    def root_mount(self) -> Path:
        return self.mount_root / "root"


@dataclass(frozen=True)
class Device:
    disk: Path
    boot: Path
    root: Path


@dataclass(frozen=True)
class TargetConfig:
    fstab: str
    cmdline: str


@dataclass
class RunContext:
    config: Config
    started: dt.datetime
    verbosity: Verbosity
    phase: str = ""
    warnings: list[str] = field(default_factory=list)
    mounts: list[Path] = field(default_factory=list)

    def begin(self, phase: str) -> None:
        self.phase = phase
        progress_log(self.verbosity, f"phase: {phase}")
        write_state(
            self.config,
            status="running",
            started=self.started,
            finished=dt.datetime.now().astimezone(),
            phase=phase,
            warnings=self.warnings,
        )


class BackupInterrupted(RuntimeError):
    pass


def run_command(
    args: Sequence[object],
    *,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Terminate the child process group when this process is interrupted."""
    rendered = list(map(str, args))
    process = subprocess.Popen(
        rendered,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate()
    except BaseException:
        with suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        raise

    completed = subprocess.CompletedProcess(
        rendered,
        process.returncode,
        stdout or "",
        stderr or "",
    )
    if check and completed.returncode:
        raise subprocess.CalledProcessError(
            completed.returncode,
            rendered,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed


def command_output(args: Sequence[object]) -> str:
    return run_command(args, capture=True).stdout.strip()


def progress_log(verbosity: Verbosity, message: str) -> None:
    if verbosity != "quiet":
        print(f"pi-backup: {message}", flush=True)


def require_root() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("must run as root")


def load_config() -> Config:
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
    return Config(
        disk_serial=required["PI_BACKUP_DISK_SERIAL"],
        boot_label=required["PI_BACKUP_BOOT_LABEL"],
        root_label=required["PI_BACKUP_ROOT_LABEL"],
        state_dir=Path(os.environ.get("PI_BACKUP_STATE_DIR", DEFAULT_STATE_DIR)),
        mount_root=Path(os.environ.get("PI_BACKUP_MOUNT_ROOT", DEFAULT_MOUNT_ROOT)),
    )


def parse_lsblk(payload: str, serial: str) -> Path:
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
    disk = find_disk(config.disk_serial)
    boot = device_for_label(config.boot_label)
    root = device_for_label(config.root_label)
    if parent_disk(boot) != disk or parent_disk(root) != disk:
        raise RuntimeError("backup labels do not belong to the configured disk")
    return Device(disk=disk, boot=boot, root=root)


def mounted_source(target: Path) -> str:
    completed = run_command(
        ["findmnt", "-nro", "SOURCE", "--mountpoint", target],
        capture=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def mounted_identity(target: Path) -> str:
    completed = run_command(
        ["findmnt", "-nro", "MAJ:MIN", "--mountpoint", target],
        capture=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def device_identity(device: Path) -> str:
    identity = command_output(["lsblk", "-dnro", "MAJ:MIN", device])
    if not identity:
        raise RuntimeError(f"cannot resolve device identity for {device}")
    return identity


def mounted_targets(identity: str) -> list[Path]:
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
    payload = command_output(["findmnt", "--json", "--output", "TARGET"])
    patterns = {
        f"{target}/***"
        for target in parse_mount_targets(payload)
        if target != Path("/")
    }
    return tuple(sorted(patterns))


def merged_excludes(*groups: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def mount_device(
    device: Path,
    target: Path,
    *,
    verbosity: Verbosity = "quiet",
) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    expected_identity = device_identity(device)
    if mounted_identity(target):
        raise RuntimeError(f"backup mountpoint already in use: {target}")
    existing_targets = mounted_targets(expected_identity)
    if existing_targets:
        rendered = ", ".join(map(str, existing_targets))
        raise RuntimeError(f"{device} is already mounted at {rendered}")

    progress_log(verbosity, f"mounting {device} at {target}")
    run_command(["mount", device, target])
    if mounted_identity(target) != expected_identity:
        with suppress(subprocess.CalledProcessError):
            unmount(target)
        raise RuntimeError(f"{target} was not mounted from expected device {device}")
    return target


def mount_source_view(
    target: Path,
    *,
    verbosity: Verbosity = "quiet",
) -> Path:
    """Expose `/` without recursively including its mounted subtrees."""
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
    return target


def unmount(target: Path) -> None:
    run_command(["umount", target])


def rsync_args(
    source: Path,
    destination: Path,
    *,
    excludes: Iterable[str] = (),
    verbosity: Verbosity = "quiet",
) -> list[str]:
    args = [
        "rsync",
        "-aHAXS",
        "--numeric-ids",
        "--one-file-system",
        "--delete",
        "--delete-delay",
        "--delete-excluded",
        "--filter",
        "protect /lost+found",
        "--filter",
        "protect /etc/fstab",
    ]
    args.extend(rsync_display_args(verbosity))
    for pattern in excludes:
        args.extend(["--exclude", pattern])
    args.extend([f"{source}/", f"{destination}/"])
    return args


def boot_rsync_args(
    source: Path,
    destination: Path,
    *,
    verbosity: Verbosity = "quiet",
) -> list[str]:
    args = [
        "rsync",
        "-rt",
        "--delete",
        "--delete-delay",
        "--modify-window=1",
        "--filter",
        "protect /cmdline.txt",
        "--exclude",
        "/cmdline.txt",
    ]
    args.extend(rsync_display_args(verbosity))
    args.extend([f"{source}/", f"{destination}/"])
    return args


def rsync_display_args(verbosity: Verbosity) -> list[str]:
    if verbosity == "quiet":
        return ["--info=stats2"]
    args = ["--human-readable", "--info=progress2,stats2"]
    if verbosity == "noisy":
        args.append("--itemize-changes")
    return args


def run_rsync(args: Sequence[str], *, context: str) -> str | None:
    completed = run_command(args, check=False)
    if completed.returncode == 0:
        return None
    if completed.returncode == 24:
        return f"{context}: source files vanished during capture"
    raise RuntimeError(f"{context} failed with rsync status {completed.returncode}")


@contextmanager
def package_database_lock(
    paths: Sequence[Path] = DPKG_LOCK_PATHS,
) -> Iterator[None]:
    """Fail rather than copy across a concurrent package installation."""
    handles = []
    try:
        for path in paths:
            handle = path.open("a+", encoding="utf-8")
            try:
                fcntl.lockf(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                handle.close()
                raise RuntimeError(
                    f"package manager is active; cannot lock {path}"
                ) from exc
            handles.append(handle)
        yield
    finally:
        for handle in reversed(handles):
            with suppress(OSError):
                fcntl.lockf(handle, fcntl.LOCK_UN)
            handle.close()


def replace_root_argument(cmdline: str, root_uuid: str) -> str:
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
    return (
        "proc /proc proc defaults 0 0\n"
        f"UUID={boot_uuid} /boot/firmware vfat defaults 0 2\n"
        f"UUID={root_uuid} / ext4 defaults,noatime 0 1\n"
    )


def filesystem_uuid(device: Path) -> str:
    return command_output(["blkid", "-s", "UUID", "-o", "value", device])


def expected_target_config(devices: Device) -> TargetConfig:
    boot_uuid = filesystem_uuid(devices.boot)
    root_uuid = filesystem_uuid(devices.root)
    source_cmdline = Path("/boot/firmware/cmdline.txt").read_text(encoding="utf-8")
    return TargetConfig(
        fstab=render_fstab(boot_uuid, root_uuid),
        cmdline=replace_root_argument(source_cmdline, root_uuid),
    )


def atomic_write(path: Path, content: str) -> None:
    """Replace a file only after its contents and parent entry are durable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.stat() if path.exists() else None
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    handle = None
    try:
        handle = os.fdopen(descriptor, "w", encoding="utf-8")
        with handle:
            temporary_stat = os.fstat(handle.fileno())
            if existing is not None:
                existing_mode = stat.S_IMODE(existing.st_mode)
                if stat.S_IMODE(temporary_stat.st_mode) != existing_mode:
                    os.fchmod(handle.fileno(), existing_mode)
                if (
                    temporary_stat.st_uid != existing.st_uid
                    or temporary_stat.st_gid != existing.st_gid
                ):
                    os.fchown(handle.fileno(), existing.st_uid, existing.st_gid)
            else:
                os.fchmod(handle.fileno(), 0o644)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
        fsync_directory(path.parent)
    except Exception:
        if handle is None:
            os.close(descriptor)
        elif not handle.closed:
            handle.close()
        temporary.unlink(missing_ok=True)
        raise


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def copy_directory_metadata(source: Path, destination: Path) -> None:
    source_stat = source.stat()
    destination.mkdir(parents=True, exist_ok=True)
    os.chown(destination, source_stat.st_uid, source_stat.st_gid)
    os.chmod(destination, stat.S_IMODE(source_stat.st_mode))


def ensure_runtime_directories(source_root: Path, target_root: Path) -> None:
    for relative in RUNTIME_DIRECTORIES:
        copy_directory_metadata(source_root / relative, target_root / relative)


def write_target_config(config: Config, devices: Device) -> TargetConfig:
    generated = expected_target_config(devices)
    atomic_write(config.root_mount / "etc" / "fstab", generated.fstab)
    atomic_write(config.boot_mount / "cmdline.txt", generated.cmdline)
    return generated


def verify_mirror(
    config: Config,
    devices: Device,
    generated: TargetConfig,
) -> None:
    expected_mounts = {
        config.boot_mount: devices.boot,
        config.root_mount: devices.root,
    }
    for target, expected_source in expected_mounts.items():
        source = mounted_source(target)
        if Path(source).resolve() != expected_source.resolve():
            raise RuntimeError(f"{target} is mounted from unexpected source {source}")

    required = (
        config.boot_mount / "config.txt",
        config.boot_mount / "cmdline.txt",
        config.root_mount / "etc" / "debian_version",
        config.root_mount / "etc" / "fstab",
        config.root_mount / "lib" / "modules" / os.uname().release,
    )
    for path in required:
        if not path.exists():
            raise RuntimeError(f"required backup path missing: {path}")

    actual_fstab = (config.root_mount / "etc" / "fstab").read_text(
        encoding="utf-8"
    )
    if actual_fstab != generated.fstab:
        raise RuntimeError("target fstab does not match expected backup mounts")

    actual_cmdline = (config.boot_mount / "cmdline.txt").read_text(encoding="utf-8")
    if actual_cmdline != generated.cmdline:
        raise RuntimeError("target cmdline.txt does not match expected root argument")

    legacy_backup = config.root_mount / "backup"
    if legacy_backup.exists():
        raise RuntimeError("legacy snapshot tree remains on bootable mirror")

    if shutil.disk_usage(config.root_mount).free < RESERVE_BYTES:
        raise RuntimeError("less than 10 GiB remains on backup root")


def write_probe(path: Path) -> None:
    descriptor, probe_name = tempfile.mkstemp(
        dir=path,
        prefix=".pi-backup-write-probe.",
    )
    probe = Path(probe_name)
    try:
        os.write(descriptor, b"probe\n")
        os.fsync(descriptor)
    finally:
        try:
            os.close(descriptor)
        finally:
            probe.unlink(missing_ok=True)


def verify_capacity(config: Config, source_root: Path) -> None:
    required = RESERVE_BYTES + shutil.disk_usage(source_root).used
    capacity = shutil.disk_usage(config.root_mount).total
    if capacity < required:
        raise RuntimeError(
            f"insufficient backup capacity: need {required} bytes, have {capacity}"
        )


def write_state(
    config: Config,
    *,
    status: str,
    started: dt.datetime,
    finished: dt.datetime,
    phase: str = "",
    message: str = "",
    warnings: Sequence[str] = (),
) -> None:
    config.state_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": status,
        "started": started.isoformat(),
        "finished": finished.isoformat(),
        "phase": phase,
        "message": message,
        "warnings": list(warnings),
    }
    content = json.dumps(payload, indent=2) + "\n"
    if status == "success":
        atomic_write(config.state_dir / "last-success.json", content)
    atomic_write(config.state_dir / "last-run.json", content)


def install_signal_handlers() -> None:
    def interrupt(signum: int, _frame: object) -> None:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        raise BackupInterrupted(f"received {signal.Signals(signum).name}")

    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)


def perform_backup(context: RunContext) -> None:
    config = context.config
    verbosity = context.verbosity

    context.begin("resolve-devices")
    devices = resolve_devices(config)
    progress_log(
        verbosity,
        f"target disk {devices.disk}: boot={devices.boot}, root={devices.root}",
    )

    context.begin("mount-targets")
    context.mounts.append(
        mount_device(devices.root, config.root_mount, verbosity=verbosity)
    )
    context.mounts.append(
        mount_device(devices.boot, config.boot_mount, verbosity=verbosity)
    )
    context.mounts.append(
        mount_source_view(DEFAULT_SOURCE_ROOT, verbosity=verbosity)
    )
    write_probe(config.root_mount)
    write_probe(config.boot_mount)
    verify_capacity(config, DEFAULT_SOURCE_ROOT)

    excludes = merged_excludes(MIRROR_EXCLUDES, nested_mount_excludes())
    if verbosity == "noisy":
        print("pi-backup: root exclusions:", flush=True)
        for pattern in excludes:
            print(f"  {pattern}", flush=True)

    context.begin("mirror-root")
    warning = run_rsync(
        rsync_args(
            DEFAULT_SOURCE_ROOT,
            config.root_mount,
            excludes=excludes,
            verbosity=verbosity,
        ),
        context="root mirror",
    )
    if warning:
        context.warnings.append(warning)
    ensure_runtime_directories(DEFAULT_SOURCE_ROOT, config.root_mount)

    context.begin("mirror-boot")
    boot_args = boot_rsync_args(
        Path("/boot/firmware"),
        config.boot_mount,
        verbosity=verbosity,
    )
    warning = run_rsync(boot_args, context="boot mirror")
    if warning:
        context.warnings.append(warning)

    generated = write_target_config(config, devices)

    context.begin("verify")
    verify_mirror(config, devices, generated)


def cleanup_mounts(context: RunContext) -> list[str]:
    errors: list[str] = []
    for target in reversed(context.mounts):
        try:
            progress_log(context.verbosity, f"unmounting {target}")
            unmount(target)
        except Exception as exc:
            errors.append(f"failed to unmount {target}: {exc}")
    return errors


def run_backup(config: Config, *, verbosity: Verbosity = "quiet") -> None:
    started = dt.datetime.now().astimezone()
    install_signal_handlers()
    context = RunContext(config=config, started=started, verbosity=verbosity)
    failure: Exception | None = None
    interrupted = False
    progress_log(verbosity, f"starting backup at {started.isoformat()}")
    try:
        context.begin("lock-package-database")
        with package_database_lock():
            perform_backup(context)
    except Exception as exc:
        failure = exc
        interrupted = isinstance(exc, BackupInterrupted)
    finally:
        cleanup_errors = cleanup_mounts(context)
        if cleanup_errors:
            cleanup_message = "; ".join(cleanup_errors)
            failure = RuntimeError(
                f"{failure}; {cleanup_message}" if failure else cleanup_message
            )

    if failure is not None:
        status_value = "interrupted" if interrupted else "failed"
        write_state(
            config,
            status=status_value,
            started=started,
            finished=dt.datetime.now().astimezone(),
            phase=context.phase,
            message=str(failure),
            warnings=context.warnings,
        )
        progress_log(verbosity, f"backup failed during {context.phase}: {failure}")
        raise failure

    for warning in context.warnings:
        progress_log(verbosity, f"warning: {warning}")
    write_state(
        config,
        status="success",
        started=started,
        finished=dt.datetime.now().astimezone(),
        phase="complete",
        warnings=context.warnings,
    )
    progress_log(verbosity, "backup completed successfully")


def status(config: Config) -> int:
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


@contextmanager
def backup_lock() -> Iterator[None]:
    """Serialize backup and destructive provisioning operations."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("backup or provisioning is already running") from exc
        yield


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--progress",
        action="store_true",
        help="print phases and aggregate transfer progress",
    )
    verbosity.add_argument(
        "-v",
        "--noisy",
        action="store_true",
        help="also list changed paths",
    )
    parser.add_argument("command", choices=("run", "status"))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config()
    if args.command == "status":
        return status(config)

    require_root()
    verbosity: Verbosity = (
        "noisy" if args.noisy else "progress" if args.progress else "quiet"
    )
    with backup_lock():
        run_backup(config, verbosity=verbosity)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"pi-backup: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
