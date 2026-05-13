# dotfiles

Personal-machine config repo for two Linux hosts:

- **pi** — Raspberry Pi 5 home server (Debian/Raspberry Pi OS). See
  `reference/pi.md`.
- **edcloud** — EC2 cloud workstation, provisioned by cloud-init from
  [`brfid/edcloud`](https://github.com/brfid/edcloud). See
  `reference/edcloud.md`.

Scope is broader than just `~/` dotfiles: each top-level folder owns the
canonical files for one tool, plus host-level `/etc/` references and
per-host notes under `reference/`. macOS hosts can borrow individual
configs ad hoc but are not a managed install target.

## Layout

| Path        | Holds                                                        |
| ----------- | ------------------------------------------------------------ |
| `shell/`    | bash and zsh startup, shared `profile`, aliases              |
| `nvim/`     | LazyVim base plus local overrides                            |
| `tmux/`     | tmux config and status-line helper scripts                   |
| `git/`      | global pre-commit hook, gitleaks config, ignore              |
| `gh/`       | GitHub CLI config                                            |
| `claude/`   | Claude Code settings and `CLAUDE.md`                         |
| `codex/`    | Codex CLI config, instructions, rules, memories              |
| `opencode/` | opencode config                                              |
| `yazi/`     | Yazi file manager config                                     |
| `neomutt/`  | Neomutt config (pi only)                                     |
| `systemd/`  | user systemd units                                           |
| `alacritty/`| Alacritty terminal config (Linux desktop)                    |
| `x11/`      | X11 startup glue (Linux desktop)                             |
| `reference/`| host docs (`pi.md`, `edcloud.md`), `/etc/` files, templates  |
| `scripts/`  | `validate.py` and small utilities                            |

Each tool folder has a `sync.toml` declaring which files map where.
`scripts/validate.py` enforces the schema.

## Quick start

```bash
git clone git@github.com:brfid/dotfiles.git ~/src/dotfiles
cp ~/src/dotfiles/reference/templates/.gitconfig.example ~/.gitconfig
cp ~/src/dotfiles/secrets.example ~/.secrets && chmod 600 ~/.secrets
```

Then point an LLM agent at `~/src/dotfiles/AGENTS.md` to install or
update configs. Real secrets live in `~/.secrets`, never in the repo.

## Packages (pi)

Verify names before install; they drift.

```
apt: zsh tmux eza bat yazi git neovim neomutt samba
brew: bun
```

edcloud installs are driven by its own cloud-init; this repo does not
bootstrap it. See `reference/edcloud.md` for the contract.

Pi-specific host setup (keyboard remap, Pi-hole, Tailscale, Unbound,
Samba) lives in `reference/pi.md`.
