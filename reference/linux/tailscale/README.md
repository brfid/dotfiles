# Tailscale

Reference only.
Keep non-secret rebuild details here.
Do not commit auth keys, peer inventory, or `/var/lib/tailscale/` state.

## Current shape

- Hostname: `jean-claude`
- Remote access path: Tailscale
- MagicDNS / accept-dns: enabled
- Exit node: none
- Advertised routes: none
- Advertised tags: none
- Tailscale SSH: disabled
- `/etc/default/tailscaled`: `PORT="41641"`, `FLAGS=""`

## Rebuild

```bash
sudo tailscale up --hostname=jean-claude
```

## Verify

```bash
tailscale status
tailscale ip -4
tailscale ip -6
tailscale debug prefs
```

SMB depends on `../samba/smb.conf.pi`.
That file allows only localhost plus tailnet ranges.
