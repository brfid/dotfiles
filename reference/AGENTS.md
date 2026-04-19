# reference agent guide

## Purpose

This folder stores reference files, templates, and host-level configs that usually need manual review.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- relevant subdir README files under `reference/linux/`

## Scope

This folder is different from normal user-config tools.
Main parts:

- `reference/linux/`: host-level files, often for `/etc/`, often need sudo and review
- `reference/python/`: reusable project templates and defaults
- `reference/templates/`: helper templates like `.gitconfig.example`

## Import

- Import only when user explicitly wants to capture a reviewed host-level file or template.
- Keep live-to-repo imports narrow and documented.
- For `/etc/` files, compare against live system first and explain purpose before updating repo copies.

## Apply

- Do not auto-apply this folder as one unit.
- For `reference/linux/` files, show diff, explain change, get confirmation, then install manually with the right target path and permissions.
- For project templates under `reference/python/` and `reference/templates/`, copy into target project or home path only when user asks.

## Exclusions

Unmanaged live paths are broad by default here. Nothing under `/etc/` or other host-level dirs should be treated as blindly synced.

## Verify

- Verify by diffing target file and checking service-native commands after manual install.
- Run `pytest` for repo checks.
