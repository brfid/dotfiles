# openbox

Role: fallback window-manager-only session.

Facts:
- Current Openbox config is minimal fallback state, not the primary desktop source.

## Bluetooth

`~/.config/openbox/autostart`:

```sh
lxpolkit &
blueman-applet &
```

Openbox needs a tray host for `blueman-applet` to be visible. Without one, use
`blueman-manager`.
