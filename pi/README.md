# pi

Role: host config and hotspare strategy. See `debian/` for OS-level preferences.

## Boot order

NVMe first, microSD fallback. Configured in EEPROM (`sudo rpi-eeprom-config --edit`). On NVMe failure, the Pi boots the hotspare SD automatically on next reboot.

## CPU policy

Prefer conservative CPU frequency scaling for daily desktop use. Keep the stock
Pi 5 top CPU frequency available for sustained work, but avoid overclocking,
`force_turbo`, or hard max-frequency caps unless there is a specific thermal or
latency reason.

## Hotspare SD

A standalone OS install on microSD. The SD has its own SSH host keys and Tailscale identity. It is not a clone — it receives allowlisted state from the NVMe host weekly.

## Sync

A weekly cron job mounts the SD by label, rsyncs allowlisted paths, snapshots system state, and unmounts.

## Failover drill

1. Shut down Pi.
2. Remove NVMe (or let it fail).
3. Boot — SD picks up automatically.
4. SSH to hotspare hostname.
5. Check last-sync timestamp for freshness.
6. Run dotfiles stow from `~/src/dotfiles`.
7. Reinstall packages from snapshot.
8. `sudo tailscale up` if needed.
9. Rename hostname if clients require it.

## Do not store

- Runtime config, crontabs, systemd units, or the sync script itself.
- SSH host keys, Tailscale identity, EEPROM config.
- SD image files or provisioning scripts (one-time, already done).
