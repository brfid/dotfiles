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
| `claude/` | `~/.claude/` | Claude Code settings, commands, plugins, and the local Jean-Claude plugin mirror |
| `copilot/` | `~/.copilot/copilot-instructions.md`, `~/.copilot/mcp-config.json` | GitHub Copilot CLI config (manual symlinks; `~/.copilot/` is not stow-managed) |
| `vscode/` | `~/.config/Code/User/` | VS Code settings and snippets |
| `neomutt/` | `~/.config/neomutt/` | Neomutt |
| `systemd-user/` | `~/.config/systemd/user/` | User systemd services and timers |
| `x11/` | `~/.xprofile`, `~/.xinitrc` | X11 session config |

| `jean-claude/` | — | System overview for the Jean-Claude family assistant ([README](jean-claude/README.md)) |

Not stow-managed:

- `system/` — Reference copies of `/etc/` configs (unbound, lightdm, cpufreq, rsnapshot, etc.). Copy manually with `sudo`.
- `templates/.gitconfig.example` — Template; copy to `~/.gitconfig` and fill in name/email.
- `secrets.example` — Template; copy to `~/.secrets` and fill in values.
- `scripts/` — Utility scripts (Google Drive backup, Signal CLI tools).
- `openclaw/` — OpenClaw bootstrap wrapper. The real project logic lives in `~/src/jean-claude`; this package captures how the machine-level runtime is restored.

Project-specific AI repos intentionally stay outside dotfiles:

- `~/src/homeschool` — canonical homeschool information store
- `~/src/jean-claude` — Claude-facing skills, persona, helper scripts, and OpenClaw runtime docs

## Usage

`.stowrc` sets `--target=~` automatically, so you can run stow without the flag:

```bash
cd ~/src/dotfiles
stow <package> [<package> ...]
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
ln -s ~/src/dotfiles/copilot/.copilot/copilot-instructions.md ~/.copilot/copilot-instructions.md
ln -s ~/src/dotfiles/copilot/.copilot/mcp-config.json ~/.copilot/mcp-config.json

# Claude-local project plugin:
claude plugin install ~/src/jean-claude

# Copilot CLI plugins (one-time; not stow-managed):
copilot plugin marketplace add anthropics/skills
copilot plugin install document-skills@anthropic-agent-skills
copilot plugin install example-skills@anthropic-agent-skills
copilot plugin install security-best-practices@awesome-copilot
copilot plugin install testing-automation@awesome-copilot
copilot plugin install context-engineering@awesome-copilot
# Note: Context7 MCP server (live doc lookups) — mcp-config.json handles this (stow-managed)
```

### Pi

```bash
stow --target="$HOME" bash shell nvim gh claude vscode git tmux x11 neomutt systemd-user

# Profile-specific shell config:
ln -sfn ~/src/dotfiles/shell/.config/shell/local.d/pi.sh ~/.config/shell/local

# Optional Telegram runtime for the Jean-Claude project:
source ~/.secrets && ~/src/dotfiles/openclaw/setup.sh

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

## Claude / OpenClaw project note

The Jean-Claude homeschool assistant is intentionally split:

- project logic in `~/src/jean-claude`
- canonical family data in `~/src/homeschool`
- durable user-level setup in this repo

That split is a feature: the project repos stay inspectable and portable, while dotfiles preserves the machine shell around them.

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
