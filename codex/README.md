# Codex

Use `~/src/agents` as source text when updating local Codex behavior.

- Live Codex instructions: `~/.codex/AGENTS.md`
- Agent rules: `~/src/agents/rules.md`
- Agent personas: `~/src/agents/personas/`

Apply relevant rule and persona text by editing the human-written sections of
`~/.codex/AGENTS.md`. Preserve the managed compound tool-map block.

- Do not symlink `~/.codex/AGENTS.md`.
- Do not replace `~/.codex/skills/`; Codex system and plugin skills live there.
- Keep `~/.codex/auth.json`, history, sessions, logs, sqlite state, caches, and
  generated state out of git.
- Configure MCP servers and model settings from current Codex docs at setup time.
