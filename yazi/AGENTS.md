# yazi agent guide

## Purpose

This folder stores canonical Yazi config files.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `yazi.toml`
- `keymap.toml`

## Managed scope

Managed files:

- `yazi.toml`
- `keymap.toml`

## Import

- Import only managed files.
- If live config dir has extra files, treat them as local-only unless user explicitly promotes them into repo.

## Apply

- Apply managed files by copy or link.
- Full-dir link okay only when user wants repo-backed live files and no unmanaged files are present.

## Exclusions

Any live files under `~/.config/yazi/` not declared in `sync.toml` are unmanaged by default.

## Verify

- `~/.config/yazi/yazi.toml` and `~/.config/yazi/keymap.toml` exist.
- Run `pytest`.
