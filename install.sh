#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p ~/.config
ln -sfn "$DOTFILES/nvim" ~/.config/nvim
ln -sfn "$DOTFILES/shell/zshrc" ~/.zshrc
ln -sfn "$DOTFILES/bash/.bashrc" ~/.bashrc
ln -sfn "$DOTFILES/tmux/.tmux.conf" ~/.tmux.conf

if [ ! -f ~/.config/shell/env ]; then
    mkdir -p ~/.config/shell
    cp "$DOTFILES/shell/env.example" ~/.config/shell/env
fi

if [ ! -f ~/.gitconfig ]; then
    cp "$DOTFILES/git/.gitconfig.example" ~/.gitconfig
fi

chmod +x "$DOTFILES/scripts"/*.py
