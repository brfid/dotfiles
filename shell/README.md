# shell

Bash and Zsh share a small profile with `nvim`, local bin paths, OpenCode path support, Rust env loading, aliases, Yazi cwd handoff, and tmux launch helpers.

Live paths:
- `bashrc` -> `~/.bashrc`
- `zshrc` -> `~/.zshrc`
- `profile` -> `~/.config/shell/profile`
- `aliases` -> `~/.config/shell/aliases`

Notes:
- Secrets and machine-local environment stay outside git.
- `profile` assumes bash or zsh because it uses process substitution for tmux environment repair.
