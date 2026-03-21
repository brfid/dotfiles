#!/usr/bin/env bash
# macOS profile

echo "Installing macOS configs..."

PYTHON3="$(command -v python3)"

# Each git-synced folder gets its own plist. Copy this block for additional
# folders — change the label, PLIST filename, REPO_DIR, and log paths.
# Folder names are not committed; they exist only in the generated plist.
# See README for full instructions and prerequisites.
PLIST="$HOME/Library/LaunchAgents/com.brf.repo-sync.plist"

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.brf.repo-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON3</string>
        <string>$DOTFILES/scripts/sync_repo.py</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>REPO_DIR</key>
        <string>$HOME/repo</string>
        <key>BRANCH</key>
        <string>main</string>
        <key>LOGFILE</key>
        <string>$HOME/Library/Logs/repo-sync.log</string>
    </dict>
    <key>StartInterval</key>
    <integer>900</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/repo-sync.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/repo-sync.stderr.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "macOS profile installed. repo-sync will run every 15 minutes."
echo "Logs: ~/Library/Logs/repo-sync.log"
