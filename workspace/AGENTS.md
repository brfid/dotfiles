# workspace agent guide

## Purpose

This folder records core rebuild resources: repos needed to rebuild a local
working environment after reinstall or repave.

This is not a full repo inventory.

## Read first

- `README.md`
- `repos.toml`

## Privacy and visibility

- GitHub repo visibility is the source of truth for public/private handling.
- Do not duplicate repo visibility in `repos.toml`.
- If visibility matters, check GitHub with
  `gh repo view brfid/<repo> --json visibility`.
- If visibility cannot be checked, treat the repo as private.
- Do not copy private repo contents into this public dotfiles repo.
- Public repos still must not receive secrets, credentials, PII, private notes,
  or machine-local state.

## Registry rules

- Keep `repos.toml` minimal: name, URL, expected local path, purpose.
- Use `~/src/<repo>` as the expected local path unless a repo has a deliberate
  exception.
- Do not add every repo. Add only repos that matter for rebuilding the local
  environment.
- Prefer GitHub SSH URLs for repos under `github.com/brfid`.
