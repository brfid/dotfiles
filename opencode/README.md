# OpenCode

Use `agents/` as source text when updating local OpenCode behavior.

- Local agents: `~/.config/opencode/agents/*.md`
- Agent rules: `agents/rules.md`
- Agent personas: `agents/personas/`

Generate local OpenCode agent files from the rules and personas. Add OpenCode YAML frontmatter locally because model names, permissions, and provider settings are client-specific.

- Do not symlink local OpenCode config back to this repo.
- Keep auth, session state, node modules, generated config, package locks, and plugin caches out of git.
