# dotfiles agent guide

LLM-driven config repo. Two workflows:

1. **Tool update** — edit canonical files in one tool folder, sync to
   the live machine.
2. **Full rebuild** — repave a fresh pi or edcloud from this repo.

Repo is public. Keep secrets, auth tokens, identifiers, and
machine-local state out of git.

## Read order

1. `README.md` (orientation).
2. This file.
3. `<tool>/AGENTS.md` if present.
4. `<tool>/sync.toml`.
5. For host-level work: `reference/<host>.md` (`pi.md`, `edcloud.md`).
6. Change only `[[managed]]` paths for that tool.

## sync.toml schema (v2)

Schema: `version = 2`, `tool = "<dirname>"`, `live_root`, and one or
more `[[managed]]` entries with `name`, `repo`, `live`. No `actions`,
no `[[unmanaged]]`, no `[[verify]]` — v2 trusts the agent to pick copy
vs. symlink, ignore obvious runtime state (history, caches, sqlite,
lockfiles), and verify what it just did. `scripts/validate.py` enforces
the schema; existing `*/sync.toml` files are the canonical examples.

## Override paths

Most tools use XDG defaults declared in `sync.toml`. Non-obvious cases:

- **shell** — `bashrc` → `~/.bashrc`; `zshrc` → `~/.zshrc` (macOS only,
  ad hoc); shared `profile` and `aliases` go to `~/.config/shell/` and
  are sourced by both.
- **git** — set `core.hooksPath` once per machine:
  `git config --global core.hooksPath ~/.config/git/hooks`.
- **tmux** — keep `~/.tmux/` a real dir (TPM writes
  `~/.tmux/plugins/`). `tmux.conf` → `~/.tmux.conf`; helper scripts
  → `~/.tmux/`.
- **codex** — keep `~/.codex/` a real dir (auth, sessions, sqlite,
  plugin payloads live there). Manage only paths in `codex/sync.toml`.
- **x11** — `xprofile` → `~/.xprofile`, `xinitrc` → `~/.xinitrc`,
  `lxsession/LXDE-pi/autostart` → `~/.config/lxsession/LXDE-pi/autostart`
  on Raspberry Pi LXDE sessions.

## Host-level work

Host docs and `/etc/` references live in `reference/`. See
`reference/AGENTS.md` for apply rules; `reference/pi.md` and
`reference/edcloud.md` for per-host facts.

## Rules

- Keep runtime state (auth, caches, logs, sqlite, history, generated
  artifacts) out of git.
- Prefer changing canonical files over writing prose that describes
  them.
- Each top-level tool folder is atomic: real config files, optional
  `AGENTS.md`, mandatory `sync.toml`. No central registries.
- Host-level `/etc/` files go under `reference/linux/<service>/`;
  per-host notes go in `reference/<host>.md`.
- Preserve unrelated user changes already in the repo.
- Run `python scripts/validate.py` before claiming done.
- Markdown is CommonMark with GFM only where GitHub needs it (tables,
  task lists). Soft-wrap prose paragraphs.
- Never write real names, emails, phone numbers, addresses, or account
  IDs into tracked files. Use placeholders (`<name>`, `<email>`,
  `<lan_ip>`). Real values belong in `~/.secrets`. The gitleaks
  pre-commit hook enforces secret patterns locally.
- Commit routine updates on local `main` and push to `origin main`
  after `validate.py` passes. No PRs unless asked.
