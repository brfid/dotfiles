# pi

Role: host config and whole-system backup strategy. See `debian/` for OS-level preferences.

## Boot order

Prefer NVMe first and USB mass storage second. Configure this in EEPROM with
`sudo rpi-eeprom-config --edit` after the USB mirror has completed and passed
validation.

## CPU policy

Prefer conservative CPU frequency scaling for daily desktop use. Keep the stock
Pi 5 top CPU frequency available for sustained work, but avoid overclocking,
`force_turbo`, or hard max-frequency caps unless there is a specific thermal or
latency reason.

## Backup drive

Use a dedicated USB drive with:

- A small FAT32 boot partition.
- An ext4 root partition containing both a bootable mirror and linked snapshots.
- Stable filesystem labels and a required USB device serial guard.

The root-owned environment file must explicitly provide the disk serial and
both filesystem labels. The script has no public fallback labels. The default
mount root (`/mnt/pi-backup`) and state directory (`/var/lib/pi-backup`) are
publishable implementation conventions and may be overridden locally.

`backup_drive.py prepare` is destructive and creates the partition layout.
`backup_drive.py run` performs one complete batch:

1. Resolve the target by configured USB serial and partition labels.
2. Safely reuse correct existing mounts or mount both target filesystems in a
   private service namespace.
3. Create a read-only, non-recursive view of the live root so unrelated nested
   mounts are not traversed, and dynamically exclude their underlying
   mountpoint directories.
4. Create an atomic root and boot snapshot with a convergence pass,
   hard-linking unchanged files to the previous snapshot. Tolerate only rsync's
   live-source disappearance status; reject and delete every other partial
   capture.
5. Refresh the bootable mirror strictly from that completed snapshot and
   rewrite only the target `fstab` and kernel root UUID.
6. Compare the mirror to the snapshot, record phase-aware machine-readable
   state, prune retention only after successful verification, sync, unmount
   owned mounts, and check the boot filesystem offline.

Keep several weekly snapshots. Exclude virtual filesystems, transient mounts,
the backup tree itself, general user caches, trash, and downloaded apt package
archives. Preserve installed language toolchains and package-manager caches
such as Rust toolchains, the Cargo registry, and npm cache because the USB drive
is intended to serve as a usable temporary workstation. Reject unexpected
devices at target mountpoints and never unmount a correct mount that predates
the run. Run the batch as root from a systemd timer with a lock, private mount
namespace, cleanup-aware signal handling, and bounded start and stop timeouts.

For an interactive run, pass `--progress` to print phase transitions, mount
decisions, aggregate percentage/rate/ETA, transfer statistics, and warnings
without listing files. Pass `--noisy` or `-v` to add exclusions and every
changed rsync path. Scheduled runs remain concise by default.

Runtime dependencies include Python 3, rsync, util-linux, dosfstools, e2fsprogs,
parted, and systemd. Install `backup_drive.py` as a root-owned executable under
`/usr/local/sbin`; keep the source in this capsule. Keep the target identity,
labels, retention, and any path overrides in a root-owned local environment
file outside this repository.

Before enabling the timer on a rebuilt machine:

1. Run the focused unit tests.
2. Install the script and tracked systemd units.
3. Create the machine-local environment file from the private restoration note.
4. Run one interactive noisy backup and inspect its state and canonical
   snapshot.
5. Perform a recovery boot drill.
6. Enable the timer only after the manual run and drill succeed.

Heartbeat should read the backup state file and alert when the latest run
failed, no run exists, or the last success is older than the expected weekly
window. Heartbeat observes the job; it does not run the privileged backup.

## Recovery drill

1. Confirm the latest backup state reports success.
2. Shut down the Pi.
3. Disconnect or disable the NVMe boot device.
4. Boot from the USB backup drive.
5. Verify root and boot mounts, networking, SSH, and critical services.
6. Reconnect the NVMe device and restore the intended boot order.

## Do not store

- Target serials, UUIDs, hostnames, live state files, or logs.
- SSH host keys, Tailscale identity, or rendered EEPROM configuration.
