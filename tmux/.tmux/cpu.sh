#!/bin/bash
freq=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null) || exit
awk "BEGIN {printf \"%.1fGHz\", $freq/1000000}"
