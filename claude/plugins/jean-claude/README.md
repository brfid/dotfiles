# jean-claude

A Claude Code plugin that implements a family assistant with structured skills
for homeschool management. Companion to a private family data repo at `~/family/`.

## What it is

Jean-Claude is a persistent family assistant built on Claude Code's skill and
plugin system. It handles homeschool lesson planning, session logging, compliance
documentation, mail intake, and book tracking — with all family-specific data
kept in a separate private repo.

The plugin is the routing and interface layer. The family repo is the data and
canonical skill content layer. Nothing personal lives here.

## Architecture

```
~/.claude/plugins/jean-claude/    ← this repo (public)
  skills/
    week-logger/SKILL.md          ← thin wrapper: triggers routing, delegates to ↓
    lesson-planner/SKILL.md
    district-writer/SKILL.md
    mail-intake/SKILL.md
    books/SKILL.md
    jean-claude/SKILL.md

~/family/jean-claude/             ← private family repo
  IDENTITY.md                     ← who Jean-Claude is
  AGENTS.md                       ← conventions, file ownership, skill routing
  CONTEXT.md                      ← navigation map of the information store
  skills/
    week-logger/SKILL.md          ← canonical skill content (family-specific)
    lesson-planner/SKILL.md
    ...

~/family/homeschool/              ← information store (private)
  STATUS.md                       ← current week, compliance tasks, notes
  books/{active,done,night,want}/ ← one file per book
  weeks/week-NN.md                ← daily lesson logs
  compliance/                     ← district documents
  resources/                      ← activity ideas, materials, reference
```

Each plugin skill file contains only frontmatter (for routing) and a single
`!cat` directive that loads the canonical content from the family repo at
runtime. This keeps the plugin clean and the family repo the single source of
truth.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `jean-claude` | Being addressed as "Jean-Claude", any family task | Loads full persona: identity, workspace map, conventions |
| `week-logger` | "log today", "we did X", any session account | Records the day's session, updates hours and status, captures book progress and activity ideas |
| `lesson-planner` | "plan next week", "what should we do Wednesday" | Generates lesson plans; rolls over the previous week before creating a new one |
| `district-writer` | "write a letter to the district", "draft the quarterly report" | Drafts compliance documents; updates the communications log |
| `mail-intake` | "process the mail", "there's new mail in Drive" | Reads photographed mail from Google Drive, writes structured summaries, surfaces deadlines |
| `books` | "we started X", "we finished X", "add X to the reading list" | Tracks school reading, night reading, and wishlist; one file per book |

## Design principles

**Skills declare file ownership.** Each skill documents which files it writes
and which sections it owns. Co-owned files (like week logs, where lesson-planner
owns plans and week-logger owns logs) have explicit non-overlap rules.

**Filesystem as state.** Book status is encoded in folder location
(`active/`, `done/`, `night/`, `want/`) rather than a status field. Moving a
file is the state transition. `ls done/` gives a clean reading record for
compliance reports with no parsing.

**One source of truth per fact.** Operational state lives in `STATUS.md`.
Compliance tasks live in `STATUS.md` (human-managed section). Book records live
in `books/`. Nothing is duplicated.

**Agents read everything, write only what they own.** Files without a skill
owner are human-authored reference documents — readable by any agent but not
writable without an explicit user request.

## Entry points

Jean-Claude runs in three environments with different skill activation behavior.

### Claude Code (CLI or IDE)
The `jean-claude` plugin loads via `settings.json`. Skills auto-activate as
slash commands — when Claude sees a routing trigger, the plugin skill file
loads automatically via the plugin system.

Entry: `/jean-claude` slash command, or the `jean-claude` plugin skill.

### OpenClaw (Telegram)
OpenClaw is a Telegram-to-Anthropic-API gateway, running as a pair of systemd
services with a working directory at `~/.openclaw/workspace/`. The workspace
`AGENTS.md` defers to `~/family/AGENTS.md` for the Jean-Claude persona and
skill routing.

There is no plugin system here. Claude reads skill files manually via file
tools when a routing trigger is matched. The routing table in
`~/family/jean-claude/AGENTS.md` includes file paths alongside skill names for
this reason — both environments can follow the same table.

Entry: Telegram messages to the family bot.

### Claude Desktop
When pointed at `~/family/`, `CLAUDE.md` loads and the full context is
available. Skills are read manually the same way as OpenClaw. MCP servers are
the Desktop-native extension mechanism if structured activation is needed.

Entry: Claude Desktop with working directory set to `~/family/`.

---

## Adapting this

To use this pattern for your own family:

1. Fork or copy this plugin structure.
2. Create a private `~/family/` repo with the same layout.
3. Write your own canonical skill content in `~/family/jean-claude/skills/`.
4. Update the `!cat` paths in the plugin wrappers if your repo lives elsewhere.
5. Populate `~/family/homeschool/` with your information store.

The plugin wrappers need no changes as long as your canonical skills live at
`~/family/jean-claude/skills/[skill-name]/SKILL.md`.
