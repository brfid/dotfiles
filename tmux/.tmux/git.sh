#!/bin/bash
cd "$1" 2>/dev/null || exit
branch=$(git branch --show-current 2>/dev/null) || exit
dirty=$(git status --porcelain 2>/dev/null | wc -l)
total=$(git ls-files 2>/dev/null | wc -l)
echo "  ${branch} (${dirty}/${total})"
