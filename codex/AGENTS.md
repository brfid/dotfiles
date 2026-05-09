# codex agent guide

## Purpose

This folder stores canonical Codex user config.
`~/.codex/` stays real writable dir.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `README.md`
- `sync.toml`
- `config.toml`
- `instructions/`

## Managed scope

Managed files:

- `config.toml`
- tracked instruction files under `instructions/`
- `rules/default.rules`
- `memories/markdown-soft-wrap.md`

## Import

- Import only managed files.
- Never import auth, history, sessions, sqlite DBs, caches, temp files, shell snapshots, UI acknowledgement state, or generated/plugin-owned payloads.
- `config.toml` uses absolute `model_instructions_file` path now. If target machine uses different home path, update deliberately. Do not guess.

## Apply

- Keep `~/.codex/` real dir.
- Apply `config.toml` by copy.
- Before applying `config.toml`, replace `/home/__USER__` with the target
  machine's real home path.
- Apply instruction files by copy or link. Use copy when unsure.
- Apply managed rules and memories by copy.
- Do not mirror full `~/.codex/` tree into repo.
- Treat `~/.codex/AGENTS.md`, `agents/compound-engineering/**`, `compound-engineering/**`, and `skills/compound-engineering/**` as Every Compound Engineering plugin-owned output. Document reinstall steps instead of tracking generated payloads.

## Exclusions

Unmanaged live paths include auth, history, sessions, logs, sqlite state, caches, temp files, shell snapshots, plugin caches, system skills, and plugin-owned generated files.

## Verify

- `~/.codex/config.toml` exists.
- Managed instruction file exists at configured path.
- Managed rules and memories exist.
- Run `pytest`.
- Run `scripts/check_markdown.sh` after Markdown edits.
