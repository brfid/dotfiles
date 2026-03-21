#!/usr/bin/env bash
# edcloud profile — server-side dotfiles

# tmux (useful on headless servers)
link_path "$DOTFILES/tmux/.tmux.conf" ~/.tmux.conf
link_path "$DOTFILES/tmux/.tmux" ~/.tmux

# systemd user services (cloud-init also sets these up, but this keeps
# dotfiles self-sufficient for manual rebuilds)
mkdir -p ~/.config/systemd/user
link_path "$DOTFILES/systemd-user/rclone-dropbox.service" \
    ~/.config/systemd/user/rclone-dropbox.service

# Shell local additions
mkdir -p ~/.config/shell
link_path "$DOTFILES/shell/local.d/edcloud.sh" ~/.config/shell/local
