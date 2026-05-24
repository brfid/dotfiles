# debian

Role: OS-level preferences for Debian installs.

## Base

Debian Trixie (13). Unattended upgrades enabled, security-only.

## Firewall

UFW active, default deny incoming.

## APT

Third-party package origins pinned via APT preferences where needed.

## Kernel tuning

Sysctl customizations for hardening and storage longevity. Swappiness set to 10.
