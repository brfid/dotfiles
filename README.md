# dotfiles

Personal dotfiles for LLM-orchestrated preference recall across machines.

Hooks keep generated state, private data, and machine-specific files out of git
so the repo stays clean.

## Model

- Let the LLM adapt these files to the current OS, package manager, and tool
  versions at setup time.
- Each root folder owns its setup notes in its own `README.md`.
