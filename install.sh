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
render_template() {
    local src="$1"
    local dst="$2"
    sed "s/__USER__/$USER/g" "$src" > "$dst"
}

export -f link_path
export -f render_template
export DOTFILES

detect_profile() {
    # 1. Explicit env override
    if [[ -n "${DOTFILES_PROFILE:-}" ]]; then
        echo "$DOTFILES_PROFILE"
        return
    fi
    # 2. Marker file
    if [[ -f "$HOME/.dotfiles-profile" ]]; then
        cat "$HOME/.dotfiles-profile"
        return
    fi
    # 3. Hostname-based
    case "$(hostname -s)" in
        edcloud) echo "edcloud"; return ;;
    esac
    # 4. Hardware/OS detection
    if grep -q "Raspberry" /proc/device-tree/model 2>/dev/null; then
        echo "pi"
    elif [[ "$(uname -s)" == "Darwin" ]]; then
        echo "mac"
    else
        echo "unknown"
    fi
}

PROFILE=$(detect_profile)
echo "Installing dotfiles [profile: ${PROFILE}]"

source "$DOTFILES/install/common.sh"

PROFILE_SCRIPT="$DOTFILES/install/${PROFILE}.sh"
if [[ -f "$PROFILE_SCRIPT" ]]; then
    echo "Applying ${PROFILE} profile..."
    source "$PROFILE_SCRIPT"
else
    echo "No profile script for '${PROFILE}' — common config only."
fi

echo "Done."
