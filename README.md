# dotfiles

Durable machine and tool configuration notes.

Use this repo with `~/src/agents` when setting up local LLM clients. Dotfiles
owns tool paths and setup notes; agents owns reusable LLM agent config. An LLM
adapts both into local config for the current machine.

Each root folder owns its setup notes in its own `README.md`.

Prefer compact rebuild facts over copied runtime config. Track exact files only
when they are durable, secret-free preferences. For stateful tools, record the
role, live paths, intentional names, dependencies, and source-vs-state boundary.
