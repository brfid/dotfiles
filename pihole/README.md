# pihole

Role: network-wide DNS ad blocker and local DNS server for the home network.

## Setup

Pi-hole v6 (FTL + built-in web server), installed via the official install script.
Runs as `pihole-FTL.service` (systemd, enabled).

Listens on the local interface, port 53. Web interface on a non-standard port.

## DNS upstream

Upstream is Unbound on localhost. Pi-hole does not do its own DNSSEC
validation — Unbound delegates that to Quad9.

## Home network DNS addresses

Configure these on the router as the DNS server for all clients:

- IPv4: `<pi-local-ip>`
- IPv6: `<pi-local-ipv6-static>` (ULA, static — ends in `::19`; prefer over the dynamic ULA or public GUA)

## Do not store

- `pihole.toml` — machine-local runtime config; changes at runtime
- Gravity database, query logs, blocklists, DHCP leases
- Web interface password or API token
