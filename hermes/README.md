# hermes

Role: self-improving AI agent for coding, automation, and messaging platforms.

Facts:
- Hermes is NousResearch's `hermes-agent`, installed via git clone into the
  hermes home directory.
- Install method is `git`; the CLI shim at `~/.local/bin/hermes` delegates to
  the venv binary inside the hermes-agent source tree.
- Rebuild: clone the repo, create a Python 3.11 venv with `uv`, install from
  `uv.lock` for hash-verified dependencies.
- Terminal backend is `local`; commands run directly on the host.
- Profiles isolate per-context config, sessions, memory, and skills. Each
  profile has its own `config.yaml`, `.env`, `state.db`, and session history.
- Keep profile responsibilities narrow. A narrowly scoped profile should use a
  focused `SOUL.md`, compact built-in memory, and only the skills its role
  requires.
- Treat skills as portable procedural memory. Sensitive personal records belong
  in machine-local private state outside the profile and skill tree; skills may
  load those files on demand.
- Use `memory.write_approval` and `skills.write_approval` for sensitive
  profiles. Opt a narrowly scoped profile out of bundled-skill seeding when the
  general catalog would add noise or accidental capability.
- Keep `USER.md` for stable user preferences, `MEMORY.md` for critical facts
  needed in every session, session search for transcript history, and skills
  for reusable procedures.
- OpenCode Go and OpenCode Zen are separate Hermes providers with separate
  credentials (`OPENCODE_GO_API_KEY` and `OPENCODE_ZEN_API_KEY`). Primary models
  are profile-specific: DeepSeek V4 Pro and Qwen3.7 Plus through Go, Claude
  Sonnet 4.6 through Zen where that model fits, and Claude Opus 4.8 through Zen
  for sensitive, higher-stakes work.
- Use DeepSeek V4 Pro through Go as the default delegation model for every
  profile. Use DeepSeek V4 Flash for lightweight text auxiliary work. Keep
  profile-specific auxiliary overrides where justified.
- Keep convenient aliases for the preferred model set: `max` for Qwen3.7 Max,
  `plus` for Qwen3.7 Plus, `deepseek` for DeepSeek V4 Pro, `glm` for GLM-5.1,
  and `sonnet` for Claude Sonnet 4.6 through Zen.
- The OpenCode provider model pickers may continue to show their complete
  catalogs; aliases identify the intentionally selected high-level subset.
- For OpenCode Zen, use the bare model ID `claude-sonnet-4-6` with provider
  `opencode-zen`; Hermes selects the Anthropic Messages transport automatically.
- The gateway script (`scripts/hermes-gateway` in the source tree) can install
  and manage a systemd user service for messaging platform integration.
- Skills are reusable procedure documents organized by category under the
  hermes home directory. The agent can create new skills after complex tasks.
- Use `agents/` as source text when updating local hermes agent behavior.
  Agent rules and personas live in `agents/rules.md` and `agents/personas/`.
- Codex CLI is available for delegating coding tasks. Install via npm to
  `~/.npm-global/bin/codex`. Requires `export PATH=~/.npm-global/bin:$PATH`
  before use. Uses ChatGPT OAuth authentication (gpt-5.5 model).

Live paths:
- Hermes home: `~/.hermes/`
- Main config: `~/.hermes/config.yaml`
- Environment: `~/.hermes/.env`
- Profiles: `~/.hermes/profiles/<name>/`
- Skills: `~/.hermes/skills/`
- Machine-local private agent data: `~/.local/share/private-state/hermes/`
- Source tree: `~/.hermes/hermes-agent/`
- CLI shim: `~/.local/bin/hermes`
- Codex CLI: `~/.npm-global/bin/codex`

Do not store:
- API keys, tokens, or credentials (`.env` files)
- Session databases (`state.db`), session JSON logs, or conversation history
- `venv/`, `node_modules/`, `__pycache__/`, or other runtime artifacts
- Profile-specific memory files, auth tokens, or private agent policy
- Docker images, container state, or sandbox artifacts
