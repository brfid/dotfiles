# systemd agent guide

## Purpose

This folder stores canonical user-level systemd units worth backing up.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- tracked `.service` and `.timer` files

## Managed scope

Managed files are tracked user units meant to live under `~/.config/systemd/user/`.

## Import

- Import only tracked unit files.
- Do not import unrelated user units, drop-in dirs, generated symlinks under `*.wants/`, or timestamped backup files.
- If a new unit is worth keeping, add it here and update `sync.toml` deliberately.

## Apply

- Apply tracked unit files by copy or link into `~/.config/systemd/user/`.
- Leave `default.target.wants/`, `timers.target.wants/`, and other generated enablement symlinks alone unless user explicitly wants them managed.
- After changing live unit files, run `systemctl --user daemon-reload`.
- Enable or disable units intentionally; do not assume every tracked unit should be enabled on every machine.

## Exclusions

Unmanaged live paths include unrelated user services, drop-ins, generated `*.wants/` symlinks, and timestamped backups.

## Verify

- Managed unit files exist under `~/.config/systemd/user/`.
- `systemctl --user daemon-reload` succeeds after apply.
- Run `pytest`.
