export PS1='%D{%H:%M:%S} %n@%m %1~ %# '

alias zshrc='source ~/.zshrc'

[ -f ~/.config/shell/aliases ] && source ~/.config/shell/aliases
[ -f ~/.secrets ] && source ~/.secrets

# Machine-specific additions (linked by dotfiles install/<profile>.sh)
[ -f ~/.config/shell/local ] && source ~/.config/shell/local
