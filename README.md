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

Managed separately — `scripts/setup-dotfiles.sh` in the edcloud repo handles linking.
During a rebuild it also pulls environment-specific variables from the edcloud environment
into the shell config, so a fresh instance is fully configured in one pass: dotfiles linked,
credentials injected, shell ready.

## Conventions

See [`AGENTS.md`](AGENTS.md).
