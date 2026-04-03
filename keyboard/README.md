# Keyboard remaps (udev hwdb)

Kernel-level key remaps via `systemd-hwdb`. Works in console and X/Wayland
— no desktop environment required.

## Files

| File | Keyboard | Layout |
|------|----------|--------|
| `90-leopold-fc900rw.hwdb` | FC900RW (USB `04B4:0510`) | CapsLock→Ctrl, RCtrl→CapsLock |
| `90-leopold-fc660mbt.hwdb` | FC660MBT (BT via Logitech `046D:B023`) | CapsLock↔Ctrl swap |

## Install

```bash
sudo cp *.hwdb /etc/udev/hwdb.d/
sudo systemd-hwdb update
sudo udevadm trigger
```

Changes take effect immediately for connected devices. Survives reboot.

## Uninstall

```bash
sudo rm /etc/udev/hwdb.d/90-leopold-*.hwdb
sudo systemd-hwdb update
sudo udevadm trigger
```

## Notes

- The FC660MBT rule matches the Logitech receiver vendor ID, not the
  Leopold itself. All keyboards on that receiver get the remap.
- The FC900RW rule matches the Cypress HID controller in the keyboard.
- HID usage codes are documented in the USB HID Usage Tables spec (§10,
  Keyboard/Keypad Page 0x07). The `0x700XX` prefix is Page 07, usage XX.
- Existing `x11/xprofile` and `x11/xinitrc` `setxkbmap` rules are
  redundant once the hwdb rules are active, but harmless to keep as a
  fallback for X sessions where hwdb isn't loaded.
