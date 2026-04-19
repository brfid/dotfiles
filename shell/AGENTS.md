# shell agent guide

## Purpose

This folder stores canonical shell startup files, shared aliases, and machine-local snippets.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `bashrc`
- `zshrc`
- `aliases`
- `local/`

## Managed scope

Managed files:

- startup files
- shared aliases
- tracked local snippets under `local/`

## Import

- Import only managed files.
- Treat `local/*.sh` as curated machine variants.
- Import live `~/.config/shell/local` into matching tracked variant only when user wants that variant preserved.
- Do not invent new profile machinery outside this folder. If new machine variant worth keeping, add file under `local/` and document it here.

## Apply

- Apply `bashrc` to `~/.bashrc` and `zshrc` to `~/.zshrc` only on machines that use those shells.
- Apply `aliases` to `~/.config/shell/aliases` by copy or link.
- Apply exactly one chosen local variant to `~/.config/shell/local` by copy or link.
- Do not assume all variants belong on every machine.

## Exclusions

Unmanaged live paths include shell history files, ad hoc local shell scripts outside tracked variant set, and anything not declared in `sync.toml`.

## Verify

- Selected startup files and shell config paths exist after apply.
- Run `pytest` for shell syntax checks.
