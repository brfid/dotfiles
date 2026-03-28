# Dotfiles

Personal system configuration repo, deployed with GNU Stow. See `AGENTS.md` for coding conventions.

## Structure

Each top-level directory is a stow package — its contents mirror the target path under `$HOME`. Run `stow <package>` to symlink into place.

- `bash/` — `.bashrc`
- `shell/` — Shared aliases, zsh, per-machine shell snippets (`shell/.config/shell/local.d/`)
- `nvim/` — LazyVim config
- `tmux/` — tmux config
- `git/` — Git hooks, gitleaks config
- `gh/` — GitHub CLI config
- `claude/` — Claude Code settings, commands, plugins
- `vscode/` — VS Code settings and snippets
- `neomutt/` — Neomutt config
- `systemd-user/` — User systemd services and timers
- `x11/` — X11 session config

Not stow-managed:
- `system/` — Reference copies of `/etc/` configs (unbound, cpufreq, rsnapshot, lightdm, logrotate)
- `scripts/` — Signal CLI tools, Google Drive backup wrapper
- `python/` — Python tooling config templates (Black, Flake8, mypy) — copy into project roots

## Key details

- Machine-local secrets go in `~/.secrets` (created from `secrets.example`; not committed)
- Per-machine shell config: symlink the appropriate file from `shell/.config/shell/local.d/` to `~/.config/shell/local`
- `edcloud` repo has its own `scripts/setup-dotfiles.sh` that runs stow for its machine
