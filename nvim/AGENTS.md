# nvim agent guide

## Purpose

This folder stores canonical Neovim config for LazyVim-based setup.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `init.lua`
- `lua/`
- `lazyvim.json`
- `lazy-lock.json`
- `stylua.toml`

## Managed scope

Managed files are config files meant to live under `~/.config/nvim/`, especially:

- `init.lua`
- `lua/**`
- `lazyvim.json`
- `lazy-lock.json`
- `stylua.toml`

Repo docs like `README.md` and `LICENSE` stay repo-only unless user explicitly changes that plan.

## Import

- Import only managed config files.
- Do not import plugin clones, Mason packages, caches, compiled Lua cache, swap files, or other runtime state from `~/.local/share/nvim` or `~/.cache/nvim`.

## Apply

- Apply managed config tree to `~/.config/nvim` by copy or link.
- Copy safer when repo not meant to stay on machine.
- Link fine when user wants repo-backed live config.
- Leave `~/.local/share/nvim` and `~/.cache/nvim` alone. Neovim and plugin managers own those trees.

## Exclusions

Unmanaged live paths include `~/.local/share/nvim/**`, `~/.cache/nvim/**`, swap files, plugin downloads, Mason data, and other runtime-generated files outside tracked config tree.

## Verify

- Key managed files exist under `~/.config/nvim`.
- Use `pytest` for repo checks.
- Use `nvim --headless '+qa'` for quick syntax/bootstrap sanity check when needed.
