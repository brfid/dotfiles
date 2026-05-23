# agents

Canonical principles for LLM agent config.

This folder stores the principles to maintain across LLM clients: personas, rules, instructions, and other preferences. An LLM applies them into local client config for Codex, OpenCode, Cline, or another tool.

This repo is source of truth. Local client config is generated output.

Current files:

- `rules.md`: durable rules and preferences to apply across clients
- `personas/plan.md`: read-only planning persona
- `personas/cautious.md`: coding persona that asks before changes
- `personas/yolo.md`: coding persona with broad tool access

Do not add symlinks back to this repo unless explicitly requested. Do not track secrets, auth, sessions, logs, caches, or generated client state.

`git commit` and `git push` require explicit user approval.
