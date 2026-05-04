# dotfiles

[![secret-scan](https://github.com/brfid/dotfiles/actions/workflows/secret-scan.yml/badge.svg?branch=main)](https://github.com/brfid/dotfiles/actions/workflows/secret-scan.yml) [![markdown](https://github.com/brfid/dotfiles/actions/workflows/markdown.yml/badge.svg?branch=main)](https://github.com/brfid/dotfiles/actions/workflows/markdown.yml)

Personal config for Raspberry Pi 5, macOS, and edcloud (EC2).
Repo organized by tool.
Goal: LLM-friendly import/apply workflows with real config files backed up in repo.
Repo not full machine mirror.

## Quick start

```bash
git clone <repo> ~/src/dotfiles
# tell your LLM: "read ~/src/dotfiles/README.md and set up my dotfiles"
```

One-time setup:

```bash
cp secrets.example ~/.secrets && chmod 600 ~/.secrets   # fill in real values
cp reference/templates/.gitconfig.example ~/.gitconfig  # set name/email
```

## LLM workflow

Start at repo root.

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read target tool's `AGENTS.md` and `sync.toml`.
4. Pick smallest safe repo access mode: `local`, `temp`, or `remote`.
5. Use tool manifest to pick live action: `import`, `copy`, or `link`.

Repo stores canonical config plus agent guidance.
Repo does not try to mirror whole home dirs or runtime state.

## Machine detection

Run `uname -s` and `uname -m`.

- Darwin = macOS
- Linux + aarch64 = Pi
- Linux + x86_64 = edcloud

Skip deployment if hostname contains `edcloud` and edcloud repo already manages bootstrap.

## Config inventory

Yes: this section is meant to be clear list of what this repo maintains.
These are the main config areas and support areas.
Not every row applies on every machine.

### Live-config areas

| Path          | Typical machines           | What it holds                                              |
| ------------- | -------------------------- | ---------------------------------------------------------- |
| shell         | Pi, macOS, edcloud         | shell startup files, aliases, machine-local shell snippets |
| nvim          | most machines              | Neovim config                                              |
| tmux          | most machines              | tmux config and helper scripts                             |
| git           | most machines              | global git hook support and gitleaks config                |
| gh            | most machines              | GitHub CLI config                                          |
| claude        | machines using Claude Code | Claude Code config                                         |
| codex         | machines using Codex       | Codex CLI config                                           |
| copilot       | machines using Copilot CLI | Copilot CLI config                                         |
| vscode        | machines using VS Code     | VS Code settings and snippets                              |
| yazi          | most machines              | Yazi config                                                |
| neomutt       | Pi                         | Neomutt config                                             |
| systemd       | Pi or Linux user services  | user systemd units                                         |
| gdrive-backup | Pi                         | Google Drive backup config                                 |
| x11           | Linux desktop machines     | X11 startup glue                                           |
| iterm2        | macOS                      | iTerm2 dynamic profiles                                    |
| reference     | manual host-level work     | `/etc/` reference files, templates, host notes             |

### Support and context areas

| Path     | What it holds                                   |
| -------- | ----------------------------------------------- |
| projects | public system overviews and design/context docs |
| skills   | repo-local skill guidance                       |
| scripts  | small local automation utilities                |
| tests    | repo verification                               |
| .github  | repo-level GitHub Actions workflows             |

If a reader wants to know what config this repo maintains, the first table above is the answer.

## Override paths

Most tools go to normal XDG or dotfile locations.
Exceptions:

- **shell**
  - pi: `shell/bashrc` → `~/.bashrc`, `shell/local/pi.sh` → `~/.config/shell/local`
  - macos: `shell/zshrc` → `~/.zshrc`, `shell/local/macos.sh` → `~/.config/shell/local`
  - edcloud: `shell/bashrc` → `~/.bashrc`, `shell/local/edcloud.sh` → `~/.config/shell/local`
  - common: `shell/aliases` → `~/.config/shell/aliases`
- **tmux**: keep `~/.tmux/` real dir because TPM writes `~/.tmux/plugins/`. `tmux/tmux.conf` goes to `~/.tmux.conf`. Helper scripts go into `~/.tmux/`.
- **codex**: keep `~/.codex/` real dir. Manage only paths declared in `codex/sync.toml`. Leave auth, caches, sessions, sqlite state, and generated plugin data unmanaged.
- **gdrive-backup**: `gdrive-backup/config.toml` → `~/.config/gdrive-backup/config.toml`
- **x11**:
  - `x11/xprofile` → `~/.xprofile`
  - `x11/xinitrc` → `~/.xinitrc`
  - `x11/lxsession/LXDE-pi/autostart` → `~/.config/lxsession/LXDE-pi/autostart`
    on Raspberry Pi LXDE sessions

## Cleanup

Remove `~/.config/shell/local.d` symlink if present. Old stow artifact.

## Packages

Verify package names before install. Names drift.

### Pi (Debian/Raspberry Pi OS)

```
apt: zsh tmux eza bat yazi nodejs npm git neovim neomutt samba
npm (global, ~/.npm-global): @githubnext/github-copilot-cli
```

Set npm prefix first:

```bash
npm config set prefix ~/.npm-global
```

### macOS

```
brew: zsh tmux eza bat yazi node git neovim
npm (global, ~/.npm-global): @githubnext/github-copilot-cli
```

## `reference/` rules

`reference/` holds system configs that need sudo or host-level review.
Do not apply automatically.
For each file:

1. Show diff against current `/etc/` file.
2. Explain what change does.
3. Ask before `sudo cp`.
4. Run `sudo systemctl daemon-reload` after systemd-related changes.

Keyboard remaps for local Leopold live in `reference/linux/keyboard/`.
Install as `systemd-hwdb` rules under `/etc/udev/hwdb.d/`.
Do not rely on `~/.xprofile` or `setxkbmap` for the real machine-local fix.
On Raspberry Pi LXDE, also apply `x11/lxsession/LXDE-pi/autostart` so LXDE
does not reintroduce `setxkbmap -option ctrl:swapcaps` on login.

## Adding a tool

1. Create tool dir.
2. Put canonical config files there.
3. Add local `AGENTS.md`.
4. Add local `sync.toml`.
5. Add it to the config inventory above.
6. If path is nonstandard, document it under override paths.
7. Apply with workflow described by that tool's `AGENTS.md` and `sync.toml`.

## PII policy

Never write real names, emails, phone numbers, addresses, or account identifiers into tracked files.
Use placeholders like `<name>`, `<email>`, `<phone>`, `<address>`.
Real values belong only in `~/.secrets`.
Gitleaks hook enforces this locally. GitHub Actions secret scan enforces it in CI too.

## Layout

Most tool dirs may contain:

- real config files
- `AGENTS.md` for tool-local workflow and caveats
- `sync.toml` for managed/unmanaged paths
- optional `scripts/` for nontrivial import/apply/verify logic

```text
shell/          bashrc, zshrc, shared aliases, per-machine local snippets
nvim/           Neovim (LazyVim)
tmux/           tmux.conf and status bar scripts
git/            Git hooks, gitleaks config
gh/             GitHub CLI config
claude/         Claude Code settings, hooks, commands, plugins
codex/          Codex CLI instructions and config fragments
copilot/        GitHub Copilot CLI config
vscode/         VS Code settings and snippets
neomutt/        Neomutt (Pi only)
systemd/        User systemd services and timers (Pi only)
yazi/           Yazi file manager keybindings
iterm2/         iTerm2 profiles with light/dark colors (macOS only)
gdrive-backup/  rclone backup config (Pi only)

reference/      System configs requiring sudo — reviewed and applied manually
  linux/        /etc/ files and host-level notes: keyboard, unbound, cpufreq, lightdm, rsnapshot, samba, tailscale, etc.
  python/       Python tooling templates: Black, Flake8, mypy
  templates/    .gitconfig.example

skills/         Agent Skills-compatible repo guidance
scripts/        Small local automation utilities
projects/       Public docs for larger system setups
tests/          pytest: repo structure and syntax checks
x11/            X11 login/startx snippets
```

## edcloud

Cloud-init clones this repo into `~/src/dotfiles` during provisioning.
Dotfiles get linked or copied on first LLM session, not at boot.
On login, `~/.bashrc` sources `~/.secrets` and `shell/local/edcloud.sh`.

## Coding conventions

### Language choice

- Use bash for shell config, install scripts, and simple glue.
- Use Python when there is a choice.
- Python scripts must work with system Python unless extra deps are truly needed.
- Write tracked Markdown in CommonMark style. Use GitHub Flavored Markdown only where GitHub needs it, like tables.
- Run `scripts/check_markdown.sh` after Markdown edits.

### Python

- Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- Use Google-style docstrings on public functions, classes, and modules.
- Use type annotations on function signatures.
- Prefer `pathlib.Path` over `os.path`.
- Use `from __future__ import annotations` for forward refs.

#### Docstring format

```python
def sync(repo_dir: Path, branch: str = "main") -> None:
    """Sync a local git repo bidirectionally with its remote.

    Commits and pushes local changes, then pulls remote changes. On
    conflict, keeps ours and saves theirs with a ``_conflicted`` suffix.

    Args:
        repo_dir: Path to the local git repository.
        branch: Remote branch to sync against.

    Raises:
        SystemExit: On unrecoverable git errors.
    """
```

### Python toolchain

- **Formatter**: Black (line length 88, target Python 3.11+)
- **Linter**: Flake8 + flake8-bugbear
- **Type checker**: mypy (strict mode)
- **LSP**: pyright (strict type checking)
- **No ruff/Astral** — see design notes below

Reference configs live in `reference/python/`.
Copy `pyproject.toml` and `.flake8` into new project roots.

### Markdown

- Follow [CommonMark](https://commonmark.org/).
- Use ATX headers.
- Leave blank lines before and after lists.
- Use fenced code blocks with language identifier.
- Do not hard-wrap prose.

### Shell scripts

- Use `set -euo pipefail` in bash scripts.
- Quote variable expansions.
- Use `command -v` instead of `which`.

## Design notes

### Why Black + Flake8 + mypy, not ruff

Black + Flake8 + mypy is boring modular stack.
Each tool does one job.
Each fails separately.
Most Python devs already know it.

- **Black**: canonical formatter, deterministic, low-config
- **Flake8** + bugbear: real bug checks beyond style
- **mypy** strict: catches type drift early

### Why strict mypy

Loose typing leaks `Any` everywhere.
Strict typing gives every function a contract.
Upfront cost small. Refactor safety worth it.

### Why Python 3.11+

3.11 is common baseline across macOS and current Raspberry Pi OS.
It also gives stdlib `tomllib`, better typing, better errors.

### Why no flake8-docstrings

Docstring style lives in repo guidance and review.
`flake8-docstrings` adds noise and pushes boilerplate or broad `# noqa` use.
Not worth it here.
