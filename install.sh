#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

link_path() {
    local src="$1"
    local dst="$2"

    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
        mv "$dst" "${dst}.pre-dotfiles.$(date +%Y%m%d-%H%M%S)"
    fi

    ln -sfn "$src" "$dst"
}

# --- Common (all systems) ---

mkdir -p ~/.config
link_path "$DOTFILES/nvim" ~/.config/nvim
link_path "$DOTFILES/shell/zshrc" ~/.zshrc
link_path "$DOTFILES/bash/.bashrc" ~/.bashrc
mkdir -p ~/.config/Code/User/snippets
if [ -f "$DOTFILES/vscode/settings.json" ]; then
    link_path "$DOTFILES/vscode/settings.json" ~/.config/Code/User/settings.json
fi
for snippet in "$DOTFILES"/vscode/snippets/*.code-snippets; do
    [ -e "$snippet" ] || continue
    link_path "$snippet" "$HOME/.config/Code/User/snippets/$(basename "$snippet")"
done

if [ ! -f ~/.config/shell/env ]; then
    mkdir -p ~/.config/shell
    cp "$DOTFILES/shell/env.example" ~/.config/shell/env
fi

mkdir -p ~/.config/gh
link_path "$DOTFILES/gh/config.yml" ~/.config/gh/config.yml

chmod +x "$DOTFILES/scripts"/*.py

# Interactive setup (skipped when non-interactive, e.g. cloud-init)
if [ -t 0 ]; then
    mkdir -p ~/.config/neomutt
    if [ ! -f ~/.config/neomutt/neomuttrc ]; then
        read -rp "Neomutt name: " mutt_name
        read -rp "Neomutt email (Gmail): " mutt_email
        sed "s/Your Name/$mutt_name/g;s/you@gmail.com/$mutt_email/g" \
            "$DOTFILES/neomutt/neomuttrc.example" > ~/.config/neomutt/neomuttrc
    fi

    if [ ! -f ~/.gitconfig ]; then
        read -rp "Git name: " git_name
        read -rp "Git email: " git_email
        sed "s/Your Name/$git_name/;s/you@example.com/$git_email/" \
            "$DOTFILES/git/.gitconfig.example" > ~/.gitconfig
    fi
fi

# --- Pi 5 setup (opt-in: ./install.sh --pi) ---

if [[ "${1:-}" == "--pi" ]]; then
    echo "Installing Pi 5 configs..."

    link_path "$DOTFILES/tmux/.tmux.conf" ~/.tmux.conf
    link_path "$DOTFILES/tmux/.tmux" ~/.tmux

    link_path "$DOTFILES/x11/.xprofile" ~/.xprofile
    link_path "$DOTFILES/x11/.xinitrc" ~/.xinitrc

    # User systemd services
    mkdir -p ~/.config/systemd/user
    link_path "$DOTFILES/systemd-user/rclone-dropbox.service" ~/.config/systemd/user/rclone-dropbox.service
    link_path "$DOTFILES/systemd-user/edc-monthly-snapshot.service" ~/.config/systemd/user/edc-monthly-snapshot.service
    link_path "$DOTFILES/systemd-user/edc-monthly-snapshot.timer" ~/.config/systemd/user/edc-monthly-snapshot.timer
    link_path "$DOTFILES/systemd-user/edc-weekly-snapshot.service" ~/.config/systemd/user/edc-weekly-snapshot.service
    link_path "$DOTFILES/systemd-user/edc-weekly-snapshot.timer" ~/.config/systemd/user/edc-weekly-snapshot.timer

    # System configs (requires sudo)
    if sudo -n true 2>/dev/null; then
        echo "Linking system configs..."

        # Unbound / Pi-hole DNS
        sudo mkdir -p /etc/unbound/unbound.conf.d
        sudo ln -sfn "$DOTFILES/system/unbound/unbound.conf" /etc/unbound/unbound.conf
        sudo ln -sfn "$DOTFILES/system/unbound/unbound.conf.d/pi-hole.conf" /etc/unbound/unbound.conf.d/pi-hole.conf
        sudo ln -sfn "$DOTFILES/system/unbound/unbound.conf.d/remote-control.conf" /etc/unbound/unbound.conf.d/remote-control.conf
        sudo ln -sfn "$DOTFILES/system/unbound/unbound.conf.d/root-auto-trust-anchor-file.conf" /etc/unbound/unbound.conf.d/root-auto-trust-anchor-file.conf

        # CPU frequency governor
        sudo ln -sfn "$DOTFILES/system/cpufreq/cpufrequtils" /etc/default/cpufrequtils
        sudo ln -sfn "$DOTFILES/system/cpufreq/cpufreq-ondemand-tune.service" /etc/systemd/system/cpufreq-ondemand-tune.service
        sudo ln -sfn "$DOTFILES/system/cpufreq/cpufreq-schedutil-tune.service" /etc/systemd/system/cpufreq-schedutil-tune.service

        # Rsnapshot backup
        sudo ln -sfn "$DOTFILES/system/rsnapshot/rsnapshot.conf" /etc/rsnapshot.conf

        # Logrotate
        sudo ln -sfn "$DOTFILES/system/logrotate/rsnapshot" /etc/logrotate.d/rsnapshot
        sudo ln -sfn "$DOTFILES/system/logrotate/minetest-server" /etc/logrotate.d/minetest-server

        # LightDM
        sudo ln -sfn "$DOTFILES/system/lightdm/lightdm.conf" /etc/lightdm/lightdm.conf

        sudo systemctl daemon-reload
        sudo systemctl enable cpufreq-ondemand-tune.service cpufreq-schedutil-tune.service
    else
        echo "Skipping system configs (sudo required)"
    fi

    echo "Pi 5 profile installed."
fi

# --- macOS setup (opt-in: ./install.sh --mac) ---

if [[ "${1:-}" == "--mac" ]]; then
    echo "Installing macOS configs..."

    PYTHON3="$(which python3)"

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

    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load "$PLIST"

    echo "macOS profile installed. repo-sync will run every 15 minutes."
    echo "Logs: ~/Library/Logs/repo-sync.log"
fi

echo "Done."
