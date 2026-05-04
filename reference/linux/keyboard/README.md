# Keyboard remaps

Local Leopold keyboard remaps live here as `systemd-hwdb` rules.
Use this for FC900RW USB keyboard (`04B4:0510`).
This is real fix for Pi local console/desktop setup.
Applies before X11.
Does not depend on `~/.xprofile`.

## Current mapping

- `Caps Lock` -> `Left Ctrl`
- `Left Ctrl` -> `Left Ctrl`
- `Right Ctrl` -> `Caps Lock`

## Why `hwdb`

- works in tty, LightDM, X11, Wayland
- works for local terminal apps too
- targets exact keyboard device
- keeps full FC900RW mapping
- `setxkbmap -option ctrl:swapcaps` does not handle `Right Ctrl` -> `Caps Lock`

## Install

```bash
sudo install -Dm0644 reference/linux/keyboard/90-leopold-fc900rw.hwdb \
  /etc/udev/hwdb.d/90-leopold-fc900rw.hwdb
sudo systemd-hwdb update
sudo udevadm trigger --subsystem-match=input
```

If old map remains, unplug/replug keyboard once or reboot.

## Pi LXDE

Also apply the managed X11 autostart file:

```bash
install -Dm0644 x11/lxsession/LXDE-pi/autostart \
  ~/.config/lxsession/LXDE-pi/autostart
```

This file must not run `setxkbmap -option ctrl:swapcaps`.
The `hwdb` rule already maps `Caps Lock` to `Left Ctrl`.
Stacking X11 `swapcaps` on top causes double remap after login.

## Verify

```bash
systemd-hwdb query 'evdev:input:b0003v04B4p0510*'
```

Expected:

```text
KEYBOARD_KEY_70039=leftctrl
KEYBOARD_KEY_700e4=capslock
```

## Remove

```bash
sudo rm -f /etc/udev/hwdb.d/90-leopold-fc900rw.hwdb
sudo systemd-hwdb update
sudo udevadm trigger --subsystem-match=input
```

Do not stack X11 `setxkbmap` swapcaps rules on top.
That causes double remap after kernel-level rule is active.
