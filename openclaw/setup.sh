#!/usr/bin/env bash
# OpenClaw setup — idempotent, run after dotfiles install
# Requires: ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, BRAVE_API_KEY in environment
# Usage: source ~/.secrets && ~/dotfiles/openclaw/setup.sh

set -euo pipefail

REQUIRED_SECRETS=(ANTHROPIC_API_KEY TELEGRAM_BOT_TOKEN BRAVE_API_KEY)

check_secrets() {
    local missing=()
    for key in "${REQUIRED_SECRETS[@]}"; do
        [[ -z "${!key:-}" ]] && missing+=("$key")
    done
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
    if ! systemctl --user is-enabled openclaw-gateway.service &>/dev/null; then
        echo "Installing gateway daemon..."
        openclaw onboard --non-interactive --accept-risk \
            --anthropic-api-key "$ANTHROPIC_API_KEY" \
            --skip-skills --skip-search --install-daemon
    fi

    if ! systemctl --user is-enabled openclaw-node.service &>/dev/null; then
        echo "Installing node host service..."
        openclaw node install
    fi
}

configure_channels() {
    echo "Configuring Telegram..."
    openclaw channels add --channel telegram --token "$TELEGRAM_BOT_TOKEN"
    openclaw config set channels.telegram.groupPolicy disabled
    openclaw config set channels.telegram.streaming partial
    openclaw config set channels.telegram.retry.attempts 3
    openclaw config set channels.telegram.retry.minDelayMs 5000
    openclaw config set channels.telegram.retry.maxDelayMs 60000
    openclaw config set channels.telegram.retry.jitter 0.2
}

configure_agent() {
    echo "Configuring agent defaults..."
    openclaw config set agents.defaults.model.primary "anthropic/claude-sonnet-4-6"
    openclaw config set agents.defaults.model.fallbacks '["anthropic/claude-haiku-4-5-20251001"]'
    openclaw config set agents.defaults.contextPruning.mode "cache-ttl"
    openclaw config set agents.defaults.contextPruning.ttl "5m"
    openclaw config set agents.defaults.contextPruning.keepLastAssistants 3
    openclaw config set agents.defaults.contextPruning.hardClear.enabled true
    openclaw config set agents.defaults.contextPruning.hardClear.placeholder "[cleared]"
}

configure_sessions() {
    echo "Configuring session policies..."
    openclaw config set session.dmScope "per-channel-peer"
    openclaw config set session.reset.mode "daily"
    openclaw config set session.reset.atHour 4
    openclaw config set session.reset.idleMinutes 30
    openclaw config set session.maintenance.mode "enforce"
    openclaw config set session.maintenance.pruneAfter "14d"
    openclaw config set session.maintenance.maxEntries 100
    openclaw config set session.maintenance.rotateBytes "10mb"
}

configure_gateway_secrets() {
    echo "Wiring API keys into gateway service..."
    local dropin_dir="$HOME/.config/systemd/user/openclaw-gateway.service.d"
    mkdir -p "$dropin_dir"
    chmod 700 "$dropin_dir"
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
configure_agent
configure_sessions
configure_gateway_secrets

echo ""
echo "Next: open Telegram, message the bot, send /start"
echo "Then run: openclaw pairing list && openclaw pairing approve <CODE>"
echo ""
echo "Setup complete. Run 'openclaw health' to verify."
