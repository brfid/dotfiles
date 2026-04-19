# tmux agent guide

## Purpose

This folder stores canonical tmux config plus helper scripts used by status bar.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `tmux.conf`
- `scripts/`

## Managed scope

Managed files:

- `tmux.conf`
- tracked shell scripts under `scripts/`

## Import

- Import only managed files.
- Do not import `~/.tmux/plugins/`; TPM owns that runtime tree.
- If new helper script is worth keeping, add it under `tmux/scripts/` and update `sync.toml` deliberately.

## Apply

- Keep `~/.tmux/` real dir because TPM writes there.
- Apply `tmux.conf` to `~/.tmux.conf` by copy or link.
- Apply managed helper scripts into real `~/.tmux/` dir by copy or link.
- Do not replace `plugins/` dir with repo content.

## Exclusions

Unmanaged live paths include `~/.tmux/plugins/**` and plugin-managed files there.

## Verify

- `~/.tmux.conf` exists.
- Managed helper scripts exist in `~/.tmux/`.
- Run `pytest`.
