# iterm2 agent guide

## Purpose

This folder stores canonical iTerm2 dynamic profile config for macOS.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `profiles.json`

## Managed scope

Managed now:

- `profiles.json`

## Import

- Import only the tracked profile JSON.
- Do not import unrelated macOS app state.

## Apply

- Apply `profiles.json` by copy or link into iTerm2 DynamicProfiles dir on macOS.
- Skip on non-macOS machines.

## Exclusions

Unmanaged live paths include all other iTerm2 app state outside the DynamicProfiles file managed here.

## Verify

- On macOS, managed profile file exists in DynamicProfiles dir.
- Run `pytest`.
