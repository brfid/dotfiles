# x11

Terminal: xterm. Preferred over xfce4-terminal for lower input latency and
reduced CPU on resource-constrained machines. xfce4-terminal stays installed
as part of the `xfce4-goodies` meta-package.

Font: JetBrainsMonoNL Nerd Font Mono, 14pt. Foreground: `#ff8700` (orange).
Background: black. 256color, UTF-8, 10000-line scrollback.

Config: `~/.Xresources`, loaded via `xrdb -merge ~/.Xresources` at session
start. No `sync.toml` needed — the config is short enough for a model to
reconstruct from this capsule.
