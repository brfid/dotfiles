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
- `copilot/` — GitHub Copilot CLI config
- `yazi/` — Yazi file manager keybindings

Not stow-managed:

- `system/` — Reference copies of `/etc/` configs (unbound, cpufreq, rsnapshot, lightdm, logrotate)
- `scripts/` — Google Drive backup wrapper, Signal CLI setup
- `python/` — Python tooling config templates (Black, Flake8, mypy) — copy into project roots
- `openclaw/` — OpenClaw bootstrap script for the Jean-Claude Telegram agent
- `jean-claude/` — System overview for the Jean-Claude family assistant
- `templates/` — `.gitconfig.example` template
- `tests/` — pytest suite (bash syntax, stow structure, gdrive_backup)

## Key details

- Machine-local secrets go in `~/.secrets` (created from `secrets.example`; not committed)
- Per-machine shell config: symlink the appropriate file from `shell/.config/shell/local.d/` to `~/.config/shell/local`
- `edcloud` repo has its own `scripts/setup-dotfiles.sh` that runs stow for its machine
