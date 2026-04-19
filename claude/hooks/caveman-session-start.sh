#!/usr/bin/env bash
# Inject repo-managed caveman instructions into Claude at session start.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
INSTRUCTIONS_PATH="${REPO_ROOT}/codex/instructions/caveman.md"

if [ -f "${INSTRUCTIONS_PATH}" ]; then
    instructions_content="$(cat "${INSTRUCTIONS_PATH}")"
else
    instructions_content="Caveman instructions missing at ${INSTRUCTIONS_PATH}."
fi

escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

instructions_escaped="$(escape_for_json "${instructions_content}")"
session_context="<EXTREMELY_IMPORTANT>\nCaveman mode active for this session.\n\n${instructions_escaped}\n</EXTREMELY_IMPORTANT>"

printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "SessionStart",\n    "additionalContext": "%s"\n  }\n}\n' "${session_context}"
