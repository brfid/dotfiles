# neomutt agent guide

## Purpose

This folder stores canonical Neomutt config files.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `neomuttrc`
- `mailcap`

## Managed scope

Managed files:

- `neomuttrc`
- `mailcap`

## Import

- Import only managed files.
- Do not import cache dirs, certificates, or account-specific runtime state.

## Apply

- Apply managed files by copy or link into `~/.config/neomutt/`.
- Use copy when unsure.

## Exclusions

Unmanaged live paths include `cache/**`, `certificates/**`, and any account/runtime files not declared in `sync.toml`.

## Verify

- `~/.config/neomutt/neomuttrc` exists.
- `~/.config/neomutt/mailcap` exists.
- Run `pytest`.
