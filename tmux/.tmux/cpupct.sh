#!/bin/bash
cache=/tmp/.tmux_cpustat
# Read aggregate line: user nice system idle iowait irq softirq steal (guest guest_nice ignored)
read -r _ a2 b2 c2 d2 e2 f2 g2 h2 _ < /proc/stat
if [ -f "$cache" ]; then
    read -r a1 b1 c1 d1 e1 f1 g1 h1 < "$cache"
    total=$(( (a2+b2+c2+d2+e2+f2+g2+h2) - (a1+b1+c1+d1+e1+f1+g1+h1) ))
    idle=$(( d2+e2 - d1-e1 ))
    [ "$total" -gt 0 ] && echo "$(( 100 * (total-idle) / total ))%"
fi
echo "$a2 $b2 $c2 $d2 $e2 $f2 $g2 $h2" > "$cache"
