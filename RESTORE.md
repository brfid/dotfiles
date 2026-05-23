# Restore

Use this repo as source material for a SOTA LLM, not as an installer.

## Flow

1. Clone to `~/src/dotfiles`.
2. Read `README.md`, `MANIFEST.md`, and `AGENTS.md`.
3. Pick only the tools used on the current machine.
4. Copy or symlink the relevant files from `MANIFEST.md`.
5. Recreate machine-local values outside git.
6. For Codex or OpenCode, read the matching root folder and the private agents
   repo.

## Importing Changes

When a live config gains a durable preference:

1. Diff it against the repo version.
2. Copy only the public, reusable preference back into this repo.
3. Leave machine-specific setup and private values out.
4. Update `MANIFEST.md` if the live path or restore note changed.

## Agent Config

Agent-related policy, private skills, and agent definitions live in the private
agents repo. This repo only keeps basic client notes under `codex/` and
`opencode/`.
