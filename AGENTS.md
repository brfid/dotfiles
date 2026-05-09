# dotfiles agent guide

Read `README.md` first.

If your client supports Agent Skills, load `skills/dotfiles-stack/SKILL.md`.

## What repo is

Repo stores canonical, human-written config plus agent guidance.
Repo is designed for LLM execution: root docs define shared policy, tool folders
define local truth, and `sync.toml` declares managed live paths.
Repo not full home-dir mirror.
Repo public. Keep secrets, auth, personal identifiers, and private machine state out of git.

## Read order

When touching one tool:

1. Read `README.md`.
2. Read this file.
3. Read `<tool>/AGENTS.md`.
4. Read `<tool>/sync.toml`.
5. Change only managed paths for that tool.

Root gives shared rules.
Tool folder gives local truth.

## Repo access modes

- `local`: repo already cloned here
- `temp`: temporary sparse/partial clone
- `remote`: direct GitHub/web/API edit for small simple repo-only changes

## Live actions

- `import`: live machine -> repo
- `copy`: repo -> live machine by copy
- `link`: repo -> live machine by symlink when user wants repo-backed live files and tool tolerates it

Pick smallest safe mode.
Prefer `local` over `temp`.
Prefer `temp` over `remote` for multi-file or validation-heavy work.
Prefer `copy` over `link` when unsure.

## Rules

- Back up real config files in repo when practical.
- Keep runtime state, auth, caches, logs, sqlite DBs, timestamps, and generated artifacts out of git unless a tool manifest marks them managed.
- Prefer changing canonical files over writing prose that only describes them.
- Keep each top-level tool folder as atomic as practical:
  - local `AGENTS.md`
  - local `sync.toml`
  - real config files
- Avoid central registries when folder convention or local manifests can carry truth.
- Do not let tests or automation convenience decide repo architecture. Design first. Tests verify.
- Do not assume one default deployment style. Use `import`, `copy`, or `link` deliberately per tool and task.
- Do not assume one default machine profile. Choose tools and variants case by case with user.
- Keep root-owned files and host notes under `reference/linux/`.
- Preserve unrelated user changes already present in repo.
- Run `pytest` plus tool-specific checks before claiming done.
- Run `scripts/check_secrets.sh` or rely on the GitHub Actions secret-scan workflow when changing files that may touch secrets policy.
- Keep tracked Markdown in CommonMark style with GFM only where repo needs GitHub tables/task lists. Run `scripts/check_markdown.sh` after Markdown edits.

## Bigger repo changes

For larger additions or restructures:

- Fresh LLM should be able to cold-start from repo root and keep going.
- Root should explain shared philosophy, not duplicate every tool contract.
- Tool folders should point back here for context, not depend on hidden metadata elsewhere.
- Prefer boring portable formats: Markdown, TOML, shell, Python stdlib.
- When tool mixes config and runtime state, make boundary explicit.
- If a useful durable rule appears in discussion, write it here or in the tool folder. Do not leave it only in chat history.

## Migration note

Repo is still moving folder by folder to:

- `AGENTS.md`
- `sync.toml`

Legacy folders may not have both yet. Keep changes narrow. If you add a new boundary, document it in the folder.
