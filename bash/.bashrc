# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# History settings
HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=2000

# Update window size after each command
shopt -s checkwinsize

# Source personal aliases and secrets if the files exist
if [ -f ~/.aliases ]; then
    . ~/.aliases
fi

if [ -f ~/.secrets ]; then
    . ~/.secrets
fi

# Enable bash completion
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# Set default editor
export EDITOR="nvim"
export VISUAL="nvim"

# Homebrew
if [ -x /home/linuxbrew/.linuxbrew/bin/brew ]; then
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi

PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
export PATH

PS1='\e[0;32m\w\e[0m\n\$ '

# -------------------------
# Minetest / VoxeLibre server helpers
# -------------------------
mtvl() {
  local world="${1:-$HOME/.minetest/worlds/default}"
  local port="${2:-30000}"
  mkdir -p "$HOME/.minetest/logs"
  /usr/lib/minetest/minetestserver \
    --terminal \
    --config "$HOME/.minetest/voxelibre-server.conf" \
    --world "$world" \
    --gameid mineclone2 \
    --port "$port" \
    --logfile "$HOME/.minetest/logs/voxelibre-server.${port}.log"
}

mtvl_log() {
  local port="${1:-30000}"
  tail -n 200 -F "$HOME/.minetest/logs/voxelibre-server.${port}.log"
}

mtvl_tmux() {
  local session="${1:-voxelibre}"
  tmux new-session -A -s "$session" "mtvl"
}
export PATH="$HOME/.npm-global/bin:$PATH"

alias t='tmux new-session -A -s main'
alias tmx='tmux new-session \; split-window -h -p 67 \; select-pane -t 0'
