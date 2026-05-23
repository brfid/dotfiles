# python

Role: Python development defaults.

Toolchain:

- Prefer Astral: `uv` for envs/deps/tool running, `ruff` for lint/import/style.
- `uv` is desired but was not on PATH during audit.
- Existing pip/setuptools CI should not be migrated to uv casually.

Project shape:

- `pyproject.toml` is source of truth for metadata, deps, tools, entry points, tests, and significant project constants.
- Use repo-local `.venv/`; never system Python for project deps.
- Current default for serious CLIs/services: `setuptools`, `[project.scripts]`, pytest, Ruff, mypy, and `py.typed` for typed packages.
- `uv.lock` policy is per-repo.

Dependencies:

- Prefer stdlib, then major well-maintained packages.
- Avoid package versions less than one week old unless explicitly accepted.

Code:

- Prefer functions/plain data over classes unless objects have clear value.
- Keep `main()` thin; move behavior into testable helpers.
- Use precise types, future annotations, frozen dataclasses for values, `TypedDict` for dict contracts, Click for CLIs, and Google-style docstrings for nontrivial functions.

Docs:

- Use CommonMark-compatible Markdown for README files and other docs.
- Put blank lines before and after lists, code fences, and section blocks.

Validation:

- `pytest -q`
- `ruff check .`
- `mypy <package>/`
- Ruff format is opt-in.

Do not store:

- `.venv/`, caches, build/wheel artifacts, `.egg-info/`, downloaded interpreters, or generated local tool state.
