# codex

Codex CLI config. `~/.codex/` stays a real writable dir; Codex writes
auth, sessions, sqlite, caches, and plugin payloads there.

Tracked: `config.toml`, `instructions/concise.md`,
`rules/default.rules`, `memories/markdown-soft-wrap.md`. See
`sync.toml`.

`config.toml` uses an absolute `model_instructions_file` path with a
`/home/__USER__` placeholder for public-repo safety. Replace on apply,
strip on import:

```bash
# Import
sed -i "s#$HOME#/home/__USER__#g" codex/config.toml
# Strip transient UI state (e.g. [tui.model_availability_nux]).

# Apply
sed "s#/home/__USER__#$HOME#g" codex/config.toml > ~/.codex/config.toml
```

Restart Codex after changing `config.toml`, rules, or MCP setup.

Never import auth, history, sessions, sqlite, caches, shell snapshots,
UI acknowledgement state, or plugin-owned payloads (`agents/**`,
`skills/**`, generated `~/.codex/AGENTS.md`).
