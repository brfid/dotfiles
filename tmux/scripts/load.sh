#!/bin/bash

read -r load1 _ < /proc/loadavg || exit 1
cores=$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null)
[ -n "$cores" ] || exit 1

# Show the real 1-minute load average with core-count context so it is not
# mistaken for another percentage.
printf '%s/%s\n' "$load1" "$cores"
