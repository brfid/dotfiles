# Copilot CLI Custom Instructions

## Working style

- Be concise in routine responses; thorough in work.
- Prefer ecosystem tools (npm, pip, stow, etc.) over manual changes.
- Only comment code that needs clarification.
- Clean up temporary files at end of task.

## This system

- Primary dev tree is `~/src`. Full read/write access expected there.
- Dotfiles managed via `mapping.yaml` symlink map in `~/src/dotfiles/`, deployed by LLM agent.
- Shell: bash and zsh. Python scripts use system Python with no external deps unless unavoidable.
- Editor: Neovim (LazyVim).

