# Manifest

Usual live paths for the preferences in this repo. Treat this as a map for a
human or LLM, not an install spec.

| Repo path | Usual live path | Note |
| --- | --- | --- |
| `shell/bashrc` | `~/.bashrc` | Bash-specific startup |
| `shell/zshrc` | `~/.zshrc` | Zsh-specific startup |
| `shell/profile` | `~/.config/shell/profile` | Shared shell preferences |
| `shell/aliases` | `~/.config/shell/aliases` | Shared aliases and functions |
| `git/ignore` | `~/.config/git/ignore` | Global ignore patterns |
| `git/.gitleaks.toml` | `~/.config/git/.gitleaks.toml` | Secret scan config |
| `git/hooks/pre-commit` | `~/.config/git/hooks/pre-commit` | Optional global hook |
| `nvim/` | `~/.config/nvim/` | Copy or symlink as a directory |
| `tmux/tmux.conf` | `~/.tmux.conf` | tmux config |
| `tmux/scripts/status-lite.sh` | `~/.tmux/status-lite.sh` | Helper used by tmux config |
| `alacritty/alacritty.toml` | `~/.config/alacritty/alacritty.toml` | Terminal preferences |
| `yazi/yazi.toml` | `~/.config/yazi/yazi.toml` | Yazi config |
| `yazi/keymap.toml` | `~/.config/yazi/keymap.toml` | Yazi keymap |
| `gh/config.yml` | `~/.config/gh/config.yml` | GitHub CLI config |
| `neomutt/neomuttrc` | `~/.config/neomutt/neomuttrc` | Mail client config |
| `neomutt/mailcap` | `~/.config/neomutt/mailcap` | Mailcap handlers |
| `codex/README.md` | n/a | Basic Codex restore notes |
| `opencode/README.md` | n/a | Basic OpenCode restore notes |

Before copying from a live machine back into this repo, remove local paths,
account-specific values, generated state, and machine-specific setup.
