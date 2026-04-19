# Jean-Claude

Jean-Claude is a personal AI assistant for a homeschooling family.
Runs on a Raspberry Pi.
Family reaches it through browser app.
Claude Code and Claude Desktop manage it on same machine.

This file gives system overview for humans and LLMs.

## What it does

- answers questions and handles tasks in browser chat
- helps run homeschool: planning, logging, compliance, hour tracking
- processes physical mail from photos into summaries with deadlines
- syncs Google Sheets curriculum tracker into local Markdown
- drafts formal school-district communication

## Architecture

```text
Browser (Cloudflare Access)
   -> web app (NiceGUI, Pi, 127.0.0.1:8000)
   -> MCP server (FastMCP, Pi, Tailscale-only)
   -> Claude API
   -> Jean-Claude skills
   -> private family repo + Google Drive sync
```

Claude Code and Claude Desktop also talk to same MCP server.
They use same skill files and data store.

## Main parts

### Web app

NiceGUI chat client behind Cloudflare Access.
Stateless.
Sends full transcript each turn.
Main family-facing UI.

### MCP server

FastMCP server on Pi, Tailscale-only.
Provides tools and resources.
Used by web app, Claude Desktop, and Claude Code.

### Claude Code

Interactive coding/task environment.
Config lives in `~/src/dotfiles/claude/`.

### Jean-Claude skills

Skill files live in `<private-family-repo>/homeschool/skills/*.md`.
Plain Markdown.
Readable by humans and LLMs.

### Private family repo

`<private-family-repo>/` is canonical private store.
Contains private family logs, plans, compliance docs, private summaries, private context files, and status files.
Backed up by Google Drive sync and GitHub.

## Data flow

### Browser request

User message -> web app -> MCP server -> Claude API + skills -> response

### Mail intake

Phone photo -> Google Drive -> rclone sync -> `<private-family-repo>/homeschool/mail/` -> mail-intake skill -> `summary.md` committed to family repo

### Curriculum tracking

Google Drive files folder -> sync script -> Markdown in `resources/gdrive/` -> lesson-planning context

### Logging

Week-logger skill -> `<private-family-repo>/homeschool/weeks/week-NN.md` + `STATUS.md` -> commit to family repo

## Separation of concerns

| Layer                      | Location                               | Public |
| -------------------------- | -------------------------------------- | ------ |
| System config              | `~/src/dotfiles/projects/jean-claude/` | Yes    |
| Claude settings            | `~/src/dotfiles/claude/`               | Yes    |
| Identity, private context | `<private-family-repo>/jean-claude/`                | No     |
| Homeschool data            | `<private-family-repo>/homeschool/`                 | No     |

Skills can be public.
Data is private.

## Load this with private context

```bash
cat ~/src/dotfiles/projects/jean-claude/README.md
cat <private-family-repo>/jean-claude/IDENTITY.md
```
