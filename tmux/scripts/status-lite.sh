#!/bin/bash
# Low-wakeup tmux status helper. Keep this cheap: one process, proc/sys reads only.

# Temperature, rightmost for fast thermal glance. Color only the value.
if [ -r /sys/class/thermal/thermal_zone0/temp ]; then
    read -r temp_millic < /sys/class/thermal/thermal_zone0/temp
    temp_c=$(( (temp_millic + 500) / 1000 ))
    if [ "$temp_c" -ge 70 ]; then
        temp="#[fg=colour196]${temp_c}°C#[fg=colour208]"
    elif [ "$temp_c" -ge 55 ]; then
        temp="#[fg=colour220]${temp_c}°C#[fg=colour208]"
    else
        temp="${temp_c}°C"
    fi
else
    temp="temp?"
fi

# 1-minute load with online core count.
read -r load1 _ < /proc/loadavg || load1="?"
cores=$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || printf '?')

# Memory usage from /proc/meminfo, MiB/GiB compact display.
mem_total_kb=0
mem_available_kb=0
while read -r key value _; do
    case "$key" in
        MemTotal:) mem_total_kb=$value ;;
        MemAvailable:) mem_available_kb=$value ;;
    esac
done < /proc/meminfo
mem_used_kb=$((mem_total_kb - mem_available_kb))
fmt_kb() {
    awk -v kb="$1" 'BEGIN {
        if (kb >= 1048576) printf "%.1fGi", kb/1048576;
        else printf "%.0fMi", kb/1024;
    }'
}
mem="$(fmt_kb "$mem_used_kb")/$(fmt_kb "$mem_total_kb")"

# Uptime in whole-hour intervals. Under 24h, show hours first: 0h, 1h, 2h.
read -r up_seconds _ < /proc/uptime
up=${up_seconds%.*}
total_hours=$((up / 3600))
days=$((total_hours / 24))
hours=$((total_hours % 24))
if [ "$days" -gt 0 ]; then
    uptime="${days}d ${hours}h"
else
    uptime="${total_hours}h"
fi

printf 'λ %s/%s  ≡ %s  ⧗ %s  %s\n' "$load1" "$cores" "$mem" "$uptime" "$temp"
