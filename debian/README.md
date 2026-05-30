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

Non-APT local binaries:
- `sops` from the upstream getsops release binary. Verify downloaded artifacts
  against the published release checksum before installing.

## Kernel tuning

Sysctl customizations for hardening and storage longevity. Swappiness set to 10.
