# debian

Role: OS-level preferences for Debian installs.

## Base

Debian Trixie (13). Unattended upgrades enabled, security-only.

## Firewall

UFW active, default deny incoming.

## APT

Third-party package origins pinned via APT preferences where needed.

Packages added for local secret handling:
- `age`

Non-APT local binaries:
- `sops` is installed at `/usr/local/bin/sops` from the upstream getsops
  Linux arm64 release binary. Verify downloaded artifacts against the published
  release checksum before installing.

## Kernel tuning

Sysctl customizations for hardening and storage longevity. Swappiness set to 10.
