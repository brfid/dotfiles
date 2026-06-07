# xfce

Desktop environment on X11. Config lives in xfconf (not dotfiles); this
capsule records intentional non-default preferences so a model can
reconstruct them.

## Desktop background

Vertical gradient from black to dark grey (~5.7% brightness). No image.
Applied to all monitors and workspace overrides.

```sh
# color-style 2 = vertical gradient
# color1 = black, color2 = rgb(3713,3713,3713) out of 65535
for mon in monitor0 monitor1; do
  xfconf-query -c xfce4-desktop -p /backdrop/screen0/$mon/color-style -s 2
  xfconf-query -c xfce4-desktop -p /backdrop/screen0/$mon/color1 \
    -t uint -s 0 -t uint -s 0 -t uint -s 0 -t uint -s 65535
  xfconf-query -c xfce4-desktop -p /backdrop/screen0/$mon/color2 \
    -t uint -s 3713 -t uint -s 3713 -t uint -s 3713 -t uint -s 65535
  xfconf-query -c xfce4-desktop -p /backdrop/screen0/$mon/image-show -s false
done
```

Note: use `-t uint` not `-t uint16` — xfconf-query silently zeroes the
alpha channel with uint16 on array properties.

## Panel

Dark mode on. Compact: size 26, icon-size 16. Position locked top.

## Theme

Adwaita-dark GTK theme, nuoveXT2 icon theme. Event and feedback sounds off.

## Window manager (xfwm4)

Borderless maximize enabled.

## Terminal

Already documented in `x11/` capsule (orange foreground, JetBrainsMono
Nerd Font 14, no close confirm). xfce4-terminal is present via
xfce4-goodies but xterm is preferred.

## Power and screensaver

Power button action: nothing. No lock on suspend. No sleep activation.

## File manager (Thunar)

All automount, autobrowse, and autoopen disabled via thunar-volman.

## Rebuild

```sh
xfconf-query -c xfce4-desktop -p /backdrop/screen0/$mon/<prop> ...
# or export/import the full channel:
xfconf-query -c xfce4-desktop -l -v > xfce4-desktop.dump
```
