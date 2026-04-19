# dotfiles

Personal configuration for a Raspberry Pi 5, macOS, and edcloud (EC2). Organized by tool, deployed by LLM agent via symlinks.

To deploy on a new machine:

```bash
git clone <repo> ~/src/dotfiles
# tell your LLM: "read ~/src/dotfiles/README.md and set up my dotfiles"
```

One-time setup (not automated):

```bash
cp secrets.example ~/.secrets && chmod 600 ~/.secrets   # fill in real values
cp reference/templates/.gitconfig.example ~/.gitconfig  # set name/email
```

## Machine detection

Run `uname -s` and `uname -m`:

- Darwin = macOS
- Linux + aarch64 = Pi
- Linux + x86_64 = edcloud

Skip deployment if hostname contains `edcloud` and the edcloud repo manages its own bootstrap.

## Profiles

Each tool directory is symlinked to its standard config location. Install `common` plus the matching machine profile.

| Tool | common | pi | macos | edcloud | Description |
|------|--------|----|-------|---------|-------------|
| shell | ✓ | ✓ | ✓ | ✓ | bashrc/zshrc, shared aliases, per-machine local snippets |
| nvim | ✓ | | | | Neovim (LazyVim) |
| tmux | ✓ | | | | tmux.conf and status bar scripts |
| git | ✓ | | | | Git hooks, gitleaks config |
| gh | ✓ | | | | GitHub CLI config |
| claude | ✓ | | | | Claude Code settings, commands, plugins |
| copilot | ✓ | | | | GitHub Copilot CLI config |
| vscode | ✓ | | | | VS Code settings and snippets |
| yazi | ✓ | | | | Yazi file manager keybindings |
| neomutt | | ✓ | | | Neomutt mail client |
| systemd | | ✓ | | | User systemd services and timers |
| gdrive-backup | | ✓ | | | rclone backup config |

## Overrides

Most tools install to their standard XDG or dotfile location (e.g. `nvim/` → `~/.config/nvim`). These are the exceptions:

- **shell**: Each profile sources a different rc file and machine-local snippet.
  - pi: `shell/bashrc` → `~/.bashrc`, `shell/local/pi.sh` → `~/.config/shell/local`
  - macos: `shell/zshrc` → `~/.zshrc`, `shell/local/macos.sh` → `~/.config/shell/local`
  - edcloud: `shell/bashrc` → `~/.bashrc`, `shell/local/edcloud.sh` → `~/.config/shell/local`
  - common: `shell/aliases` → `~/.config/shell/aliases`
- **tmux**: `~/.tmux/` must be a real directory (tpm installs plugins into `~/.tmux/plugins/`). Symlink `tmux/tmux.conf` → `~/.tmux.conf`, then each script in `tmux/scripts/` individually into `~/.tmux/` (e.g. `~/.tmux/cpu.sh`). Do not symlink the scripts directory itself.
- **gdrive-backup**: `gdrive-backup/config.toml` → `~/.config/gdrive-backup/config.toml`

## Cleanup

Remove `~/.config/shell/local.d` symlink if present (stow migration artifact).

## Packages

Verify current package names before installing — they drift between OS versions.

### Pi (Debian/Raspberry Pi OS)

```
apt: zsh tmux eza bat yazi nodejs npm git neovim neomutt samba
npm (global, ~/.npm-global): @githubnext/github-copilot-cli
```

Set npm prefix before installing: `npm config set prefix ~/.npm-global`

### macOS

```
brew: zsh tmux eza bat yazi node git neovim
npm (global, ~/.npm-global): @githubnext/github-copilot-cli
```

## reference/ — system configs requiring sudo

Do not apply automatically. For each file:

1. Show a diff between the repo file and the current `/etc/` version.
2. Explain what the change does.
3. Ask for confirmation before `sudo cp`.
4. Run `sudo systemctl daemon-reload` after applying systemd-related changes.

Keyboard remaps for the local Leopold live in
`reference/linux/keyboard/`. Install them as `systemd-hwdb` rules under
`/etc/udev/hwdb.d/`; do not rely on `~/.xprofile`/`setxkbmap` for the real
machine-local fix.

## Adding a new tool

1. Create a directory named after the tool with its config files inside.
2. Add it to the profile table above.
3. If the install location isn't the standard XDG/dotfile convention, add an entry under Overrides.
4. Create the symlink on the current machine.

