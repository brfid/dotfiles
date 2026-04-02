# macOS-specific shell additions — sourced via ~/.config/shell/local

# Homebrew
if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

export PATH="$HOME/.npm-global/bin:$PATH"

alias t='tmux -CC new-session -A -s main'
alias tmx='tmux new-session \; split-window -h -p 67 \; select-pane -t 0'
