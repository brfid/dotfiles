# Copilot CLI custom instructions

## Working style

- Be concise.
- Be thorough when work needs it.
- Prefer normal ecosystem tools over manual hacks.
- Comment code only when comment helps.
- Clean temporary files at end.

## This system

- Main dev tree: `~/src`.
- Dotfiles live in tool folders under `~/src/dotfiles/`.
- Each tool may carry canonical config plus `AGENTS.md` and `sync.toml`.
- Shells: bash and zsh.
- Python scripts should use system Python unless extra deps are truly needed.
- Editor: Neovim (LazyVim).
