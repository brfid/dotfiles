# pi

Role: Raspberry Pi 5 host config and hotspare strategy. See `debian/` for OS-level preferences.

## Boot order

NVMe first, microSD fallback. Configured in EEPROM (`sudo rpi-eeprom-config --edit`). On NVMe failure, the Pi boots the hotspare SD automatically on next reboot.

## Hotspare SD

A 32 GB microSD (`/dev/mmcblk0`) with a standalone Raspberry Pi OS Lite Trixie install. Hostname: `<hotspare-hostname>`. User: `<username>`, UID/GID 1000.

Partition labels: `HOTSPARE_ROOT`, `HOTSPAREBT`.

The SD has its own OS, SSH host keys, and Tailscale identity. It is not a clone — it receives allowlisted state from the NVMe host weekly.

## Sync

`~/bin/hotspare-sync` runs weekly (Sunday 04:15) via `/etc/cron.d/hotspare-sync` as root. It mounts the SD by label, rsyncs allowlisted paths, snapshots system state, and unmounts.

Synced paths:
- `~/src/dotfiles` — config source of truth
- `~/.ssh` — keys and authorized_keys
- `~/bin-repo` — custom scripts
- `~/bin` — user binaries (including the sync script itself)
- `~/.codex/memories` — LLM agent memory

System snapshots written to `/var/lib/hotspare/` on the SD:
- `apt-packages.txt` — installed packages
- `crontab-<username>.txt` — user crontab
- `last-sync.txt` — timestamp

## Failover drill

1. Shut down Pi.
2. Remove NVMe (or let it fail).
3. Boot — SD picks up automatically.
4. SSH to `<hotspare-hostname>`.
5. Check `/var/lib/hotspare/last-sync.txt` for freshness.
6. Run dotfiles stow from `~/src/dotfiles`.
7. Reinstall packages from `apt-packages.txt`.
8. `sudo tailscale up` if needed.
9. Rename hostname to `<primary-hostname>` if clients require it.

## Do not store

- Runtime config, crontabs, systemd units, or the sync script itself.
- SSH host keys, Tailscale identity, EEPROM config.
- SD image files or provisioning scripts (one-time, already done).
