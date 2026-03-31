---
name: lesson-planner
description: >
  Generate daily lesson plans, weekly objectives, or activity sequences for
  the homeschool. 12 required subjects, 15-20 min blocks, outdoor and
  hands-on first.
argument-hint: '[week number or topic]'
---

# Lesson Planner

## Learner Profile

!`cat ~/family/jean-claude/learner-profile.md`

## Format

Follow the canonical week file structure defined in
`~/family/homeschool/weeks/_week-template.md`. Read that file before
generating or editing any week plan.

## Generating a New Week File

Create `~/family/homeschool/weeks/week-NN.md` with:

1. Week header: title, date range, theme, goal, optional note.
2. For each weekday (Day 1–5):
   - `## [Weekday], [Month DD] — Day [N]`
   - `### Log` section with `**Status:** Pending` and a `---` separator
   - `### Plan` section with `#### Morning` and `#### Afternoon` blocks
3. Weekend section (optional activities).
4. Materials needed section.
5. Empty hour log table.

## Adding Plans Mid-Week

If the week file already exists with some days logged, only add or modify
plan sections for days that haven't happened yet. Do not touch logged days.

## Design Principles

- **Ordered lists, not timed schedules.** Daily plans are numbered sequences. Time is flexible.
- **15–20 min blocks.** If engaged, let it run. If not, move on.
- **Outdoor and hands-on first.** The natural environment is the primary classroom.
- **Themes.** Thread the learner's interests through all subjects each week.
- **Prefer offline.** Minimal screen time. Printables and real objects over apps.
- **Use free resources.** EngageNY, library, printables, property.

## Required Subjects (12)

Arithmetic, Reading, Spelling, Writing/English, Geography, US History, Science,
Health, Music, Visual Arts, Physical Education, plus any enrichment tracks
defined in the learner profile.

## Activity Entry Format

Each activity should include:

- What the learner does
- Any sibling parallel tracks as defined in the learner profile
- Subjects covered in italics, e.g. *(reading, writing, social studies)*
- Materials if non-obvious

## What to Omit from Plans

Do not include:
- Snack breaks or movement breaks as standalone items
- "Free time" items

## Week Detail Levels

- **Weeks 1–4:** Full daily activity sequences with parallel tracks, materials, and subject tags.
- **Weeks 5–13:** Weekly objectives and daily suggestions. Parents can request expansion.

## Subjects

Use lowercase, comma-separated. Canonical list: arithmetic, reading, spelling,
writing, geography, US history, science, health, music, visual arts, PE,
social-emotional, orientation.
