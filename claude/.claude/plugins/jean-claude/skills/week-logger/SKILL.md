---
name: week-logger
description: >
  Use this skill any time someone says "log today", "record what happened",
  "we did X today", or gives any account of a completed home learning session.
  Writes to ~/family/homeschool/weeks/week-NN.md and updates STATUS.md.
argument-hint: '[day or week summary]'
---

# Week Logger

## Learner Profile

!`cat ~/family/jean-claude/learner-profile.md`

## Format

Follow the canonical week file structure defined in
`~/family/homeschool/weeks/_week-template.md`. Read that file before
editing any week log.

## Before You Write Anything: Get a Good Account

If the user's summary is thin (e.g. "we did reading and math today"), ask
before writing. A log written from sparse input is useless for planning and
compliance. Ask what you need — but don't pepper them with a list. Read what
they gave you and ask only for what's actually missing.

Questions that surface useful detail:

- **What was the learner's energy/mood like?** Any friction, resistance, or
  breakthroughs? Distress or excitement?
- **Walk me through what you actually did** — in order, not what was planned.
- **Did anything surprise you** — something said, noticed, or absorbed in?
- **What got skipped or changed** from the plan, and why?
- **How long?** Morning block hours + afternoon block hours.

If the user gives a rich, detailed account, structure it directly.

**Never invent detail.** A short honest entry is better than a padded one.

## Where to Write

- **Week logs:** `~/family/homeschool/weeks/week-NN.md`
- **Status:** `~/family/homeschool/STATUS.md` — update after logging

Check `~/family/homeschool/STATUS.md` for the current week number.

## How to Log a Day

1. Open the week file and find the day heading: `## [Weekday], [Month DD] — Day [N]`
2. Find the `### Log` section with `**Status:** Pending`.
3. Replace it:

```markdown
### Log
**Status:** Logged
**Engagement:** [sustained | mixed | disengaged | went deep]

- [what happened — specific, not generic]
- [what the learner said, noticed, or got absorbed in]
- [what was skipped or changed from the plan, and why]
- [anything that should inform future planning]

**Subjects:** [comma-separated lowercase]
**Hours:** [X morning + Y afternoon = Z total]
```

4. If the plan was not followed, annotate: `### Plan *(not followed — reason)*`
5. Update the hour log table at the bottom of the file.
6. Update `~/family/homeschool/STATUS.md`: hours total, and any notes that
   change the operational picture.

## What Makes a Log Entry Good

**Good:** "Resisted the writing activity initially — said they didn't know what
to write. Parent modeled one sentence and they wrote two more on their own.
Ended up proud. Pattern: lower the activation energy, then step back."

**Too thin:** "Did some writing. It went okay."

**Good:** "Pivoted away from the map activity — got visibly distressed when the
drawing didn't look right. Switched to Lego. Note: mapping needs a smaller
scaffold — maybe start with one room."

**Too thin:** "Skipped the map. Did Lego instead."

## If a Day Was Skipped

```markdown
### Log
**Status:** Skipped — [reason]
```

Annotate the plan: `### Plan *(not followed — [reason])*`

## Subjects

Use lowercase, comma-separated. Canonical list: arithmetic, reading, spelling,
writing, geography, US history, science, health, music, visual arts, PE,
social-emotional, orientation.
