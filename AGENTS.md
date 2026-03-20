# Coding conventions

## Language choice

- Use bash for shell configuration, install scripts, and simple glue.
- Use Python when there is a choice between languages.
- Python scripts must work with the system Python (no external dependencies
  unless unavoidable).

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

## Markdown

- Follow [CommonMark](https://commonmark.org/) spec.
- Use ATX headers (`#`, `##`) instead of bold text for sections.
- Leave a blank line before and after lists.
- Use fenced code blocks with a language identifier.
- Wrap prose at a reasonable line length (80-100 characters) in source.

## Shell scripts

- Use `set -euo pipefail` in bash scripts.
- Quote all variable expansions.
- Use `command -v` instead of `which`.
