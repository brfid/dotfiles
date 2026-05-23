# dotfiles

Public personal dotfiles for preference recall across machines.

This repo is not a machine image, bootstrap script, or full home-directory
backup. It keeps the config choices I want a current SOTA LLM to see when
setting up a new machine.

## Model

- Keep durable, public preferences here.
- Keep machine-specific setup, job-specific configuration, credentials, runtime
  state, caches, and generated files out of this repo.
- Keep agent policy, private skills, and agent definitions in the private
  agents repo, not here.
- Let the LLM adapt these files to the current OS, package manager, and tool
  versions at setup time.

## Contents

| Path | Purpose |
| --- | --- |
| `shell/` | Bash/Zsh startup, shared profile, aliases, tmux launch helpers |
| `git/` | Global ignore, pre-commit hook, secret scan config |
| `nvim/` | Neovim/LazyVim preferences |
| `tmux/` | tmux preferences and status helper |
| `alacritty/` | Alacritty terminal preferences |
| `yazi/` | Yazi preferences |
| `gh/` | GitHub CLI preferences |
| `neomutt/` | Neomutt mail client preferences |
| `codex/` | Basic Codex config notes |
| `opencode/` | Basic OpenCode config notes |

Use `MANIFEST.md` for usual live paths.

## Restore

```bash
git clone <repo> ~/src/dotfiles
cd ~/src/dotfiles
cat README.md RESTORE.md MANIFEST.md AGENTS.md
```

Then ask the LLM to apply only the files that make sense on the current
machine. Prefer copy for one-off setup and symlink for files actively edited
from this repo.

## Public Boundary

Tracked files must be safe to publish. Do not add machine inventories,
job-specific config, credentials, account-specific values, private paths, logs,
sessions, caches, generated client state, or runtime databases.
