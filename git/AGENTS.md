# git agent guide

## Purpose

This folder stores canonical global Git support files safe to share across machines.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `.gitleaks.toml`
- `hooks/pre-commit`

## Managed scope

Managed files:

- global gitleaks config
- global pre-commit hook
- repo-local secret-scan helper script and CI workflow live outside this folder but use this config

## Import

- Import only managed files.
- Do not import `~/.gitconfig`; kept outside repo on purpose.
- Treat `~/.config/git/ignore` as local artifact unless user explicitly wants it backed up here.

## Apply

- Apply `.gitleaks.toml` to `~/.config/git/.gitleaks.toml` by copy or link.
- Apply `hooks/pre-commit` into real `~/.config/git/hooks/` dir by copy or link.
- Keep `git config --global core.hooksPath ~/.config/git/hooks` pointed at managed hook dir.

## Exclusions

Unmanaged live paths include `ignore` and future local-only files under `~/.config/git/` that are not declared in `sync.toml`.

## Verify

- `~/.config/git/.gitleaks.toml` exists.
- `~/.config/git/hooks/pre-commit` exists and is executable.
- `git config --global core.hooksPath` matches `~/.config/git/hooks`.
- Run `pytest`.
