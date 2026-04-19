______________________________________________________________________

## name: dotfiles-stack description: Use when working in ~/src/dotfiles. Read README.md first, keep tool folders atomic, keep secrets and local identity out of git, place root-owned files under reference/linux, and validate with pytest plus service-native checks.

# Dotfiles Stack

Read:

- `README.md`
- `AGENTS.md`

Use when relevant:

- `reference/linux/samba/smb.conf.pi`
- `reference/linux/tailscale/README.md`
- `tests/test_install.py`

Rules:

- Keep user config in top-level tool dirs.
- Keep tool folders atomic: local `AGENTS.md`, local `sync.toml`, real config files.
- Put root-owned files and short host notes in `reference/linux/<service>/`.
- Keep placeholders and secrets policy from `README.md`.
- Do not mirror full runtime state into repo.
- Validate with `pytest` plus service-native checks when needed.
