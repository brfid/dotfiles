# pihole

Role: network-wide DNS ad blocker and local DNS server for the home network.

## Setup

Pi-hole installed via the official install script. Runs as `pihole-FTL.service` (systemd, enabled). Upstream is a local recursive resolver over DoT. Pi-hole does not do its own DNSSEC validation.

Pi-hole v6 uses the FTL built-in web server and stores runtime settings in
`/etc/pihole/pihole.toml`. Keep the live TOML local; document durable defaults
here and exact host values in the private restoration reference.

Keep iCloud Private Relay special-domain handling enabled so Apple devices do
not bypass Pi-hole on the home network. Pi-hole should answer the Apple relay
canary domains with NXDOMAIN, matching Apple's network-operator guidance.

Gravity blocklist refresh is scheduled externally. Prefer a small dedicated
`/etc/cron.d` snippet that runs only `pihole updateGravity`; do not restore the
bundled disabled Pi-hole cron file wholesale.

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
