#!/usr/bin/env python3
"""Destructively provision the dedicated Raspberry Pi backup drive."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shlex
import subprocess
import sys
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG = Path("/etc/pi-backup.conf")
LOCK_PATH = Path("/run/lock/pi-backup.lock")
MINIMUM_SIZE = 16 * 1024**3


@dataclass(frozen=True)
class Config:
    disk_serial: str
    boot_label: str
    root_label: str


@dataclass(frozen=True)
class Disk:
    path: Path
    transport: str
    removable: bool
    size: int
    mounted_at: tuple[str, ...]


def run_command(
    args: Sequence[object],
    *,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    rendered = list(map(str, args))
    print("+", " ".join(rendered), flush=True)
    return subprocess.run(
        rendered,
        check=check,
        text=True,
        capture_output=capture,
    )


def command_output(args: Sequence[object]) -> str:
    return run_command(args, capture=True).stdout.strip()


def require_root() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("must run as root")


@contextmanager
def backup_lock() -> Iterator[None]:
    """Serialize provisioning with backup runs."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("backup or provisioning is already running") from exc
        yield


def parse_environment_file(path: Path) -> dict[str, str]:
    """Parse the supported KEY=VALUE subset of a systemd EnvironmentFile."""
    values: dict[str, str] = {}
    for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise RuntimeError(f"{path}:{number}: expected KEY=VALUE")
        key, raw_value = line.split("=", 1)
        tokens = shlex.split(raw_value, comments=True)
        if len(tokens) > 1:
            raise RuntimeError(f"{path}:{number}: invalid value")
        values[key.strip()] = tokens[0] if tokens else ""
    return values


def load_config(path: Path) -> Config:
    values = parse_environment_file(path)
    required = (
        "PI_BACKUP_DISK_SERIAL",
        "PI_BACKUP_BOOT_LABEL",
        "PI_BACKUP_ROOT_LABEL",
    )
    missing = [name for name in required if not values.get(name, "").strip()]
    if missing:
        raise RuntimeError(f"{', '.join(missing)} required in {path}")
    return Config(
        disk_serial=values["PI_BACKUP_DISK_SERIAL"].strip(),
        boot_label=values["PI_BACKUP_BOOT_LABEL"].strip(),
        root_label=values["PI_BACKUP_ROOT_LABEL"].strip(),
    )


def parse_target(payload: str, serial: str) -> Disk:
    devices = json.loads(payload)["blockdevices"]
    matches = [
        device
        for device in devices
        if device.get("type") == "disk"
        and (device.get("serial") or "").strip() == serial
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one disk with serial {serial!r}; found {len(matches)}"
        )

    device = matches[0]
    mounted_at = tuple(
        mountpoint
        for node in (device, *(device.get("children") or []))
        for mountpoint in (node.get("mountpoints") or [])
        if mountpoint
    )
    return Disk(
        path=Path(device["path"]),
        transport=(device.get("tran") or "").strip(),
        removable=bool(device.get("rm")),
        size=int(device.get("size") or 0),
        mounted_at=mounted_at,
    )


def resolve_target(serial: str) -> Disk:
    payload = command_output(
        [
            "lsblk",
            "--json",
            "--bytes",
            "--paths",
            "--output",
            "PATH,TYPE,SERIAL,TRAN,RM,SIZE,MOUNTPOINTS",
        ]
    )
    target = parse_target(payload, serial)
    if target.path.name.startswith("nvme"):
        raise RuntimeError(f"refusing to repartition NVMe device {target.path}")
    if target.transport != "usb":
        raise RuntimeError(
            f"refusing non-USB target {target.path}: "
            f"transport={target.transport or 'unknown'}"
        )
    if not target.removable:
        raise RuntimeError(f"refusing non-removable target {target.path}")
    if target.size < MINIMUM_SIZE:
        raise RuntimeError(f"refusing target smaller than 16 GiB: {target.path}")
    if target.mounted_at:
        raise RuntimeError(
            f"refusing mounted target {target.path}: "
            + ", ".join(target.mounted_at)
        )
    return target


def partitions_for(disk: Path) -> tuple[Path, Path]:
    lines = command_output(["lsblk", "-nrpo", "PATH,TYPE", disk]).splitlines()
    partitions = [
        Path(fields[0])
        for line in lines
        if len(fields := line.split()) == 2 and fields[1] == "part"
    ]
    if len(partitions) != 2:
        raise RuntimeError(
            f"expected two partitions on {disk}; found {len(partitions)}"
        )
    return partitions[0], partitions[1]


def provision(config: Config, confirmation: str) -> None:
    if confirmation != config.disk_serial:
        raise RuntimeError("--confirm-erase must exactly match the configured serial")

    disk = resolve_target(config.disk_serial).path
    run_command(["wipefs", "--all", disk])
    run_command(["parted", "--script", disk, "mklabel", "gpt"])
    run_command(
        ["parted", "--script", disk, "mkpart", "boot", "fat32", "1MiB", "1025MiB"]
    )
    run_command(["parted", "--script", disk, "set", "1", "boot", "on"])
    run_command(
        ["parted", "--script", disk, "mkpart", "root", "ext4", "1025MiB", "100%"]
    )
    run_command(["partprobe", disk])
    run_command(["udevadm", "settle"])

    boot, root = partitions_for(disk)
    run_command(["mkfs.vfat", "-F", "32", "-n", config.boot_label, boot])
    run_command(["mkfs.ext4", "-F", "-m", "0", "-L", config.root_label, root])
    checked = run_command(["e2fsck", "-f", "-p", root], check=False)
    if checked.returncode not in (0, 1, 2):
        raise RuntimeError(f"e2fsck failed with status {checked.returncode}")
    run_command(["udevadm", "settle"])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"backup environment file (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument("--confirm-erase", required=True, metavar="SERIAL")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require_root()
    with backup_lock():
        provision(load_config(args.config), args.confirm_erase)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"pi-prepare-backup-drive: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
