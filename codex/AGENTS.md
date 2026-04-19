# codex agent guide

## Purpose

This folder stores canonical Codex user config.
`~/.codex/` stays real writable dir.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `config.toml`
- `instructions/`

## Managed scope

Managed files:

- `config.toml`
- tracked instruction files under `instructions/`

## Import

- Import only managed files.
- Never import auth, history, sessions, sqlite DBs, caches, temp files, shell snapshots, or generated plugin payloads.
- `config.toml` uses absolute `model_instructions_file` path now. If target machine uses different home path, update deliberately. Do not guess.

## Apply

- Keep `~/.codex/` real dir.
- Apply `config.toml` by copy.
- Apply instruction files by copy or link. Use copy when unsure.
- Do not mirror full `~/.codex/` tree into repo.

## Exclusions

Unmanaged live paths include auth, history, sessions, logs, sqlite state, caches, temp files, shell snapshots, and plugin caches.

## Verify

- `~/.codex/config.toml` exists.
- Managed instruction file exists at configured path.
- Run `pytest`.
