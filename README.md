# dotfiles

My development environment configuration. Currently learning Neovim (LazyVim) and building a portable setup.

## What's Here

- **nvim/** - Full LazyVim configuration
- **shell/** - Zsh config and environment variables template
- **bash/** - Bash configuration
- **tmux/** - Tmux configuration
- **git/** - Git config template
- **scripts/** - Automation scripts for syncing and backups

## Setup

### Quick Install

```bash
git clone https://github.com/brfid/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./install.sh
```

### Manual Setup

1. **Neovim (LazyVim)**
   ```bash
   ln -sfn ~/.dotfiles/nvim ~/.config/nvim
   ```
   Plugins will auto-install on first launch.

2. **Shell Configuration**
   ```bash
   # Zsh
   ln -sfn ~/.dotfiles/shell/zshrc ~/.zshrc

   # Environment variables (copy and customize)
   cp ~/.dotfiles/shell/env.example ~/.config/shell/env
   # Edit ~/.config/shell/env with your actual API keys
   ```

3. **Bash**
   ```bash
   ln -sfn ~/.dotfiles/bash/.bashrc ~/.bashrc
   ```

4. **Tmux**
   ```bash
   ln -sfn ~/.dotfiles/tmux/.tmux.conf ~/.tmux.conf
   ```

5. **Git**
   ```bash
   cp ~/.dotfiles/git/.gitconfig.example ~/.gitconfig
   # Edit ~/.gitconfig with your name and email
   ```

## Learning Notes

### Neovim/LazyVim
- Using LazyVim starter config
- Learning modal editing and vim motions
- Custom keymaps in `nvim/lua/config/keymaps.lua`
- Plugin configs in `nvim/lua/plugins/`

### What I'm Working On
- Building muscle memory for vim motions
- Understanding text objects and operators
- Setting up a reproducible dev environment

## Scripts

- `scripts/sync_all.py` - Auto-sync git repos with conflict handling
- `scripts/push_config.py` - Multi-project git sync controller

## Prerequisites

- Neovim >= 0.9.0
- Git
- Zsh (optional, for shell config)
- Tmux (optional)

## Notes

This is a work in progress as I learn and refine my setup. Commits show the evolution.
