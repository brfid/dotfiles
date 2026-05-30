# xfce

Role: primary Debian desktop session.

Baseline packages:
- `xfce4`
- `xfce4-goodies`
- `network-manager-gnome`
- `blueman`
- `pavucontrol`

LightDM should default to the `xfce` session. Keep Openbox installed as a
fallback session.

Panel: keep the system tray visible for NetworkManager and Blueman. Place the
`pulseaudio` plugin immediately next to the tray.
