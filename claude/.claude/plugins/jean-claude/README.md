# jean-claude

Claude Code plugin providing a family assistant identity and homeschool management skills.

## Skills

- **jean-claude** — activates the family assistant persona; loads identity and workspace context from a private family repo at runtime
- **district-writer** — drafts compliance documents, letters, and reports for home instruction under NY State regulation (8 NYCRR §100.10); contacts and current status loaded from private context
- **lesson-planner** — generates lesson plans and weekly objectives; learner profile and subject preferences loaded from private context
- **week-logger** — logs completed home learning sessions and updates status tracking
- **mail-intake** — processes photographed physical mail from Google Drive, writes structured summaries

## Design

Skills contain logic, format, and procedure. Personal context (contacts, learner profile, compliance status) is loaded at runtime from a private family repo via `!cat` directives. Nothing personal is hardcoded here.

## Prerequisites

- A private family repo at `~/family/` with identity and context files
- `~/family/jean-claude/IDENTITY.md`, `SOUL.md`, `CONTEXT.md`, `AGENTS.md`
- `~/family/jean-claude/learner-profile.md` — learner names, preferences, schedule
- `~/family/jean-claude/district-context.md` — district contacts and compliance calendar
