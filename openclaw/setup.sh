#!/usr/bin/env bash
# OpenClaw (CLAWIAC) setup — idempotent, run after dotfiles install
# Requires: ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, BRAVE_API_KEY in environment
# Usage: source ~/.secrets && ~/dotfiles/openclaw/setup.sh

set -euo pipefail

check_secrets() {
    local missing=()
    [[ -z "${ANTHROPIC_API_KEY:-}" ]] && missing+=("ANTHROPIC_API_KEY")
    [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]] && missing+=("TELEGRAM_BOT_TOKEN")
    [[ -z "${BRAVE_API_KEY:-}" ]] && missing+=("BRAVE_API_KEY")
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Missing secrets: ${missing[*]}" >&2
        echo "Add them to ~/.secrets and re-run: source ~/.secrets && $0" >&2
        exit 1
    fi
}

install_openclaw() {
    if ! command -v openclaw &>/dev/null; then
        echo "Installing OpenClaw..."
        curl -fsSL https://openclaw.ai/install.sh | bash
    else
        echo "OpenClaw $(openclaw --version 2>/dev/null | head -1) already installed."
    fi
}

install_services() {
    echo "Installing gateway daemon..."
    if ! systemctl --user is-enabled openclaw-gateway.service &>/dev/null; then
        openclaw onboard --non-interactive --accept-risk \
            --anthropic-api-key "$ANTHROPIC_API_KEY" \
            --skip-skills --skip-search --install-daemon
    fi

    echo "Installing node host service..."
    if ! systemctl --user is-enabled openclaw-node.service &>/dev/null; then
        openclaw node install
    fi
}

configure_channels() {
    echo "Configuring Telegram..."
    openclaw channels add --channel telegram --token "$TELEGRAM_BOT_TOKEN"
    openclaw config set channels.telegram.groupPolicy disabled
}

configure_model() {
    echo "Setting model to Claude Haiku..."
    openclaw models set claude-haiku-4-5-20251001
}

configure_gateway_secrets() {
    echo "Wiring API keys into gateway service..."
    local dropin_dir="$HOME/.config/systemd/user/openclaw-gateway.service.d"
    mkdir -p "$dropin_dir"
    cat > "$dropin_dir/secrets.conf" << EOF
[Service]
Environment=BRAVE_API_KEY=${BRAVE_API_KEY}
Environment=ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
EOF
    chmod 600 "$dropin_dir/secrets.conf"

    systemctl --user daemon-reload
    systemctl --user enable --now openclaw-gateway.service
    systemctl --user enable --now openclaw-node.service
}

check_secrets
install_openclaw
install_services
configure_channels
configure_model
configure_gateway_secrets

echo ""
echo "Next: open Telegram, message @CLAWIAC_BOT, send /start"
echo "Then run: openclaw pairing list && openclaw pairing approve <CODE>"
echo ""
echo "CLAWIAC setup complete. Run 'openclaw status' to verify."
