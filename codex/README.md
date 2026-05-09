# Codex config

This folder stores the canonical user-level Codex configuration for this machine.

`~/.codex/` stays a real writable directory because Codex writes auth, sessions, logs, sqlite state, caches, plugin payloads, and generated UI state there.

## Managed files

Managed by this repo:

- `config.toml` → `~/.codex/config.toml`
- `instructions/caveman.md` → `~/.codex/instructions.md`
- `rules/default.rules` → `~/.codex/rules/default.rules`
- `memories/markdown-soft-wrap.md` → `~/.codex/memories/markdown-soft-wrap.md`

Everything else in `~/.codex/` is live runtime state or plugin-owned output unless `sync.toml` says otherwise.

## Current policy

- Default model: `gpt-5.5`
- Reasoning effort: `high`
- Shared instructions: caveman natural-language mode from `instructions/caveman.md`
- Enabled plugin: `superpowers@openai-curated`
- Enabled MCP server: `openaiDeveloperDocs` at `https://developers.openai.com/mcp`
- Trusted project roots are explicit in `config.toml` with `/home/__USER__`
  placeholders for public-repo safety.
- UI acknowledgement state, model-picker NUX state, auth, sessions, logs, caches, sqlite files, and plugin-generated payloads are not tracked.

## Rules policy

Rules live in `rules/default.rules`.

Keep rules narrow and explain why they exist:

- Prefer exact prefixes over broad command families.
- Use `allow` only for low-risk, repeatable commands.
- Use `prompt` for commands that can alter durable system state.
- Add `justification`, `match`, and `not_match` examples when practical.

Current deliberate rules:

- Allow `crontab -l` because it is read-only.
- Prompt for broader `crontab` commands because they can change scheduled jobs.
- Allow `tmux` because it controls the active terminal session and is needed for config reloads and inspection.

When the `codex` CLI is on `PATH`, test rules with:

```bash
codex execpolicy check --pretty --rules ~/.codex/rules/default.rules -- crontab -l
```

## Memories policy

Manage durable, low-risk personal preferences only.

Current managed memory:

- `markdown-soft-wrap.md`: prefer soft-wrapped Markdown prose.

Do not import raw conversation history, logs, session summaries, or private family/project details into this repo.

## Skill lifecycle

Use skills for repeatable workflows, not one-off notes.

Minimal lifecycle:

1. Draft a focused `SKILL.md` for one job.
2. Include trigger phrases, inputs, outputs, steps, and verification.
3. Keep early versions local while testing.
4. Use the skill on real work at least three times.
5. Refine wording when Codex misses the trigger or follows the wrong steps.
6. Promote to a plugin only when the workflow is stable and worth reinstalling or sharing.

Prefer small skills over broad bundles. Put deterministic helper scripts in the skill only when they improve reliability.

Local experimental skills may live under `~/.codex/skills/<name>/SKILL.md`. Shared repo or team skills should live in a repo-owned `.agents/skills/<name>/SKILL.md` or be packaged as a plugin.

## Plugins and MCP policy

Install only plugins or MCP servers that remove a repeated manual loop.

Keep installed plugin payloads out of git. Document how to reinstall them instead of mirroring generated files.

Current MCP servers:

- `openaiDeveloperDocs`: official OpenAI developer documentation lookup.

Current installed plugin payloads:

- Superpowers via `plugins/cache/openai-curated/superpowers/**` — enabled in `config.toml`.
- Compound Engineering via `AGENTS.md`, `agents/compound-engineering/**`, `compound-engineering/**`, and `skills/compound-engineering/**` — installed by the Every installer and treated as plugin-owned.

Compound Engineering install command:

```bash
bunx @every-env/compound-plugin install compound-engineering --to codex
```

On this Pi, `bun` was installed with npm and may require the npm global bin directory on `PATH` in noninteractive shells:

```bash
PATH="$HOME/.npm-global/bin:$PATH" bunx @every-env/compound-plugin install compound-engineering --to codex
```

Useful candidate not yet configured here:

- Context7 MCP for current library documentation.

Do not install broad app plugins such as Gmail, Drive, or Slack unless there is a concrete workflow and data-access decision.

## Import workflow

Import only managed files:

```bash
cp ~/.codex/config.toml codex/config.toml
cp ~/.codex/rules/default.rules codex/rules/default.rules
cp ~/.codex/memories/markdown-soft-wrap.md codex/memories/markdown-soft-wrap.md
```

Before committing, replace direct home paths with `/home/__USER__` and remove
transient UI state from `config.toml`, such as `[tui.model_availability_nux]`.

## Apply workflow

Apply managed files to the live Codex directory:

```bash
mkdir -p ~/.codex/rules ~/.codex/memories
sed "s#/home/__USER__#$HOME#g" codex/config.toml > ~/.codex/config.toml
ln -sfn "$HOME/src/dotfiles/codex/instructions/caveman.md" ~/.codex/instructions.md
cp codex/rules/default.rules ~/.codex/rules/default.rules
cp codex/memories/markdown-soft-wrap.md ~/.codex/memories/markdown-soft-wrap.md
```

Restart Codex after changing `config.toml`, rules, plugins, or MCP setup.

## Verify

Run repo checks:

```bash
pytest
scripts/check_markdown.sh
```

Run Codex checks:

```bash
test -f ~/.codex/config.toml
test -e ~/.codex/instructions.md
test -f ~/.codex/rules/default.rules
test -f ~/.codex/memories/markdown-soft-wrap.md
```
