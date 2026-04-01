#!/bin/bash
# Average frequency across all cores
total=0; count=0
for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
    val=$(cat "$f" 2>/dev/null) || continue
    total=$(( total + val )); count=$(( count + 1 ))
done
[ "$count" -gt 0 ] || exit
awk "BEGIN {printf \"%.1fGHz\", $total/$count/1000000}"
