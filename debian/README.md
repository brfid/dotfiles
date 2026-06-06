# debian

Role: OS-level preferences for Debian installs.

## Base

Unattended upgrades enabled, security-only.

## Firewall

UFW active, default deny incoming.

## APT

Third-party package origins pinned via APT preferences where needed.

Packages added for local secret handling:
- `age`

Bluetooth/audio packages:
- `bluez`
- `blueman`
- `pi-bluetooth`
- `libspa-0.2-bluetooth`
- `pipewire`
- `pipewire-pulse`
- `wireplumber`

Desktop packages:
- `xfce4`
- `xfce4-goodies`
- `network-manager-gnome`
- `pavucontrol`

LightDM defaults to XFCE. Openbox remains installed as a fallback session.

Non-APT local binaries:
- `sops` from the upstream getsops release binary. Verify downloaded artifacts
  against the published release checksum before installing.

## Kernel tuning

Sysctl customizations for hardening and storage longevity. Swappiness set to 10.
