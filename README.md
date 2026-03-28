# dotfiles

Personal system configuration, deployed with [GNU Stow](https://www.gnu.org/software/stow/).

## Packages

Each directory is a stow package. Its contents mirror the target path under `$HOME`.

| Package | Target | Description |
|---------|--------|-------------|
| `bash/` | `~/.bashrc` | Bash config |
| `shell/` | `~/.config/shell/`, `~/.zshrc` | Shared aliases, zsh, per-machine shell snippets |
| `nvim/` | `~/.config/nvim/` | Neovim (LazyVim) |
| `tmux/` | `~/.tmux.conf`, `~/.tmux/` | Tmux |
| `git/` | `~/.config/git/` | Git hooks, gitleaks config |
| `gh/` | `~/.config/gh/` | GitHub CLI |
| `claude/` | `~/.claude/` | Claude Code settings, commands, plugins |
| `vscode/` | `~/.config/Code/User/` | VS Code settings and snippets |
| `neomutt/` | `~/.config/neomutt/` | Neomutt |
| `systemd-user/` | `~/.config/systemd/user/` | User systemd services and timers |
| `x11/` | `~/.xprofile`, `~/.xinitrc` | X11 session config |

Not stow-managed:

- `system/` — Reference copies of `/etc/` configs (unbound, lightdm, cpufreq, rsnapshot, etc.). Copy manually with `sudo`.
- `templates/.gitconfig.example` — Template; copy to `~/.gitconfig` and fill in name/email.
- `secrets.example` — Template; copy to `~/.secrets` and fill in values.
- `scripts/` — Utility scripts (Google Drive backup, Signal CLI tools).

## Usage

```bash
cd ~/src/dotfiles
stow --target="$HOME" <package> [<package> ...]
```

To adopt an existing config file into the repo:

```bash
stow --adopt --target="$HOME" <package>   # moves file into repo, replaces with symlink
git diff                  # review what changed
```

## Setup checklists

### All machines

```bash
git clone <repo> ~/src/dotfiles
cd ~/src/dotfiles
stow --target="$HOME" bash shell nvim gh claude vscode git

# One-time manual steps:
cp secrets.example ~/.secrets && chmod 600 ~/.secrets  # edit with real values
cp templates/.gitconfig.example ~/.gitconfig             # edit name/email
```

### Pi

```bash
stow --target="$HOME" bash shell nvim gh claude vscode git tmux x11 neomutt systemd-user

# Profile-specific shell config:
ln -sfn ~/src/dotfiles/shell/.config/shell/local.d/pi.sh ~/.config/shell/local

# System configs (review before copying):
sudo cp system/unbound/unbound.conf /etc/unbound/unbound.conf
sudo cp system/unbound/unbound.conf.d/* /etc/unbound/unbound.conf.d/
sudo cp system/cpufreq/cpufrequtils /etc/default/cpufrequtils
sudo cp system/lightdm/lightdm.conf.d/99-local.conf /etc/lightdm/lightdm.conf.d/
sudo cp system/swap/dphys-swapfile /etc/dphys-swapfile
# Edit templated files (replace __USER__ etc.) before copying:
# system/rsnapshot/rsnapshot.conf → /etc/rsnapshot.conf
sudo systemctl daemon-reload
```

### edcloud

See `edcloud` repo — `scripts/setup-dotfiles.sh` handles stow and shell linking.

### macOS

```bash
stow --target="$HOME" bash shell nvim gh claude vscode git
```

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md).

## Scripts

- `scripts/gdrive_backup.py` — Google Drive backup wrapper (archive + bisync modes)
- `scripts/signal/` — Signal CLI setup, backup, and scli wrapper

## Running tests

```bash
pip install -e '.[dev]'
pytest
```
