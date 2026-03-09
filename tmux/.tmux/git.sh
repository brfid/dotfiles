#!/bin/bash
cd "$1" 2>/dev/null || exit
branch=$(git branch --show-current 2>/dev/null) || exit
dirty=$(git status --porcelain 2>/dev/null | wc -l)
[ "$dirty" -gt 0 ] && echo "| ${branch}*" || echo "| ${branch}"
