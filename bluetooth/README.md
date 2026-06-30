# bluetooth

Role: pairing-preservation workaround for the Pi 5 on-board Bluetooth adapter.

## Problem

The BCM4345C0 chip on Raspberry Pi 5 sometimes boots with a default firmware
address instead of the burned-in MAC. BlueZ stores every pairing under the
adapter MAC address as a directory name in `/var/lib/bluetooth/`. When the MAC
flips, BlueZ looks in the wrong directory and all previously paired devices
appear to vanish.

## Root cause

The stock `pi-bluetooth` package ships a udev rule
(`/usr/lib/udev/rules.d/90-pi-bluetooth.rules`) that triggers
`bthelper@hci0.service` on Bluetooth adapter arrival. The rule includes
`TEST=="/dev/serial1"`, a condition that is never met on Pi 5 because the
`serial1` symlink is not created. So `bthelper` never runs, and the MAC is
never corrected.

## Fix

Override the rule at `/etc/udev/rules.d/90-pi-bluetooth.rules` dropping the
`TEST` clause. The override takes priority over the packaged rule. `bthelper`
then runs on every boot, detects the default address pattern, and writes the
correct MAC derived from the Pi serial number.

Install: copy `90-pi-bluetooth.rules` to `/etc/udev/rules.d/` and run
`udevadm control --reload-rules`.

## Backup

A daily timer runs `bluetooth-backup-pairings`, which rsyncs
`/var/lib/bluetooth/` to `/var/lib/bluetooth.backup/` preserving permissions
and keeping a small set of timestamped snapshots. The `.last_adapter` marker
records which adapter MAC was current at backup time.

Install the script to `/usr/local/bin/bluetooth-backup-pairings`.

## Restore

A boot-time oneshot service runs `bluetooth-auto-restore` after
`bluetooth.service` is up. For each device in `/etc/bluetooth-auto-restore.conf`
it checks whether a paired `info` file exists under the current adapter
directory. If missing, it searches all adapter directories in the backup and
copies the `info` file into place, then restarts `bluetoothd`. If the backup
has no record of the device, it notifies the desktop user to re-pair manually
via the GUI. Auto-scanning and auto-pairing are a fallback only; the backup
restore path is reliable, the scan path is not.

Connection attempts for already-paired devices are best-effort, deduplicated by
MAC, capped with a hard timeout, and keep `bluetoothctl` event chatter out of
the journal. If a paired device still fails with BlueZ authentication or
`Host is down` errors, re-pair the device; restoring the saved `info` file will
not repair a stale device-side bond.

Install the script to `/usr/local/bin/bluetooth-auto-restore`.

Config file format (`/etc/bluetooth-auto-restore.conf`):
```
# MAC_ADDRESS  human-name
AA:BB:CC:DD:EE:FF  DeviceName
```

Concrete MAC addresses and device names belong in the private restoration
reference, not here.

## Source-vs-state boundary

- `/var/lib/bluetooth/` — live BlueZ state. Not tracked.
- `/var/lib/bluetooth.backup/` — runtime backup. Not tracked.
- `/etc/bluetooth-auto-restore.conf` — rendered from the private reference. Not tracked.
- `/var/log/bluetooth-auto-restore.log` — runtime log. Not tracked.

## Do not store

MAC addresses, link keys, adapter addresses, or any rendered config.
