export PS1='%D{%H:%M:%S} %n@%m %1~ %# '

alias zshrc='source ~/.zshrc'

[ -f ~/.config/shell/aliases ] && source ~/.config/shell/aliases
[ -f ~/.secrets ] && source ~/.secrets

# Machine-specific additions (symlink from shell/.config/shell/local.d/)
[ -f ~/.config/shell/local ] && source ~/.config/shell/local
