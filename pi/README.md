# pi

Role: host config and whole-system backup strategy. See `debian/` for OS-level
preferences.

## Boot order

Prefer NVMe first, USB mass storage second, and microSD third. The corresponding
EEPROM value is `BOOT_ORDER=0xf146`; fields are evaluated right to left.

## CPU policy

Prefer conservative CPU frequency scaling for daily desktop use. Keep the stock
Pi 5 top CPU frequency available for sustained work, but avoid overclocking,
`force_turbo`, or hard max-frequency caps unless there is a specific thermal or
latency reason.

## Backup drive

This section is the canonical design and operating reference. Code contains
only local safety-contract docstrings. Machine-specific identity and live state
belong in the private `pi` and `systemd` restoration notes.

Purpose: maintain one directly bootable USB replacement for the primary drive.
It is an in-place mirror, not versioned or archival storage.

Layout:

- 1 GiB FAT32 boot partition.
- Remaining space as an ext4 root partition.
- Exact disk serial and filesystem labels in `/etc/pi-backup.conf`.

Safety invariants:

- Resolve the disk by serial and prove both labels belong to it.
- Refuse targets already mounted anywhere.
- Serialize backup and provisioning with `/run/lock/pi-backup.lock`.
- Run target mounts in a private mount namespace.
- Hold native dpkg locks during capture.
- Do not traverse nested source mounts.
- Preserve the USB `fstab` and `cmdline.txt` until their atomic replacements
  are ready.
- Record success only after verification and clean unmount.

The root and boot filesystems are each copied once. Root rsync preserves Linux
metadata, hard links, ACLs, xattrs, and sparse files. Exclusions remove virtual
filesystems, other mounts, caches, trash, downloaded packages, `node_modules`,
project `.venv`, and Rust `target` trees. Source, lockfiles, application data,
installed packages and runtimes, editor state, and unpublished build output
remain.

Commands:

```sh
pi-backup
pi-backup status
sudo systemctl enable --now pi-backup.timer
```

`pi-backup` runs interactively with aggregate percentage, rate, and ETA.
Scheduled output is concise. `--noisy` also lists changed paths.

The first interrupt terminates the active child and starts reverse-order
unmounting. A second interrupt uses the OS default termination behavior. The
private mount namespace prevents abandoned mounts after forced termination.
Because the mirror is updated in place, an interrupted run may leave incomplete
files; rerun it before relying on the drive.

`prepare_backup_drive.py` is deliberately separate and destructive. It refuses
NVMe, non-USB, non-removable, undersized, mounted, or serial-mismatched targets.
Run it only with `--confirm-erase SERIAL`.

Dependencies: Python 3, rsync, util-linux, dosfstools, e2fsprogs, parted, and
systemd.

Rebuild:

```sh
cd ~/src/dotfiles/pi
python3 -m unittest -q test_backup_drive.py test_prepare_backup_drive.py
sudo install -o root -g root -m 0755 backup_drive.py \
  /usr/local/sbin/pi-backup-drive
sudo install -o root -g root -m 0755 prepare_backup_drive.py \
  /usr/local/sbin/pi-prepare-backup-drive
sudo install -o root -g root -m 0755 pi-backup /usr/local/bin/pi-backup
sudo install -o root -g root -m 0644 ../systemd/pi-backup.service \
  /etc/systemd/system/pi-backup.service
sudo install -o root -g root -m 0644 ../systemd/pi-backup.timer \
  /etc/systemd/system/pi-backup.timer
sudo systemctl daemon-reload
```

Machine identity remains in the private restoration note and root-owned
environment file.

Limitations:

- The live copy is neither point-in-time nor application-consistent.
- Excluded project dependencies may require network access to rebuild.
- USB fallback does not help if NVMe firmware boot succeeds and Linux fails
  later; disconnect or disable NVMe for recovery.
- This unencrypted attached drive does not cover theft, electrical damage,
  privileged compromise, or media failure. Keep independent archival backups.

After the first successful manual backup, complete the recovery drill below.

## Recovery drill

1. Confirm the latest backup state reports success.
2. Shut down the Pi.
3. Disconnect or disable the NVMe boot device.
4. Boot from the USB backup drive.
5. Verify root and boot mounts, networking, SSH, and critical services.
6. Reconnect the NVMe device and restore the intended boot order.

## Bluetooth

The on-board BCM4345C0 adapter has a firmware bug that causes MAC address
instability across some reboots, which silently orphans the BlueZ pairing
database. See `bluetooth/` for the workaround, backup, and restore strategy.

## Do not store

- Target serials, UUIDs, hostnames, live state files, or logs.
- SSH host keys, Tailscale identity, or rendered EEPROM configuration.
