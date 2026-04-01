# Deployment

This repo is deployed by an LLM agent. See `mapping.yaml` for the full
source-to-target symlink map. This section covers everything else the agent
needs to know.

## How to deploy

1. Read `mapping.yaml`. It has `common`, `pi`, and `macos` profiles.
2. Run `uname -s` (Darwin = macOS, Linux = Pi) and `uname -m` (aarch64 = Pi).
3. Create symlinks for `common` + the matching machine profile.
   - Use `ln -sfn <abs-source> <abs-target>`. Create parent dirs as needed.
   - Check existing symlinks first — only update if wrong or missing.
   - Report what you changed.
4. Remove `~/.config/shell/local.d` symlink if present (stow migration artifact).

Skip everything if hostname contains `edcloud` — it manages its own dotfiles.

## Package installation

Verify current package names before installing — they drift between OS versions.

### Pi (Debian/Raspberry Pi OS)

```
apt: zsh tmux eza bat yazi nodejs npm git neovim neomutt
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

## One-time manual steps

These are intentionally not automated:

```bash
cp secrets.example ~/.secrets && chmod 600 ~/.secrets   # fill in real values
cp reference/templates/.gitconfig.example ~/.gitconfig  # set name/email
```

## tmux status scripts

Scripts in `tmux/scripts/` (cpu.sh, ram.sh, etc.) are symlinked individually into
`~/.tmux/` (e.g. `~/.tmux/cpu.sh`). Do not symlink the whole directory — `~/.tmux/`
must remain a real directory because tpm installs plugins into `~/.tmux/plugins/` at
runtime.

---

# Coding conventions

## Language choice

- Use bash for shell configuration, install scripts, and simple glue.
- Use Python when there is a choice between languages.
- Python scripts must work with the system Python (no external dependencies unless unavoidable).

## Python

- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- Use Google-style docstrings on all public functions, classes, and modules.
- Use type annotations on function signatures.
- Prefer `pathlib.Path` over `os.path`.
- Use `from __future__ import annotations` for forward references.

### Docstring format

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

## Python Toolchain

- **Formatter**: Black (line length 88, target Python 3.11+)
- **Linter**: Flake8 + flake8-bugbear
- **Type checker**: mypy (strict mode)
- **LSP**: pyright (strict type checking)
- **No ruff/Astral** — see Design Decisions below

Reference configs live in `reference/python/`. Copy `pyproject.toml` and `.flake8` into new project roots.

## Markdown

- Follow [CommonMark](https://commonmark.org/) spec.
- Use ATX headers (`#`, `##`) instead of bold text for sections.
- Leave a blank line before and after lists.
- Use fenced code blocks with a language identifier.
- Do not hard-wrap prose. Let the editor or viewer handle line wrapping.

## Shell scripts

- Use `set -euo pipefail` in bash scripts.
- Quote all variable expansions.
- Use `command -v` instead of `which`.

## Design Decisions

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
