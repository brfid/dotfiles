# dotfiles

Personal system configuration for a Raspberry Pi 5, an edcloud server, and macOS, deployed with [GNU Stow](https://www.gnu.org/software/stow/).

## Repo layout

```
packages/           Stow packages (symlinked into $HOME)
  bash/               .bashrc
  shell/              Shared aliases, zsh, per-machine shell snippets
  nvim/               Neovim (LazyVim)
  tmux/               tmux
  git/                Git hooks, gitleaks config
  gh/                 GitHub CLI
  claude/             Claude Code settings, commands, plugins
  copilot/            GitHub Copilot CLI config
  vscode/             VS Code settings and snippets
  neomutt/            Neomutt
  systemd-user/       User systemd services and timers
  x11/                X11 session config
  yazi/               Yazi file manager keybindings

reference/          Reference configs (copied manually, not stow-managed)
  linux/              /etc/ configs: unbound, cpufreq, lightdm, rsnapshot, etc.
  macos/              macOS app preferences (applied via PlistBuddy/defaults)
  python/             Python tooling templates: Black, Flake8, mypy
  templates/          .gitconfig.example

projects/           Documentation and bootstrap for external projects
  jean-claude/        System overview for the Jean-Claude family assistant
  openclaw/           OpenClaw bootstrap script for Telegram agent

scripts/            Utility scripts: Google Drive backup, Signal CLI setup
tests/              pytest: bash syntax, stow structure, gdrive_backup
```

## Usage

`.stowrc` sets `--dir=packages --target=~`, so stow commands run from the repo root:

```bash
cd ~/src/dotfiles
stow <package> [<package> ...]
```

To adopt an existing config file into the repo:

```bash
stow --adopt <package>   # moves file into repo, replaces with symlink
git diff                  # review what changed
```

## Machine setup

### All machines

```bash
git clone <repo> ~/src/dotfiles
cd ~/src/dotfiles
stow bash shell nvim gh claude vscode git
```

One-time manual steps:

```bash
cp secrets.example ~/.secrets && chmod 600 ~/.secrets  # edit with real values
cp reference/templates/.gitconfig.example ~/.gitconfig  # edit name/email
```

### macOS

```bash
stow bash shell nvim gh claude vscode git
```

### Pi

```bash
stow bash shell nvim gh claude vscode git tmux x11 neomutt systemd-user

# Per-machine shell config:
ln -sfn ~/src/dotfiles/packages/shell/.config/shell/local.d/pi.sh ~/.config/shell/local

# Optional Telegram runtime:
source ~/.secrets && ~/src/dotfiles/projects/openclaw/setup.sh

# Linux system configs (review before copying):
sudo cp reference/linux/unbound/unbound.conf /etc/unbound/unbound.conf
sudo cp reference/linux/unbound/unbound.conf.d/* /etc/unbound/unbound.conf.d/
sudo cp reference/linux/cpufreq/cpufrequtils /etc/default/cpufrequtils
sudo cp reference/linux/lightdm/lightdm.conf.d/99-local.conf /etc/lightdm/lightdm.conf.d/
sudo cp reference/linux/swap/dphys-swapfile /etc/dphys-swapfile
# Edit templated files (replace __USER__ etc.) before copying:
# reference/linux/rsnapshot/rsnapshot.conf → /etc/rsnapshot.conf
sudo systemctl daemon-reload
```

### edcloud

See `edcloud` repo -- `scripts/setup-dotfiles.sh` handles stow and shell linking.

## Project split

The Jean-Claude homeschool assistant is intentionally split across repos:

- Project logic: `~/src/jean-claude`
- Family data: `~/src/homeschool`
- Machine-level setup: this repo (`projects/jean-claude/`, `projects/openclaw/`)

## Scripts

- `scripts/gdrive_backup.py` -- Google Drive backup wrapper (archive + bisync modes)
- `scripts/signal/signal-setup.sh` -- Signal CLI device linking

## Running tests

```bash
pip install -e '.[dev]'
pytest
```

## Coding conventions

See [`AGENTS.md`](AGENTS.md).
