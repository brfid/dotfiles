# dotfiles

> **LLM agent?** Read [`AGENTS.md`](AGENTS.md) — it has the symlink map, machine profiles,
> package lists, and deployment rules. Check `uname -s` and `uname -m`, then proceed.

Personal configuration for a Raspberry Pi 5 and macOS.

Files are organised by purpose (`shell/`, `nvim/`, `tmux/`, ...). `mapping.yaml` declares
the source-to-target symlink map for each machine profile. An LLM agent reads that plus
`AGENTS.md` and handles deployment — fresh repave or drift sync, same operation either way.

To deploy:

```bash
git clone <repo> ~/src/dotfiles
# tell your assistant: "read ~/src/dotfiles/AGENTS.md and sync this machine's dotfiles"
```

One-time setup:

```bash
cp secrets.example ~/.secrets && chmod 600 ~/.secrets
cp reference/templates/.gitconfig.example ~/.gitconfig
```

## Layout

```
shell/          bashrc, zshrc, shared aliases, per-machine local snippets
nvim/           Neovim (LazyVim)
tmux/           tmux.conf and status bar scripts
git/            Git hooks, gitleaks config
gh/             GitHub CLI config
claude/         Claude Code settings, commands, plugins
copilot/        GitHub Copilot CLI config
vscode/         VS Code settings and snippets
neomutt/        Neomutt (Pi only)
x11/            X11 session config (Pi only)
systemd/        User systemd services and timers (Pi only)
yazi/           Yazi file manager keybindings

reference/      System configs requiring sudo — reviewed and applied manually
  linux/          /etc/: unbound, cpufreq, lightdm, rsnapshot, etc.
  python/         Python tooling templates: Black, Flake8, mypy
  templates/      .gitconfig.example

mapping.yaml    Symlink map (source → target) with common/pi/macos profiles
scripts/        Google Drive backup, Signal CLI setup
projects/       Bootstrap docs for jean-claude and openclaw
tests/          pytest: mapping.yaml coverage, bash syntax
```

## edcloud

A second use case alongside Pi/macOS. During provisioning, cloud-init clones this repo and
fetches secrets from AWS SSM (Tailscale auth key, GitHub token, rclone config) to configure
tools directly. `scripts/setup-dotfiles.sh` in the edcloud repo then symlinks these configs
manually after the instance is up. On each login, `~/.bashrc` sources `~/.secrets`
(user-maintained from `secrets.example`) and `shell/local/edcloud.sh`.

## Conventions

See [`AGENTS.md`](AGENTS.md).
