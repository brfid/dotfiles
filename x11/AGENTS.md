# x11 agent guide

## Purpose

This folder stores canonical user X11 startup glue.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `xprofile`
- `xinitrc`

## Managed scope

Managed files:

- `xprofile`
- `xinitrc`
- `lxsession/LXDE-pi/autostart`

## Import

- Import only tracked files.
- Do not import `~/.xsessionrc` or other ad hoc X session files unless user explicitly decides to manage them here.
- Keep keyboard-remap policy aligned with `reference/linux/keyboard/`; do not reintroduce `setxkbmap` hacks here.

## Apply

- Apply `xprofile` to `~/.xprofile`, `xinitrc` to `~/.xinitrc`, and
  `lxsession/LXDE-pi/autostart` to `~/.config/lxsession/LXDE-pi/autostart`
  by copy or link.
- Use copy when unsure.

## Exclusions

Unmanaged live paths include `~/.xsessionrc`, Xorg logs, and other session/runtime files.

## Verify

- `~/.xprofile` and `~/.xinitrc` exist.
- `~/.config/lxsession/LXDE-pi/autostart` exists and does not run
  `setxkbmap`.
- Run `pytest`.
