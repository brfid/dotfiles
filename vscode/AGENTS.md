# vscode agent guide

## Purpose

This folder stores canonical VS Code user settings and tracked snippets.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `settings.json`
- `snippets/`

## Managed scope

Managed files:

- `settings.json`
- tracked snippet files declared in `sync.toml`

## Import

- Import only managed files.
- Do not import `History`, workspace state, extension caches, or timestamped backup files.
- Treat ad hoc snippet files like `markdown.json` as local-only unless user explicitly promotes them into repo and updates `sync.toml`.

## Apply

- Apply `settings.json` by copy or link.
- Apply tracked snippet files by copy or link into `~/.config/Code/User/snippets/`.
- Do not replace full `User/` tree or import editor history.

## Exclusions

Unmanaged live paths include `History/**`, workspace state, ad hoc snippet files not declared in `sync.toml`, and timestamped backups.

## Verify

- `~/.config/Code/User/settings.json` exists.
- Tracked snippet files exist under `~/.config/Code/User/snippets/`.
- Run `pytest`.
