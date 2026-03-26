#!/bin/bash
cache=/tmp/.tmux_netstat
IDLE_THRESHOLD=102400  # 100 KB/s — below this, show idle

# Find active non-virtual interface
iface=$(ip -br link show | awk '$2=="UP"{print $1; exit}')
[ -z "$iface" ] && exit

read -r rx2 tx2 < <(awk -v i="$iface:" '$1==i{print $2, $10}' /proc/net/dev)

if [ -f "$cache" ]; then
    read -r rx1 tx1 ts1 < "$cache"
    now=$(date +%s)
    dt=$((now - ts1))
    [ "$dt" -lt 1 ] && dt=1
    rxr=$(( (rx2 - rx1) / dt ))
    txr=$(( (tx2 - tx1) / dt ))

    fmt_rate() {
        if [ "$1" -ge 1048576 ]; then
            awk "BEGIN {printf \"%.1fMB/s\", $1/1048576}"
        elif [ "$1" -ge 1024 ]; then
            awk "BEGIN {printf \"%.0fKB/s\", $1/1024}"
        else
            echo "${1}B/s"
        fi
    }

    if [ "$rxr" -lt "$IDLE_THRESHOLD" ] && [ "$txr" -lt "$IDLE_THRESHOLD" ]; then
        echo "↓ — ↑ —"
    else
        echo "↓ $(fmt_rate $rxr) ↑ $(fmt_rate $txr)"
    fi
fi
echo "$rx2 $tx2 $(date +%s)" > "$cache"
