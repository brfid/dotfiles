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

# Source shared aliases and secrets
if [ -f ~/.config/shell/aliases ]; then
    . ~/.config/shell/aliases
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

# Machine-specific additions (linked by dotfiles install/<profile>.sh)
if [ -f ~/.config/shell/local ]; then
    . ~/.config/shell/local
fi
