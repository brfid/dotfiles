# Jean-Claude

Jean-Claude is a personal AI assistant built for a homeschooling family. It runs
on a Raspberry Pi, reaches the family through a browser app, and is managed
day-to-day through Claude Code and Claude Desktop on the same machine.

This document describes the overall system. It is intended to be read by humans
and loaded as context by LLMs working within the setup.

---

## What it does

- Answers questions and handles tasks via a browser chat app
- Manages a structured homeschool: lesson planning, daily logging, compliance
  reporting, and hour tracking
- Processes physical mail (photographed → Drive → summarised with deadlines)
- Syncs a Google Sheets curriculum tracker to local Markdown
- Drafts formal communications to the school district

---

## Architecture

```
Browser (Cloudflare Access)
   │
   ▼
Web app (NiceGUI, Pi, 127.0.0.1:8000)
   │
   ▼
MCP server (FastMCP, Pi, Tailscale-only)
   │  skill routing, context loading, file tools
   ▼
Claude API (Anthropic)
   │  model: claude-haiku-4-5 (chat), claude-sonnet-4-6 (MCP clients)
   ▼
Jean-Claude skills (homeschool/skills/*.md)
   │  district-writer, lesson-planner, week-logger, mail-intake, etc.
   ▼
Private family repo  ←──  Google Drive (rclone bisync, 10min)
<private-family-repo>/                  └─ mail images, files
  homeschool/              Google Drive files folder (sync_all.py, 10min)
  jean-claude/             └─ docs/sheets → Markdown in resources/gdrive/
```

Claude Code and Claude Desktop also connect via MCP, using the same skill
files and data store.

---

## Components

### Web app
NiceGUI chat client behind Cloudflare Access. Stateless — sends full
transcript each turn. Family-facing primary interface.

### MCP server
FastMCP server on the Pi, Tailscale-only. Provides tools (chat_turn,
read_file, write_file, search_homeschool, run_validation) and resources
(status, skills, week files). Used by the web app, Claude Desktop, and
Claude Code.

### Claude Code
Interactive AI coding and task environment. Configuration in
`~/src/dotfiles/claude/.claude/`:

- `settings.json` — model, permissions, hooks, thinking enabled
- `CLAUDE.md` — user preferences

### Jean-Claude skills
Skill definitions live in `<private-family-repo>/homeschool/skills/*.md` — plain markdown,
readable by any human or LLM. Each skill contains purpose, triggers, file
ownership, domain knowledge, behavior instructions, and examples.

### Private family repo (`<private-family-repo>/`)
Canonical information store. Not public. Contains:
- Homeschool week logs, lesson plans, compliance documents
- Jean-Claude private context files (IDENTITY.md, AGENTS.md)
- Mail intake folder (images excluded from git, summaries committed)
- STATUS.md — current week, hours, open deadlines

Backed up via Google Drive (rclone bisync, 10 min) and GitHub.

---

## Data flow

**Browser → response:**
User message → web app → MCP server → Claude API + skills → response

**Mail intake:**
Phone photo → Google Drive → rclone sync → `<private-family-repo>/homeschool/mail/` →
mail-intake skill → `summary.md` committed to family repo

**Curriculum tracking:**
Google Drive files folder → sync_all.py (every 10 min) → Markdown files in
`resources/gdrive/` → available for lesson planning context.

**Logging:**
Week-logger skill → `<private-family-repo>/homeschool/weeks/week-NN.md` + STATUS.md →
committed to family repo

---

## Separation of concerns

| Layer | Location | Public |
|-------|----------|--------|
| System config (this) | `~/src/dotfiles/projects/jean-claude/` | Yes |
| Claude settings | `~/src/dotfiles/claude/` | Yes |
| Identity, private context | `<private-family-repo>/jean-claude/` | No |
| Homeschool data | `<private-family-repo>/homeschool/` | No |

Skills are public (as a pattern); the data they operate on is private.

---

## Loading this document

To give an LLM full system context, load this file alongside the private context:

```
cat ~/src/dotfiles/projects/jean-claude/README.md
cat <private-family-repo>/jean-claude/IDENTITY.md
```
