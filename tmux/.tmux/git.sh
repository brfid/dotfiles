#!/bin/bash
cd "$1" 2>/dev/null || exit
branch=$(git branch --show-current 2>/dev/null) || exit
dirty=$(git status --short -uno 2>/dev/null)
[ -n "$dirty" ] && echo "  ${branch}*" || echo "  ${branch}"
