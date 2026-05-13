#!/bin/bash
cd "$1" 2>/dev/null || exit

uid=${UID:-$(id -u)}
cache_dir="${XDG_RUNTIME_DIR:-/run/user/$uid}"
[ -d "$cache_dir" ] && [ -w "$cache_dir" ] || cache_dir=/dev/shm
[ -d "$cache_dir" ] && [ -w "$cache_dir" ] || cache_dir=/tmp
key=$(printf '%s' "$PWD" | cksum)
key=${key%% *}
cache="$cache_dir/.tmux_git_$key"
ttl=${TMUX_GIT_CACHE_TTL:-60}
now=$(date +%s)

if [ -f "$cache" ]; then
    IFS= read -r ts < "$cache"
    if [ $((now - ts)) -lt "$ttl" ]; then
        sed -n '2p' "$cache"
        exit
    fi
fi

branch=$(git branch --show-current 2>/dev/null) || exit
dirty=$(git status --short -uno 2>/dev/null)
[ -n "$dirty" ] && out="  ${branch}*" || out="  ${branch}"
printf '%s\n%s\n' "$now" "$out" > "$cache"
printf '%s\n' "$out"
