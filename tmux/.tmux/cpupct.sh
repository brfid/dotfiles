#!/bin/bash
cache=/tmp/.tmux_cpustat
read -r _ a2 b2 c2 d2 _ < /proc/stat
if [ -f "$cache" ]; then
    read -r a1 b1 c1 d1 < "$cache"
    total=$(( (a2+b2+c2+d2) - (a1+b1+c1+d1) ))
    idle=$(( d2 - d1 ))
    [ "$total" -gt 0 ] && echo "$(( 100 * (total-idle) / total ))%"
fi
echo "$a2 $b2 $c2 $d2" > "$cache"
