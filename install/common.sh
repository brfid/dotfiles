#!/usr/bin/env bash
# Common setup — applied on all systems
set -euo pipefail

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

if [ ! -f ~/.secrets ]; then
    cp "$DOTFILES/secrets.example" ~/.secrets
    chmod 600 ~/.secrets
    echo "Created ~/.secrets from template — edit it with your real values."
fi

mkdir -p ~/.config/gh
link_path "$DOTFILES/gh/config.yml" ~/.config/gh/config.yml

# Global git hooks (gitleaks pre-commit)
mkdir -p ~/.config/git
link_path "$DOTFILES/git/hooks" ~/.config/git/hooks

chmod +x "$DOTFILES/scripts"/*.py

# Interactive setup (skipped when non-interactive, e.g. cloud-init)
if [ -t 0 ]; then
    mkdir -p ~/.config/neomutt/cache/headers ~/.config/neomutt/cache/bodies
    link_path "$DOTFILES/neomutt/neomuttrc" ~/.config/neomutt/neomuttrc
    link_path "$DOTFILES/neomutt/mailcap" ~/.config/neomutt/mailcap

    if [ ! -f ~/.gitconfig ]; then
        git_name="${GIT_NAME:-}"
        git_email="${GIT_EMAIL:-}"
        if [ -z "$git_name" ]; then
            read -rp "Git name: " git_name
        fi
        if [ -z "$git_email" ]; then
            read -rp "Git email: " git_email
        fi
        sed "s/Your Name/$git_name/;s/you@example.com/$git_email/" \
            "$DOTFILES/git/.gitconfig.example" > ~/.gitconfig
    fi

    # Claude Code settings
    read -rp "Claude Code profile? [default/sandbox] (default): " claude_profile
    claude_profile="${claude_profile:-default}"
    mkdir -p ~/.claude
    if [ "$claude_profile" = "sandbox" ]; then
        link_path "$DOTFILES/claude/settings.sandbox.json" ~/.claude/settings.json
    else
        link_path "$DOTFILES/claude/settings.json" ~/.claude/settings.json
    fi
else
    # Non-interactive: install default Claude Code config
    mkdir -p ~/.claude
    link_path "$DOTFILES/claude/settings.json" ~/.claude/settings.json
fi

link_path "$DOTFILES/claude/CLAUDE.md" ~/.claude/CLAUDE.md

# Claude Code local plugins
mkdir -p ~/.claude/plugins/local
for plugin_dir in "$DOTFILES"/claude/plugins/*/; do
    [ -d "$plugin_dir/.claude-plugin" ] || continue
    plugin_name="$(basename "$plugin_dir")"
    link_path "$plugin_dir" "$HOME/.claude/plugins/local/$plugin_name"
done
