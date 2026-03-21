# Pi-specific shell additions — sourced via ~/.config/shell/local

export PATH="$HOME/.npm-global/bin:$PATH"

# OpenClaw: faster CLI startup on ARM via Node.js compile cache
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache

alias t='tmux new-session -A -s main'
alias tmx='tmux new-session \; split-window -h -p 67 \; select-pane -t 0'

# -------------------------
# Minetest / VoxeLibre server helpers
# -------------------------
mtvl() {
  local world="${1:-$HOME/.minetest/worlds/wwwwrettt}"
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
