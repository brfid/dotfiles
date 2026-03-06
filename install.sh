#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing dotfiles from $DOTFILES"

# Neovim
echo "→ Linking Neovim config..."
mkdir -p ~/.config
ln -sfn "$DOTFILES/nvim" ~/.config/nvim
echo "  ✓ ~/.config/nvim"

# Shell
echo "→ Linking shell configs..."
ln -sfn "$DOTFILES/shell/zshrc" ~/.zshrc
echo "  ✓ ~/.zshrc"

# Environment variables
if [ ! -f ~/.config/shell/env ]; then
    mkdir -p ~/.config/shell
    cp "$DOTFILES/shell/env.example" ~/.config/shell/env
    echo "  ✓ ~/.config/shell/env (template - EDIT WITH YOUR KEYS)"
else
    echo "  ⊘ ~/.config/shell/env already exists (not overwriting)"
fi

# Bash
echo "→ Linking bash config..."
ln -sfn "$DOTFILES/bash/.bashrc" ~/.bashrc
echo "  ✓ ~/.bashrc"

# Tmux
echo "→ Linking tmux config..."
ln -sfn "$DOTFILES/tmux/.tmux.conf" ~/.tmux.conf
echo "  ✓ ~/.tmux.conf"

# Git
if [ ! -f ~/.gitconfig ]; then
    cp "$DOTFILES/git/.gitconfig.example" ~/.gitconfig
    echo "  ✓ ~/.gitconfig (template - EDIT WITH YOUR INFO)"
else
    echo "  ⊘ ~/.gitconfig already exists (not overwriting)"
fi

# Scripts
echo "→ Making scripts executable..."
chmod +x "$DOTFILES/scripts"/*.py
echo "  ✓ scripts/"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit ~/.gitconfig with your name and email"
echo "  2. Edit ~/.config/shell/env with your API keys"
echo "  3. Launch nvim - plugins will auto-install"
echo "  4. Reload shell: source ~/.zshrc"
