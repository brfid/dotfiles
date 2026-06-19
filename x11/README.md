# x11

Terminal: xterm. Preferred over xfce4-terminal for lower input latency and
reduced CPU on resource-constrained machines. xfce4-terminal stays installed
as part of the `xfce4-goodies` meta-package.

Font: JetBrainsMonoNL Nerd Font Mono, 14pt. Foreground: `#ff8700` (orange).
Background: black. 256color, UTF-8, 10000-line scrollback.

Config: `~/.Xresources`, loaded via `xrdb -merge ~/.Xresources` at session
start. No `sync.toml` needed — the config is short enough for a model to
reconstruct from this capsule.

## Display power (DPMS)

X screensaver disabled; display powers off via DPMS after 1 hour. VA panel —
no burn-in risk, so sleep is purely for power saving.

Config: `~/.xprofile` → `dotfiles/x11/xprofile`, sourced at session start by
LightDM.

```sh
xset s off
xset +dpms
xset dpms 0 0 3600
```
