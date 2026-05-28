# unbound

Role: local DNS resolver forwarding to Quad9 over DoT, sitting between Pi-hole and the internet.

## Setup

Installed via apt (`unbound`, `dns-root-data`). Runs as `unbound.service` (systemd, enabled).
Config drop-in at the standard unbound conf.d path.

Listens on `127.0.0.1:<port>`. Pi-hole points its upstream here.

## Architecture

```
Pi-hole :53 → Unbound localhost:<port> → Quad9 DoT :853
```

ISP sees only encrypted TLS to Quad9. Quad9 sees queries but not the
client IP (anycast). Quad9 chosen for: Swiss non-profit, no-log, DNSSEC
validation, built-in threat blocking.

## Key config decisions

**Forwarder mode, not recursive.** Unbound forwards to Quad9 rather than
resolving from root servers. Faster, benefits from Quad9's anycast and threat
blocking.

**`module-config: "iterator"`** — critical for forwarder mode. The default
`"validator iterator"` causes Unbound to re-validate DNSSEC on top of Quad9's
own validation, producing spurious BOGUS failures. Drop the validator; let
Quad9 handle it.

**`qname-minimisation: no`** — only useful in recursive mode; generates extra
spurious queries when forwarding.

**`edns-buffer-size: 1232`** — reduces IP fragmentation. Old guides say 4096;
1232 is correct for modern deployments.

Cache: `msg-cache-size 50m`, `rrset-cache-size 100m`, `prefetch yes`.

## Do not store

- `/var/lib/unbound/root.key` — managed at runtime by `unbound-anchor`
- Unbound cache or runtime state
