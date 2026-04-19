# gdrive-backup agent guide

## Purpose

This folder stores canonical config for local `gdrive-backup` script runs.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `config.toml`

## Managed scope

Managed now:

- `config.toml`

## Import

- Import only `config.toml`.
- Keep secrets and real account data out of tracked values.
- If live config has machine-only backup entries not worth sharing, keep them out unless user explicitly wants them backed up.

## Apply

- Apply `config.toml` by copy or link to `~/.config/gdrive-backup/config.toml`.
- Use copy when unsure.

## Exclusions

Unmanaged live paths are anything else under `~/.config/gdrive-backup/` not declared in `sync.toml`.

## Verify

- `~/.config/gdrive-backup/config.toml` exists.
- Run `pytest`.
