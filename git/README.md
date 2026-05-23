# git

Global git preferences are limited to ignores, gitleaks rules, and an optional pre-commit hook.

Live paths:
- `ignore` -> `~/.config/git/ignore`
- `.gitleaks.toml` -> `~/.config/git/.gitleaks.toml`
- `hooks/pre-commit` -> `~/.config/git/hooks/pre-commit`

Notes:
- Enable the hook with `git config --global core.hooksPath ~/.config/git/hooks`.
- The hook blocks commits when `gitleaks` is unavailable; keep it optional on new machines.
