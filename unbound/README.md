# unbound

Role: local DNS forwarder with DoT upstream, sitting between Pi-hole and the internet.

## Setup

Installed via apt (`unbound`, `dns-root-data`). Runs as `unbound.service` (systemd, enabled). Config drop-in at `/etc/unbound/unbound.conf.d/`.

## Key config decisions

**Forwarder mode, not recursive.** Forwards to an upstream resolver rather than
resolving from root servers. Faster, benefits from upstream anycast and threat
blocking.

**`module-config: "iterator"`** — critical for forwarder mode. The default
`"validator iterator"` causes Unbound to re-validate DNSSEC on top of the
upstream's own validation, producing spurious BOGUS failures. Drop the
validator; let the upstream handle it.

**`qname-minimisation: no`** — only useful in recursive mode; generates extra
spurious queries when forwarding.

**`edns-buffer-size: 1232`** — reduces IP fragmentation. Old guides say 4096;
1232 is correct for modern deployments.

## Do not store

- `/var/lib/unbound/root.key` — managed at runtime by `unbound-anchor`
- Unbound cache or runtime state
- The live config file (machine-specific values live in private restoration reference)
