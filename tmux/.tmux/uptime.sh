#!/bin/bash
up=$(awk '{print int($1)}' /proc/uptime)
days=$((up / 86400))
hours=$(( (up % 86400) / 3600 ))
printf "%d:%02d" $days $hours
