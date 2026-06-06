# shell

Bash and Zsh share a small profile with `nvim`, local bin paths, OpenCode path
support, Rust env loading, aliases, Yazi cwd handoff, tmux launch helpers, and
an interactive `backup` command that runs the whole-system backup with compact
phase and aggregate progress output. The command delegates to the installed
root backup script and loads its root-owned machine-local environment file;
those runtime files are not tracked here. Pass `backup --noisy` or `backup -v`
to add exclusions and file-by-file updates.

Live paths:
- `bashrc` -> `~/.bashrc`
- `zshrc` -> `~/.zshrc`
- `profile` -> `~/.config/shell/profile`
- `aliases` -> `~/.config/shell/aliases`

Notes:
- Secrets and machine-local environment stay outside git.
- `profile` assumes bash or zsh because it uses process substitution for tmux environment repair.
