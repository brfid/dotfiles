# Codex adapter

Agent policy and private skills live in `~/src/agents`.

- Shared policy: `~/src/agents/policy/`
- Codex base instructions: `~/src/agents/codex/AGENTS.md`
- Live Codex instructions: `~/.codex/AGENTS.md`
- Private portable skills: `~/src/agents/skills/`

Copy `~/src/agents/codex/AGENTS.md` into `~/.codex/AGENTS.md` outside the
managed compound tool-map block. Do not symlink the whole file because Codex
manages that block.

Link private skills individually:

```text
~/.codex/skills/<name> -> ~/src/agents/skills/<name>
```

Do not replace `~/.codex/skills/`; Codex system and plugin skills also live
there.

- Keep `~/.codex/auth.json`, history, sessions, logs, sqlite state, caches, and
  generated state out of git.
- Configure MCP servers and model settings from current Codex docs at setup time.
