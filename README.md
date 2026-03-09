# dotfiles

- `nvim/` - Neovim (LazyVim)
- `micro/` - Micro editor
- `shell/` - Zsh, environment variables
- `bash/` - Bash
- `tmux/` - Tmux
- `git/` - Git
- `vscode/` - VS Code user settings
- `x11/` - X11 session config (xprofile, xinitrc)
- `scripts/` - Sync automation
- `system/` - System configs (symlinked into `/etc/` via sudo)

### Scripts

- `scripts/push_config.py` - sync helper for configured repos
- `scripts/sync_all.py` - wrapper to run sync scripts
- `scripts/push_vault.py` - sync helper for an Obsidian vault repo

## Install

```bash
./install.sh
```
