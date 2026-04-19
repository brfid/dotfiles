# Keyboard remaps

Local Leopold keyboard remaps live here as `systemd-hwdb` rules.

Use this path for the FC900RW USB keyboard (`04B4:0510`). It is the real fix
for the Raspberry Pi local console/desktop setup because it applies before X11
and does not depend on `~/.xprofile` being sourced.

Current FC900RW mapping:

- `Caps Lock` → `Left Ctrl`
- `Left Ctrl` → `Left Ctrl` (unchanged)
- `Right Ctrl` → `Caps Lock`

Why `hwdb` instead of X11-only remaps:

- works in tty consoles, LightDM, and X11/Wayland
- applies while using local terminal apps, including `ssh`
- targets the exact keyboard device instead of all keyboards
- preserves the full FC900RW mapping; `setxkbmap -option ctrl:swapcaps` does
  not cover `Right Ctrl` → `Caps Lock`

Install:

```bash
sudo install -Dm0644 reference/linux/keyboard/90-leopold-fc900rw.hwdb \
  /etc/udev/hwdb.d/90-leopold-fc900rw.hwdb
sudo systemd-hwdb update
sudo udevadm trigger --subsystem-match=input
```

If the keyboard is still on the old map after install, unplug/replug it once
or reboot.

Verify:

```bash
systemd-hwdb query 'evdev:input:b0003v04B4p0510*'
```

Expected lines:

```text
KEYBOARD_KEY_70039=leftctrl
KEYBOARD_KEY_700e4=capslock
```

Remove:

```bash
sudo rm -f /etc/udev/hwdb.d/90-leopold-fc900rw.hwdb
sudo systemd-hwdb update
sudo udevadm trigger --subsystem-match=input
```

Do not stack X11 `setxkbmap` swapcaps rules on top of this. That creates a
double remap once the kernel-level rule is active.
