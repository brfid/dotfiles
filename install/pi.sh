#!/usr/bin/env bash
# Pi 5 profile

echo "Installing Pi 5 configs..."

# browsh (text-based browser, requires Firefox)
if ! command -v browsh &>/dev/null; then
    BROWSH_VERSION="1.8.2"
    BROWSH_DEB="/tmp/browsh_${BROWSH_VERSION}_linux_arm64.deb"
    curl -fsSL "https://github.com/browsh-org/browsh/releases/download/v${BROWSH_VERSION}/browsh_${BROWSH_VERSION}_linux_arm64.deb" \
        -o "$BROWSH_DEB"
    sudo dpkg -i "$BROWSH_DEB"
    rm -f "$BROWSH_DEB"
fi

link_path "$DOTFILES/tmux/.tmux.conf" ~/.tmux.conf
link_path "$DOTFILES/tmux/.tmux" ~/.tmux

link_path "$DOTFILES/x11/.xprofile" ~/.xprofile
link_path "$DOTFILES/x11/.xinitrc" ~/.xinitrc

# Signal CLI
mkdir -p ~/.local/bin
link_path "$DOTFILES/scripts/signal/scli" ~/.local/bin/scli
link_path "$DOTFILES/scripts/signal/signal-setup.sh" ~/.local/bin/signal-setup
chmod +x "$DOTFILES/scripts/signal/signal-setup.sh"
link_path "$DOTFILES/scripts/signal/signal-backup.sh" ~/.local/bin/signal-backup
chmod +x "$DOTFILES/scripts/signal/signal-backup.sh"

# User systemd services
mkdir -p ~/.config/systemd/user
link_path "$DOTFILES/systemd-user/rclone-dropbox.service" ~/.config/systemd/user/rclone-dropbox.service
link_path "$DOTFILES/systemd-user/edc-monthly-snapshot.service" ~/.config/systemd/user/edc-monthly-snapshot.service
link_path "$DOTFILES/systemd-user/edc-monthly-snapshot.timer" ~/.config/systemd/user/edc-monthly-snapshot.timer
link_path "$DOTFILES/systemd-user/edc-weekly-snapshot.service" ~/.config/systemd/user/edc-weekly-snapshot.service
link_path "$DOTFILES/systemd-user/edc-weekly-snapshot.timer" ~/.config/systemd/user/edc-weekly-snapshot.timer

# Clawdiac (OpenClaw) — full setup via dedicated script
# Requires secrets to be loaded: source ~/.secrets && ~/clawdiac/setup.sh
if command -v openclaw &>/dev/null; then
    echo "OpenClaw already installed."
else
    echo "OpenClaw not installed — run: source ~/.secrets && ~/clawdiac/setup.sh"
fi

# Shell local additions
mkdir -p ~/.config/shell
link_path "$DOTFILES/shell/local.d/pi.sh" ~/.config/shell/local

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
    render_template "$DOTFILES/system/rsnapshot/rsnapshot.conf" /tmp/rsnapshot.conf
    sudo cp /tmp/rsnapshot.conf /etc/rsnapshot.conf
    rm -f /tmp/rsnapshot.conf

    # Logrotate
    sudo ln -sfn "$DOTFILES/system/logrotate/rsnapshot" /etc/logrotate.d/rsnapshot
    sudo ln -sfn "$DOTFILES/system/logrotate/minetest-server" /etc/logrotate.d/minetest-server

    # LightDM (drop-in survives apt upgrades)
    sudo mkdir -p /etc/lightdm/lightdm.conf.d
    render_template "$DOTFILES/system/lightdm/lightdm.conf.d/99-local.conf" /tmp/99-local.conf
    sudo cp /tmp/99-local.conf /etc/lightdm/lightdm.conf.d/99-local.conf
    rm -f /tmp/99-local.conf

    # Swap
    sudo cp "$DOTFILES/system/swap/dphys-swapfile" /etc/dphys-swapfile

    sudo systemctl daemon-reload
    sudo systemctl enable cpufreq-ondemand-tune.service cpufreq-schedutil-tune.service
else
    echo "Skipping system configs (sudo required)"
fi

echo "Pi 5 profile installed."
