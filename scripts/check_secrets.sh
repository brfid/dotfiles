#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
GITLEAKS_BIN="${GITLEAKS_BIN:-gitleaks}"
CONFIG_PATH="${GITLEAKS_CONFIG:-${REPO_ROOT}/git/.gitleaks.toml}"

if ! command -v "${GITLEAKS_BIN}" >/dev/null 2>&1; then
  echo "gitleaks not found. install it first." >&2
  echo "examples: brew install gitleaks  |  sudo apt install gitleaks" >&2
  exit 127
fi

cd "${REPO_ROOT}"
exec "${GITLEAKS_BIN}" git \
  --config "${CONFIG_PATH}" \
  --redact \
  --verbose \
  "$@" \
  "${REPO_ROOT}"
