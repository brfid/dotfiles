# dotfiles

Personal system configuration, symlinked into place by `install.sh`.

## Directory layout

- `nvim/` -- Neovim (LazyVim)
- `shell/` -- Zsh, environment variables
- `bash/` -- Bash
- `tmux/` -- Tmux (Pi only)
- `git/` -- Git
- `vscode/` -- VS Code user settings
- `x11/` -- X11 session config (Pi only)
- `scripts/` -- Utility automation
- `claude/` -- Claude Code settings (default: granular permissions; sandbox: wide-open for VMs)
- `system/` -- System configs (symlinked into `/etc/` via sudo)

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for known issues and workarounds (signal-cli linking, etc.).

## Scripts

- `scripts/gdrive_backup.py` -- Google Drive backup wrapper (archive + bisync modes)

## Platforms

- **Common** — Runs on all systems (nvim, zsh, bash, vscode, gh, claude)
- **Pi 5** — Tmux, X11, systemd timers, system configs, minetest helpers
- **edcloud** — Tmux, rclone-dropbox systemd service, server shell aliases
- **macOS** — Common config only (nvim, zsh, bash, vscode, gh, claude)

## Quick start / Install

```bash
./install.sh   # auto-detects profile and installs
```

### Auto-detection order

1. `DOTFILES_PROFILE` environment variable (highest priority)
2. `~/.dotfiles-profile` marker file (contains the profile name as a single word)
3. Hostname match (`edcloud` → edcloud profile)
4. Hardware/OS detection (Raspberry Pi model string → pi; Darwin → mac)

### Manual profile override

Create a marker file to pin the profile permanently:

```bash
echo "pi" > ~/.dotfiles-profile
./install.sh
```

Or use an environment variable for a one-shot override:

```bash
DOTFILES_PROFILE=pi ./install.sh
```

### Running tests

```bash
pip install -e '.[dev]'
pytest
```

## Maintenance

`edcloud` bootstrap depends on this repo exposing a working `install.sh` at `~/src/dotfiles/install.sh`.

If the install entrypoint, its location, or its behavior changes, update `edcloud` in the same change or immediately after so rebuilds keep working.
