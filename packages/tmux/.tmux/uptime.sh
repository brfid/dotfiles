#!/bin/bash
up=$(awk '{print int($1)}' /proc/uptime)
days=$((up / 86400))
hours=$(( (up % 86400) / 3600 ))
mins=$(( (up % 3600) / 60 ))
[ "$days" -gt 0 ] && printf "%dd %d:%02d" $days $hours $mins || printf "%d:%02d" $hours $mins
