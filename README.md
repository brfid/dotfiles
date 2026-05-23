# dotfiles

Public personal dotfiles for preference recall across machines.

This repo is not a machine image, bootstrap script, or full home-directory
backup. It keeps durable config choices I want a current SOTA LLM to see when
setting up a machine.

## Model

- Keep public preferences here.
- Keep machine-specific setup, job-specific config, credentials, runtime state,
  caches, generated files, and private values out of this repo.
- Keep agent policy, private skills, and agent definitions in the private
  agents repo, not here.
- Let the LLM adapt these files to the current OS, package manager, and tool
  versions at setup time.
- Each root folder owns its setup notes in its own `README.md`.

## Contents

| Folder | Usual live path | Purpose |
| --- | --- | --- |
| `alacritty/` | `~/.config/alacritty/` | Terminal preferences |
| `codex/` | n/a | Basic Codex restore notes |
| `gh/` | `~/.config/gh/` | GitHub CLI preferences |
| `git/` | `~/.config/git/` | Global ignores, gitleaks, optional hook |
| `neomutt/` | `~/.config/neomutt/` | Mail client preferences |
| `nvim/` | `~/.config/nvim/` | Neovim/LazyVim preferences |
| `opencode/` | n/a | Basic OpenCode restore notes |
| `shell/` | `~/.bashrc`, `~/.zshrc`, `~/.config/shell/` | Shell startup and aliases |
| `tmux/` | `~/.tmux.conf`, `~/.tmux/` | tmux preferences and status helper |
| `yazi/` | `~/.config/yazi/` | File manager preferences |

## Restore

```bash
git clone <repo> ~/src/dotfiles
cd ~/src/dotfiles
cat README.md AGENTS.md
```

Then read the `README.md` in each relevant folder and apply only what makes
sense on the current machine. Prefer copy for one-off setup and symlink for
files actively edited from this repo.

When importing live changes back into this repo, diff first and copy only the
public, reusable preference.
