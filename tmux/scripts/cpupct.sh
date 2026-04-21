#!/bin/bash

uid=${UID:-$(id -u)}
cache_dir="${XDG_RUNTIME_DIR:-/run/user/$uid}"
[ -d "$cache_dir" ] && [ -w "$cache_dir" ] || cache_dir=/dev/shm
[ -d "$cache_dir" ] && [ -w "$cache_dir" ] || cache_dir=/tmp
cache="$cache_dir/.tmux_cpustat_$uid"

# Aggregate CPU busy percentage over the previous tmux refresh interval.
# Treat iowait as non-busy time so the number tracks actual CPU work done.
read -r _ user2 nice2 system2 idle2 iowait2 irq2 softirq2 steal2 _ < /proc/stat

if [ -f "$cache" ]; then
    read -r user1 nice1 system1 idle1 iowait1 irq1 softirq1 steal1 < "$cache"

    total=$(( (user2 + nice2 + system2 + idle2 + iowait2 + irq2 + softirq2 + steal2) - (user1 + nice1 + system1 + idle1 + iowait1 + irq1 + softirq1 + steal1) ))
    idle=$(( (idle2 + iowait2) - (idle1 + iowait1) ))

    if [ "$total" -gt 0 ]; then
        awk -v total="$total" -v idle="$idle" 'BEGIN { printf "%.1f%%\n", 100 * (total - idle) / total }'
    fi
fi

printf '%s %s %s %s %s %s %s %s\n' \
    "$user2" "$nice2" "$system2" "$idle2" "$iowait2" "$irq2" "$softirq2" "$steal2" > "$cache"
