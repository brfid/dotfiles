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

mkdir -p ~/.config
link_path "$DOTFILES/nvim" ~/.config/nvim
link_path "$DOTFILES/micro" ~/.config/micro
link_path "$DOTFILES/shell/zshrc" ~/.zshrc
link_path "$DOTFILES/bash/.bashrc" ~/.bashrc
link_path "$DOTFILES/tmux/.tmux.conf" ~/.tmux.conf

mkdir -p ~/.config/Code/User/snippets
if [ -f "$DOTFILES/vscode/settings.json" ]; then
    link_path "$DOTFILES/vscode/settings.json" ~/.config/Code/User/settings.json
fi
if [ -f "$DOTFILES/vscode/keybindings.json" ]; then
    link_path "$DOTFILES/vscode/keybindings.json" ~/.config/Code/User/keybindings.json
fi
for snippet in "$DOTFILES"/vscode/snippets/*.code-snippets; do
    [ -e "$snippet" ] || continue
    link_path "$snippet" "$HOME/.config/Code/User/snippets/$(basename "$snippet")"
done

if [ ! -f ~/.config/shell/env ]; then
    mkdir -p ~/.config/shell
    cp "$DOTFILES/shell/env.example" ~/.config/shell/env
fi

if [ ! -f ~/.gitconfig ]; then
    cp "$DOTFILES/git/.gitconfig.example" ~/.gitconfig
fi

chmod +x "$DOTFILES/scripts"/*.py
