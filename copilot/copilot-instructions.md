# Copilot CLI Custom Instructions

## Working style

- Be concise in routine responses; thorough in work.
- Prefer ecosystem tools (npm, pip, stow, etc.) over manual changes.
- Only comment code that needs clarification.
- Clean up temporary files at end of task.

## This system

- Primary dev tree is `~/src`. Full read/write access expected there.
- Dotfiles managed with GNU Stow from `~/src/dotfiles/`.
- Shell: bash and zsh. Python scripts use system Python with no external deps unless unavoidable.
- Editor: Neovim (LazyVim).

## Code conventions

Follow the conventions in `~/src/dotfiles/AGENTS.md` for any code changes.
