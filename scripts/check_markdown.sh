#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MDFORMAT_BIN="${MDFORMAT_BIN:-mdformat}"

if ! command -v "${MDFORMAT_BIN}" >/dev/null 2>&1; then
  echo "mdformat not found. install it first." >&2
  echo "examples: python -m pip install mdformat mdformat-gfm  |  pipx install mdformat-gfm" >&2
  exit 127
fi

cd "${REPO_ROOT}"

mapfile -t markdown_files < <(git ls-files '*.md')

if [ "${#markdown_files[@]}" -eq 0 ]; then
  exit 0
fi

exec "${MDFORMAT_BIN}" --check --wrap keep --number --extensions gfm "$@" "${markdown_files[@]}"
