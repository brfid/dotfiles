# claude agent guide

## Purpose

This folder stores canonical Claude Code user config worth backing up.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `settings.json`
- `settings.anthropic.json`
- `settings.glm.json`

## Managed scope

Managed files:

- settings variants
- shared `CLAUDE.md`
- local marketplace manifest at `plugins/.claude-plugin/marketplace.json`

## Import

- Import only managed files from `sync.toml`.
- Do not import `.credentials.json`, backups, cache, debug output, file history, downloaded marketplace data, or plugin install state.
- If live file has machine-local paths, keep repo convention unless user explicitly wants that path backed up.
- Keep private workspace access such as `additionalDirectories` in
  `~/.claude/settings.local.json`, not tracked settings files.

## Apply

- Apply only managed files.
- Settings and `CLAUDE.md` may be copied or linked.
- Local marketplace manifest should usually be copied into mixed runtime `~/.claude/plugins/` tree, not linked.
- Do not create duplicate live hook files. Managed settings already point at repo scripts.

## Exclusions

Unmanaged live paths include credentials, backups, cache, debug logs, file history, plugin caches, plugin install state, and downloaded marketplace dirs.

## Verify

- Managed files exist in `~/.claude`.
- Runtime-only files stay out of git.
- Run `pytest`.
