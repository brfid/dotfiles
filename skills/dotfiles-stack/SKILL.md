---
name: dotfiles-stack
description: Use when working in ~/src/dotfiles. Read README.md first, keep the symlink model intact, keep secrets and local identity out of git, place root-owned files under reference/linux, and validate with pytest plus service-native checks.
---

# Dotfiles Stack

Read:

- `README.md`
- `AGENTS.md`

Use:

- `reference/linux/samba/smb.conf.pi`
- `reference/linux/tailscale/README.md`
- `tests/test_install.py`

Rules:

- Keep the symlink model unchanged unless asked.
- Put user configs in top-level tool dirs.
- Put root-owned files and short host notes in `reference/linux/<service>/`.
- Keep placeholders and secrets policy from `README.md`.
- Link only paths that exist.
