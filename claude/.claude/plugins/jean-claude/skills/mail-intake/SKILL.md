---
name: mail-intake
description: >
  Process physical mail that has been photographed and uploaded to Google Drive.
  Converts images, analyzes content, and writes a structured summary into the
  homeschool/mail/ folder. Surfaces any deadlines explicitly.
argument-hint: '[optional: describe the mail batch if known]'
---

# Mail Intake

## Trigger phrases

"deal with the mail", "process the mail", "intake the mail", "there's new mail
in drive", or any similar phrasing indicating uploaded mail images are waiting.

## Infrastructure

- Google Drive syncs bidirectionally with `~/family/` every 10 minutes via rclone.
- Images uploaded to Drive at `family/homeschool/mail/` arrive automatically at
  `~/family/homeschool/mail/` after the next sync cycle.
- Do not assume images are present until the sync has run. If the user just
  uploaded, wait or ask them to confirm the sync has completed.

## Procedure

### 1. Find unprocessed images

Look in `~/family/homeschool/mail/` for image files at the root level (not yet
organized into a dated subfolder). Supported formats: HEIC, HEIF, JPG, JPEG,
PNG, PDF.

If nothing is found, tell the user and stop.

### 2. Convert if needed

HEIC/HEIF files must be converted to JPG. Use pillow-heif:

```python
from pillow_heif import register_heif_opener
from PIL import Image
register_heif_opener()
img = Image.open("input.HEIC")
img.save("output.jpg", "JPEG", quality=85)
```

Write the JPG alongside the original. After confirming it is readable, delete
the HEIC original. Image files are never committed to git.

### 3. Analyze

Read all images in the batch together. Identify:
- Sender (person, organization, government agency)
- Date on the document (not today's date)
- Document type (letter, policy, form, notice, etc.)
- Key facts and any deadlines (extract exact date and what is due)

### 4. Confirm folder name

Propose a slug: `YYYY-MM-DD_sender-topic`. Ask the user to confirm before
creating anything.

### 5. Write summary

Create `~/family/homeschool/mail/YYYY-MM-DD_sender-topic/summary.md`:

```markdown
---
sender: [full sender name]
date: YYYY-MM-DD
type: [letter | policy | notice | form | other]
subjects: [comma-separated topics]
deadlines:
  - date: YYYY-MM-DD
    item: [what is due]
---

## Summary

[2–4 sentence plain-language summary.]

## Key facts

- [Bullet list of material facts]

## Deadlines

[Prose deadline list. If none, write "None identified."]

## Action items

- [ ] [Specific thing to do, with deadline if applicable]
```

### 6. Surface deadlines

After writing, explicitly call out any deadlines in your chat response:

> **Deadline:** [what is due] — [date]

### 7. Only summary.md is committed

Image files are never committed to git. The `homeschool/mail/.gitignore`
excludes all image formats.
