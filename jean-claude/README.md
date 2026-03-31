# Jean-Claude

Jean-Claude is a personal AI assistant built for a homeschooling family. It runs
on a Raspberry Pi, reaches the family through Telegram, and is managed day-to-day
through Claude Code on the same machine.

This document describes the overall system. It is intended to be read by humans
and loaded as context by LLMs working within the setup.

---

## What it does

- Answers questions and handles tasks over Telegram (voice and text)
- Manages a structured homeschool: lesson planning, daily logging, compliance
  reporting, and hour tracking
- Processes physical mail (photographed → Drive → summarised with deadlines)
- Syncs a Google Sheets curriculum tracker to local Markdown
- Drafts formal communications to the school district

---

## Architecture

```
Telegram
   │
   ▼
OpenClaw gateway (systemd daemon, Raspberry Pi)
   │  session management, context pruning, retry logic
   ▼
Claude API (Anthropic)
   │  model: claude-sonnet-4-6
   ▼
Jean-Claude skills (Claude Code plugin, this repo)
   │  district-writer, lesson-planner, week-logger, mail-intake
   ▼
Private family repo  ←──  Google Drive (rclone bisync, 10min)
~/family/                  └─ mail images, curriculum sheets
  homeschool/              Google Sheets (sync script, 12hr)
  jean-claude/             └─ curriculum tracker → Markdown
```

Claude Code on the Pi is also used directly (interactive sessions) with the same
jean-claude plugin active — so the same skills work both from Telegram and from
the terminal.

---

## Components

### OpenClaw
Runtime daemon that connects Claude API to messaging channels. Handles session
lifecycle, context pruning, and retry/backoff. Configured via
`~/src/dotfiles/openclaw/setup.sh`.

Channels: Telegram (primary). Session resets daily at 04:00 and after 30 minutes
idle. Context pruned on a cache-TTL strategy, keeping the last 3 assistant turns.

### Claude Code
Interactive AI coding and task environment. Configuration in
`~/src/dotfiles/claude/.claude/`:

- `settings.json` — model, permissions, hooks (black formatter on save),
  thinking enabled, effortLevel medium
- `CLAUDE.md` — user preferences: Google developer docs style, concise,
  Context7 for library docs
- Memory system at `~/.claude/projects/` — auto-persisted across sessions

### Jean-Claude plugin
Claude Code plugin (`~/src/dotfiles/claude/.claude/plugins/jean-claude/`)
providing the assistant identity and skills. Skills contain logic and structure
only — personal context (learner profile, district contacts, compliance calendar)
is loaded at runtime from the private family repo via `!cat` directives. Nothing
personal is hardcoded here.

Skills:
- **jean-claude** — activates the persona; loads identity, soul, and workspace
  map from the private repo
- **district-writer** — compliance documents and letters under 8 NYCRR §100.10
- **lesson-planner** — weekly and daily lesson plans; learner profile injected
  at runtime
- **week-logger** — logs completed sessions, updates STATUS.md and hour totals
- **mail-intake** — processes Drive-synced mail images, writes structured
  summaries with deadlines

### Private family repo (`~/family/`)
Canonical information store. Not public. Contains:
- Homeschool week logs, lesson plans, compliance documents
- Learner profile, district context, compliance calendar
- Jean-Claude identity files (IDENTITY.md, SOUL.md, CONTEXT.md, AGENTS.md)
- Mail intake folder (images excluded from git, summaries committed)
- STATUS.md — current week, hours, open deadlines

Backed up daily via git push (cron, 02:00). Google Drive syncs bidirectionally
via rclone every 10 minutes.

---

## Data flow

**Telegram → response:**
User message → OpenClaw → Claude API + skills → response

**Mail intake:**
Phone photo → Google Drive → rclone sync → `~/family/homeschool/mail/` →
mail-intake skill → `summary.md` committed to family repo

**Curriculum tracking:**
Google Sheets → sync script (06:00, 18:00) → Markdown files in family repo →
available for lesson planning context

**Logging:**
Week-logger skill → `~/family/homeschool/weeks/week-NN.md` + STATUS.md →
committed to family repo nightly

---

## Separation of concerns

| Layer | Location | Public |
|-------|----------|--------|
| System config (this) | `~/src/dotfiles/jean-claude/` | Yes |
| Claude settings, skills | `~/src/dotfiles/claude/` | Yes |
| OpenClaw setup | `~/src/dotfiles/openclaw/` | Yes |
| Identity, persona, context | `~/family/jean-claude/` | No |
| Homeschool data | `~/family/homeschool/` | No |

Skills are public; the data they operate on is private.

---

## Loading this document

To give an LLM full system context, load this file alongside the private context:

```
!`cat ~/src/dotfiles/jean-claude/README.md`
!`cat ~/family/jean-claude/CONTEXT.md`
```

Or reference it on demand — skills don't load this automatically.
