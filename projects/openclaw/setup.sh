#!/usr/bin/env bash
# OpenClaw setup — idempotent, run after dotfiles install
# Requires: ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, BRAVE_API_KEY, TELEGRAM_FAMILY_GROUP_ID in environment
# Usage: source ~/.secrets && ~/src/dotfiles/openclaw/setup.sh

set -euo pipefail

REQUIRED_SECRETS=(ANTHROPIC_API_KEY TELEGRAM_BOT_TOKEN BRAVE_API_KEY TELEGRAM_FAMILY_GROUP_ID)

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
    openclaw config set channels.telegram.groupPolicy open
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
    openclaw config set agents.defaults.memorySearch.extraPaths '["~/family"]'
    openclaw config set skills.load.extraDirs '["~/family/jean-claude/skills"]'
}

configure_sessions() {
    echo "Configuring session policies..."
    openclaw config set session.dmScope "per-channel-peer"
    openclaw config set session.reset.mode "daily"
    openclaw config set session.reset.atHour 4
    openclaw config set session.reset.idleMinutes 120
    openclaw config set session.maintenance.mode "enforce"
    openclaw config set session.maintenance.pruneAfter "14d"
    openclaw config set session.maintenance.maxEntries 100
    openclaw config set session.maintenance.rotateBytes "10mb"
}

configure_workspace() {
    echo "Writing workspace AGENTS.md and symlinking SOUL.md and IDENTITY.md..."
    local workspace="$HOME/.openclaw/workspace"
    mkdir -p "$workspace"

    # Both SOUL.md and IDENTITY.md are symlinks to ~/family/jean-claude/IDENTITY.md — the canonical persona.
    # Edit that file; do not edit SOUL.md or IDENTITY.md in this workspace directly.
    ln -sf "$HOME/family/jean-claude/IDENTITY.md" "$workspace/SOUL.md"
    ln -sf "$HOME/family/jean-claude/IDENTITY.md" "$workspace/IDENTITY.md"

    cat > "$workspace/AGENTS.md" << 'EOF'
# AGENTS.md — Operating instructions
# Managed by ~/src/dotfiles/openclaw/setup.sh — edits here will be overwritten on next setup run.
# To make permanent changes, edit setup.sh.

You are Jean-Claude, a family assistant. At the start of each session:

1. Read `SOUL.md` (the canonical persona — symlink to `~/family/jean-claude/IDENTITY.md`).
   (`IDENTITY.md` in this workspace is also a symlink to the same file.)
2. Read `~/family/jean-claude/AGENTS.md` for skill routing — this is the table
   you use to decide how to handle any family or homeschool task.
3. Read `memory/` for today and yesterday when continuity matters.
4. Read `~/family/homeschool/STATUS.md` when the task touches school operations,
   current week, deadlines, or hours.

## Skill activation

When you recognize a trigger from the skill routing table, **read the
corresponding skill file before responding**. The skill file contains the
format, procedures, and file ownership rules for that task. Do not improvise
what a skill already handles.

This is not optional. A response that skips the skill file will miss format
requirements and may write to the wrong files.

## Memory

- Write important facts, decisions, and task state to `memory/YYYY-MM-DD.md`.
- Read today and yesterday on session start for continuity.
- Keep entries concise — they accumulate across weeks.

## Tools

See `TOOLS.md` for notes on available local tools and operator shortcuts.

## Heartbeat

See `HEARTBEAT.md` for the heartbeat checklist.
EOF
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

configure_cron() {
    echo "Configuring cron jobs..."
    # Family group chat ID — stored in ~/.secrets as TELEGRAM_FAMILY_GROUP_ID, not hardcoded here.
    local GROUP="$TELEGRAM_FAMILY_GROUP_ID"
    local HAIKU="anthropic/claude-haiku-4-5-20251001"
    local SKILL_MSG_PREFIX="Read ~/family/jean-claude/skills/brief/SKILL.md and follow the"
    local SKILL_MSG_SUFFIX="Output only the brief, no narration."

    # Helper: add job only if it doesn't already exist by name
    cron_add_if_missing() {
        local name="$1"; shift
        if openclaw cron list --json 2>/dev/null | python3 -c \
            "import json,sys; data=json.load(sys.stdin); exit(0 if any(j.get('name')=='$name' for j in data.get('jobs',data)) else 1)" 2>/dev/null; then
            echo "  Cron job '$name' already exists, skipping."
        else
            openclaw cron add --name "$name" "$@"
        fi
    }

    # Single end-of-day log check at 6pm weekdays.
    # Content format is defined in ~/family/jean-claude/skills/brief/SKILL.md — edit there.

    cron_add_if_missing "log-check-6pm" \
        --cron "0 18 * * 1-5" --tz "America/New_York" \
        --model "$HAIKU" --session isolated --announce --to "$GROUP" --light-context \
        --description "6pm daily log summary" \
        --message "$SKILL_MSG_PREFIX evening check format. $SKILL_MSG_SUFFIX"
}

check_secrets
install_openclaw
install_services
configure_channels
configure_agent
configure_sessions
configure_gateway_secrets
configure_workspace
configure_cron

echo ""
echo "Next: open Telegram, message the bot, send /start"
echo "Then run: openclaw pairing list && openclaw pairing approve <CODE>"
echo ""
echo "Setup complete. Run 'openclaw health' to verify."
