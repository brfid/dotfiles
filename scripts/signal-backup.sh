#!/usr/bin/env bash
# Back up signal-cli identity/data to edcloud for repave recovery.
# Run after initial linking or periodically.
set -euo pipefail

SRC="$HOME/.local/share/signal-cli"
DST="$HOME/edcloud/signal-cli"

if [ ! -d "$SRC" ]; then
    echo "No signal-cli data at $SRC — nothing to back up."
    exit 1
fi

mkdir -p "$DST"
rsync -a --delete "$SRC/" "$DST/"
echo "signal-cli data backed up to $DST"
