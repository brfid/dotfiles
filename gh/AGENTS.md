# gh agent guide

## Purpose

This folder stores canonical GitHub CLI user config worth backing up.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `config.yml`

## Managed scope

Managed now:

- `config.yml`

## Import

- Import only `config.yml` unless user expands scope.
- Do not import `hosts.yml`; it contains login/token material.
- Ignore timestamped backups like `config.yml.pre-dotfiles.*`.

## Apply

- Apply `config.yml` by copy or link.
- Leave `hosts.yml` and login state unmanaged.

## Exclusions

Unmanaged live paths include `hosts.yml` and timestamped backup files.

## Verify

- `~/.config/gh/config.yml` exists.
- Auth material stays out of git.
- Run `pytest`.
