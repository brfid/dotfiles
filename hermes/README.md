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
- OpenCode Go and OpenCode Zen are separate Hermes providers with separate
  credentials (`OPENCODE_GO_API_KEY` and `OPENCODE_ZEN_API_KEY`). Use
  Qwen3.7 Max as the main conversational model, while Qwen3.7 Plus handles
  auxiliary and delegated work.
- Keep convenient aliases for the preferred model set: `max` for Qwen3.7 Max,
  `plus` for Qwen3.7 Plus, `deepseek` for DeepSeek V4 Pro, `kimi` for Kimi
  K2.6, `glm` for GLM-5.1, and `sonnet` for Claude Sonnet 4.6 through Zen.
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
- Source tree: `~/.hermes/hermes-agent/`
- CLI shim: `~/.local/bin/hermes`
- Codex CLI: `~/.npm-global/bin/codex`

Do not store:
- API keys, tokens, or credentials (`.env` files)
- Session databases (`state.db`), session JSON logs, or conversation history
- `venv/`, `node_modules/`, `__pycache__/`, or other runtime artifacts
- Profile-specific memory files, auth tokens, or private agent policy
- Docker images, container state, or sandbox artifacts
