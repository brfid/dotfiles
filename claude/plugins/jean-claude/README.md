# jean-claude

Claude Code plugin that loads the local OpenClaw main agent identity into Claude Code sessions. When invoked, Claude Code adopts the persona, context, and conventions defined in the OpenClaw workspace.

## How it works

The skill auto-activates when the user addresses Claude as "Jean-Claude" or discusses family organization topics (scheduling, homeschool planning, meal planning, chores, etc.). Identity files are read from `~/.openclaw/workspace/` at runtime using `!`cat`` preprocessing. No private data is stored in the plugin.

## Prerequisites

- A configured OpenClaw installation at `~/.openclaw/`
- Workspace identity files: `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, `TOOLS.md`
