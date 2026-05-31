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

Terminal: xfce4-terminal with JetBrainsMonoNL Nerd Font Mono at 14pt and
orange foreground (`#ff8700`). Install the Nerd Font on the machine, or pick a
close installed Nerd Font Mono family.

Panel: keep the system tray visible for NetworkManager and Blueman. Place the
`pulseaudio` plugin immediately next to the tray.
