# dotfiles agent guide

Read `README.md`, `RESTORE.md`, and `MANIFEST.md` first.

## Repo Purpose

Public preference dotfiles for LLM-assisted machine setup. Keep durable config
that is hard enough to recreate that it deserves a canonical copy.

This repo is not for scripts, full machine state, job-specific setup, generated
client state, or private values.

Agent-related policy, private skills, and agent definitions live in the private
agents repo. Do not add them here.

## Rules

- Keep tracked files safe to publish.
- Keep job-specific config, machine-specific config, credentials,
  account-specific values, private paths, sessions, logs, caches, generated
  state, and databases out of git.
- Prefer plain Markdown and canonical config files over automation.
- Use `MANIFEST.md` as the restore map.
- Preserve unrelated user changes.

## Read Order

For broad work:

1. `README.md`
2. `RESTORE.md`
3. `MANIFEST.md`
4. Relevant tool folder

For one tool:

1. `MANIFEST.md`
2. Relevant tool folder
