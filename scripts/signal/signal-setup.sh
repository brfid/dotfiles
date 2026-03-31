#!/usr/bin/env bash
# Set up signal-cli: restore from edcloud backup or link as a new device.
# Usage: ./signal-setup.sh [--name DEVICE_NAME]
#
# STATUS: never successfully linked as of March 2026.
#
# KNOWN ISSUES
#   Signal's provisioning WebSocket closes after 60 seconds. The phone must
#   scan *and* complete the handshake within that window. Repeated failures
#   trigger server-side rate limiting — wait 30–60 minutes before retrying.
#
#   URI format: sgnl://linkdevice?uuid=...&pub_key=... (correct as of 0.14.1)
#   The old tsdevice:/ format is deprecated.
#
# BEFORE ATTEMPTING
#   1. Settings > Linked Devices on your phone — max 5 linked devices allowed.
#   2. Pre-navigate to Settings > Linked Devices > + before running this script.
#   3. Open the QR in a browser (chromium/firefox) rather than feh — better rendering.
#      Use DISPLAY=:0 if running from tmux without a display.
#   4. Try a non-default device name (--name mypi) if the default fails.
#   5. If still failing, wait until the next day — provisioning endpoint has known
#      flakiness with third-party clients.
#
# REFERENCES
#   signal-cli-rest-api #651  — "QR code not valid" on Android, Jan 2025+
#   AsamK/signal-cli #1567    — "Connection closed" during provisioning
#   AsamK/signal-cli #190     — "Linking Device Failed" history
set -euo pipefail

EDCLOUD_SRC="$HOME/dev/edcloud/signal-cli"
DATA_DIR="$HOME/.local/share/signal-cli"
ACCOUNTS_JSON="$DATA_DIR/data/accounts.json"
DEVICE_NAME="${SIGNAL_DEVICE_NAME:-rpi}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) DEVICE_NAME="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# --- Check deps ---
if ! command -v signal-cli &>/dev/null; then
    echo "Error: signal-cli not found. Install it first (e.g. brew install signal-cli)."
    exit 1
fi
if ! command -v qrencode &>/dev/null; then
    echo "Error: qrencode not found. Install it (e.g. sudo apt install qrencode)."
    exit 1
fi

# --- Already configured? ---
if [ -f "$ACCOUNTS_JSON" ] && \
   python3 -c "import json,sys; d=json.load(open('$ACCOUNTS_JSON')); sys.exit(0 if d.get('accounts') else 1)" 2>/dev/null; then
    echo "signal-cli already has a linked account. Nothing to do."
    echo "To re-link, remove $DATA_DIR and re-run."
    exit 0
fi

# --- Restore from edcloud if available ---
if [ -d "$EDCLOUD_SRC" ]; then
    echo "Restoring signal-cli data from edcloud..."
    mkdir -p "$(dirname "$DATA_DIR")"
    rsync -a "$EDCLOUD_SRC/" "$DATA_DIR/"
    echo "Restored. Verifying..."
    if [ -f "$ACCOUNTS_JSON" ] && \
       python3 -c "import json,sys; d=json.load(open('$ACCOUNTS_JSON')); sys.exit(0 if d.get('accounts') else 1)" 2>/dev/null; then
        echo "signal-cli ready (restored from edcloud)."
        exit 0
    else
        echo "Edcloud backup exists but has no accounts — falling through to fresh link."
    fi
fi

# --- Fresh device link ---
echo "Linking signal-cli as a new device ('$DEVICE_NAME')..."
echo "This will display a QR code. Scan it in Signal:"
echo "  Phone > Settings > Linked Devices > +"
echo ""

URI_FILE="$(mktemp /tmp/signal-uri.XXXXXX)"
trap 'rm -f "$URI_FILE"' EXIT

signal-cli link --name "$DEVICE_NAME" > "$URI_FILE" &
LINK_PID=$!

# Wait for URI to appear
WAIT=0
while [ ! -s "$URI_FILE" ] && kill -0 "$LINK_PID" 2>/dev/null; do
    sleep 0.3
    WAIT=$((WAIT + 1))
    if [ "$WAIT" -gt 60 ]; then
        echo "Timed out waiting for link URI."
        kill "$LINK_PID" 2>/dev/null || true
        exit 1
    fi
done

if [ ! -s "$URI_FILE" ]; then
    echo "signal-cli exited before producing a URI."
    exit 1
fi

# Display QR code
qrencode -t UTF8 < "$URI_FILE"
echo ""
echo "Waiting for scan..."

if wait "$LINK_PID"; then
    echo "Linked successfully as '$DEVICE_NAME'."

    # Back up to edcloud if available
    if [ -d "$(dirname "$EDCLOUD_SRC")" ]; then
        mkdir -p "$EDCLOUD_SRC"
        rsync -a --delete "$DATA_DIR/" "$EDCLOUD_SRC/"
        echo "Backed up to edcloud."
    fi
else
    echo "Linking failed. Check signal-cli output for details."
    exit 1
fi
