#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${REPO_ROOT}"

mapfile -t tracked_files < <(git ls-files | grep -Ev '^scripts/check_public_safety\.sh$')

if [ "${#tracked_files[@]}" -eq 0 ]; then
  exit 0
fi

fail=0

check_pattern() {
  local name="$1"
  local regex="$2"
  local matches

  matches="$(grep -InE -- "${regex}" "${tracked_files[@]}" || true)"
  if [ -n "${matches}" ]; then
    printf 'public-safety violation: %s\n' "${name}" >&2
    printf '%s\n' "${matches}" >&2
    fail=1
  fi
}

check_path() {
  local name="$1"
  local regex="$2"
  local matches

  matches="$(printf '%s\n' "${tracked_files[@]}" | grep -E -- "${regex}" || true)"
  if [ -n "${matches}" ]; then
    printf 'public-safety violation: %s\n' "${name}" >&2
    printf '%s\n' "${matches}" >&2
    fail=1
  fi
}

# Direct local identity. Public config should use placeholders such as
# <name>, <user>, /home/__USER__, or /Users/<user>.
check_pattern "real person name" '\bBrad(ley)?[[:space:]]+Fidler\b'
check_pattern "private local username" '(/home/whf\b|/Users/bfidler\b|\bbfidler\b)'
check_pattern "first-name owner metadata" '"name"[[:space:]]*:[[:space:]]*"Bradley"'

# Private workspace paths. Public repo may name private repos in
# workspace/repos.toml, but must not expose local private data paths.
check_pattern "private family path" '(~/family\b|/home/[^[:space:]"]+/family\b|\bfamily/(homeschool|jean-claude)\b)'

# Private-data content descriptions that belong in the private repo, not in
# public rebuild/config docs.
check_pattern "private family data description" '(homeschool logs|mail summaries|identity files|persona, context)'

# Tracked path guard. These are usually accidental directory imports.
check_path "private top-level data directory" '^(family|homeschool|jean-claude|mail|signal-downloads|Dropbox)(/|$)'
check_path "runtime credential/state path" '(^|/)(auth|credentials|token|history|sessions|logs?|cache|sqlite|state_.*\.sqlite|logs_.*\.sqlite)(/|$|\.)'

exit "${fail}"
