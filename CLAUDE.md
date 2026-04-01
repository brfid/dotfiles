# Dotfiles

Personal system configuration repo, deployed with GNU Stow. See `AGENTS.md` for coding conventions.

## Structure

```
packages/       Stow packages — symlinked into $HOME via `stow <package>`
reference/      Reference configs — copied manually, not stow-managed
  linux/        /etc/ configs (unbound, cpufreq, rsnapshot, lightdm, logrotate)
  macos/        macOS app preferences (applied via scripts/PlistBuddy)
  python/       Python tooling config templates (Black, Flake8, mypy)
  templates/    .gitconfig.example template
projects/       Project glue — documentation and bootstrap for external projects
  jean-claude/  System overview for the Jean-Claude family assistant
  openclaw/     OpenClaw bootstrap script for Telegram agent
scripts/        Google Drive backup wrapper, Signal CLI setup
tests/          pytest suite (bash syntax, stow structure, gdrive_backup)
```

`.stowrc` sets `--dir=packages --target=~`, so `stow <package>` works from the repo root.

## Key details

- Machine-local secrets go in `~/.secrets` (created from `secrets.example`; not committed)
- Per-machine shell config: symlink the appropriate file from `packages/shell/.config/shell/local.d/` to `~/.config/shell/local`
- `edcloud` repo has its own `scripts/setup-dotfiles.sh` that runs stow for its machine