## PII policy

Never write real names, emails, phone numbers, addresses, or account identifiers into tracked files. Use placeholders: `<name>`, `<email>`, `<phone>`, `<address>`. Real values belong only in `~/.secrets` (untracked). The gitleaks pre-commit hook (`git/.gitleaks.toml`) enforces this at commit time.

## Layout

```
shell/          bashrc, zshrc, shared aliases, per-machine local snippets
nvim/           Neovim (LazyVim)
tmux/           tmux.conf and status bar scripts
git/            Git hooks, gitleaks config
gh/             GitHub CLI config
claude/         Claude Code settings, commands, plugins
copilot/        GitHub Copilot CLI config
vscode/         VS Code settings and snippets
neomutt/        Neomutt (Pi only)
systemd/        User systemd services and timers (Pi only)
yazi/           Yazi file manager keybindings
iterm2/         iTerm2 profiles with light/dark colors (macOS only)
gdrive-backup/  rclone backup config (Pi only)

reference/      System configs requiring sudo — reviewed and applied manually
  linux/          /etc/ files and host-level notes: keyboard, unbound, cpufreq, lightdm, rsnapshot, samba, tailscale, etc.
  python/         Python tooling templates: Black, Flake8, mypy
  templates/      .gitconfig.example

skills/         Agent Skills-compatible repo guidance
scripts/        Small local automation utilities
projects/       Public docs for larger system setups
tests/          pytest: profile table coverage, bash syntax
x11/            X11 login/startx snippets
```

## edcloud

During provisioning, cloud-init clones this repo into `~/src/dotfiles`. Dotfiles are linked on first LLM session, not at boot. On each login, `~/.bashrc` sources `~/.secrets` and `shell/local/edcloud.sh`.

## Coding conventions

### Language choice

- Use bash for shell configuration, install scripts, and simple glue.
- Use Python when there is a choice between languages.
- Python scripts must work with the system Python (no external dependencies unless unavoidable).

### Python

- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- Use Google-style docstrings on all public functions, classes, and modules.
- Use type annotations on function signatures.
- Prefer `pathlib.Path` over `os.path`.
- Use `from __future__ import annotations` for forward references.

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
- **No ruff/Astral** — see Design Decisions below

Reference configs live in `reference/python/`. Copy `pyproject.toml` and `.flake8` into new project roots.

### Markdown

- Follow [CommonMark](https://commonmark.org/) spec.
- Use ATX headers (`#`, `##`) instead of bold text for sections.
- Leave a blank line before and after lists.
- Use fenced code blocks with a language identifier.
- Do not hard-wrap prose. Let the editor or viewer handle line wrapping.

### Shell scripts

- Use `set -euo pipefail` in bash scripts.
- Quote all variable expansions.
- Use `command -v` instead of `which`.

## Design decisions

### Why Black + Flake8 + mypy (not ruff)

Ruff collapses formatting, linting, and some type-checking into one tool with its own rule semantics. Black + Flake8 + mypy is the established, modular stack:

- **Black** is the canonical Python formatter. Zero config, deterministic, widely understood.
- **Flake8** with flake8-bugbear catches real bugs (B-series) beyond style. Plugin ecosystem is mature.
- **mypy** in strict mode is the reference type checker. Strict means: no implicit `Any`, no untyped defs, no missing return types.

Each tool does one thing. They compose cleanly, fail independently, and are understood by every Python developer.

### Why strict mypy

Gradual typing with `strict = false` means half the codebase has `Any` leaking through, and mypy only catches errors in the parts you remembered to annotate. Strict from the start means every function has a contract. The upfront cost is small; the long-term benefit is that refactoring is safe.

### Why Python 3.11+

3.11 is the minimum supported version across both macOS (Homebrew) and Raspberry Pi OS (Debian Bookworm ships 3.11). Using 3.11+ means: `tomllib` in stdlib, exception groups, `Self` type, and fine-grained error locations.

### Why no flake8-docstrings

Docstring conventions (Google style) are documented here and enforced by review, not by linter. `flake8-docstrings` (pydocstyle) produces noisy false positives on helper functions and test code, encouraging either boilerplate docstrings or per-file `# noqa` blankets. Neither outcome improves code quality.
