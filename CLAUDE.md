# Dotfiles

Personal system configuration repo. See `AGENTS.md` for coding conventions.

## Structure

- `nvim/` — LazyVim config (symlinked to `~/.config/nvim`)
- `python/` — Python tooling config templates (Black, Flake8, mypy)
- `scripts/` — Signal CLI tools (`scripts/signal/`) and Google Drive backup wrapper (`gdrive_backup.py`)
- `shell/` — Zsh config and machine-local shell additions
  - `shell/local.d/` — Per-profile shell snippets (`pi.sh`, `edcloud.sh`);
    linked to `~/.config/shell/local` by the corresponding install profile
- `tmux/` — tmux config
- `system/` — Pi system configs (unbound, cpufreq, rsnapshot, lightdm, logrotate, pihole, ufw, crontab, fstab)
- `install.sh` — Entry point: auto-detects profile, sources `install/common.sh`
  then `install/<profile>.sh`
- `install/` — Profile install scripts
  - `common.sh` — Applied on every system (nvim, zsh, bash, vscode, gh, claude)
  - `pi.sh` — Pi 5 extras (tmux, X11, systemd timers, system configs)
  - `edcloud.sh` — edcloud server extras (tmux, rclone service)
  - `mac.sh` — macOS profile (common config only for now)

## Platforms

- **Common** — Runs on all systems (nvim, zsh, bash, vscode, gh, claude)
- **Pi 5** — Tmux, X11, systemd timers, system configs, minetest helpers
- **edcloud** — Tmux, rclone-dropbox systemd service, server shell aliases
- **macOS** — Common config only (nvim, zsh, bash, vscode, gh, claude)

## Key details

- `edcloud` depends on `~/src/dotfiles/install.sh` existing and working
- Machine-local secrets go in `~/.secrets` (created from `secrets.example` on first install; not committed)
- `python/` configs are reference templates, not globally active — copy into project roots.
