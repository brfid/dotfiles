# pihole

Role: network-wide DNS ad blocker and local DNS server for the home network.

## Setup

Pi-hole installed via the official install script. Runs as `pihole-FTL.service` (systemd, enabled). Upstream is a local recursive resolver over DoT. Pi-hole does not do its own DNSSEC validation.

## PADD

Stats display script. Install:

```
curl -sSL https://install.padd.sh -o ~/padd.sh && chmod +x ~/padd.sh
sudo ln -s ~/padd.sh /usr/local/bin/padd
```

Update: `~/padd.sh -u`

## Do not store

- `pihole.toml` — machine-local runtime config; changes at runtime
- Gravity database, query logs, blocklists, DHCP leases
- Web interface password or API token
