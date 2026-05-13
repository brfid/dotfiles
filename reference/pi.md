# pi

Raspberry Pi 5 home server. Debian/Raspberry Pi OS.

## Role

LAN DNS (Pi-hole), file share (Samba over Tailscale), local sandbox.
No public inbound; remote access is Tailscale.

## Tracked references for this host

| Path                                       | Purpose                                  |
| ------------------------------------------ | ---------------------------------------- |
| `linux/keyboard/90-leopold-fc900rw.hwdb`   | Leopold FC900RW keyboard remap (hwdb)    |
| `linux/pihole/pihole-custom.toml`          | Pi-hole DNS / local config snippet       |
| `linux/unbound/unbound.conf*`              | Recursive resolver (currently disabled)  |
| `linux/samba/smb.conf.pi`                  | SMB share, tailnet-only ACL              |
| `linux/ufw/user.rules`                     | Firewall rules                           |
| `linux/cpufreq/*`                          | ondemand governor tuning                 |
| `linux/swap/dphys-swapfile`                | swap size                                |
| `linux/lightdm/lightdm.conf.d/99-local.conf` | display manager local override         |
| `linux/crontab/crontab.pi`                 | user crontab template                    |
| `linux/fstab/fstab.pi`                     | mount table template                    |
| `linux/logrotate/*`                        | per-service log rotation                 |
| `linux/rsnapshot/rsnapshot.conf`           | local backup config                      |

PII rule: never commit real LAN/ULA/link-local/Tailscale addresses.
Use placeholders (`<pi_lan_ip>`, `<lan_cidr>`, `<tailnet_suffix>`).

## Keyboard remap (Leopold FC900RW, USB `04B4:0510`)

Maps `Caps Lock` ↔ `Right Ctrl`, leaves `Left Ctrl` alone. Use a
`systemd-hwdb` rule, not `setxkbmap` — hwdb covers tty, LightDM, X11,
Wayland, and survives login.

```bash
sudo install -Dm0644 reference/linux/keyboard/90-leopold-fc900rw.hwdb \
  /etc/udev/hwdb.d/90-leopold-fc900rw.hwdb
sudo systemd-hwdb update
sudo udevadm trigger --subsystem-match=input
# If the old map persists, unplug/replug the keyboard.

# Verify
systemd-hwdb query 'evdev:input:b0003v04B4p0510*'
# Expect:
#   KEYBOARD_KEY_70039=leftctrl
#   KEYBOARD_KEY_700e4=capslock
```

LXDE on the Pi defaults to `setxkbmap -option ctrl:swapcaps`, which
double-remaps on top of hwdb. Apply the managed override:

```bash
install -Dm0644 ../x11/lxsession/LXDE-pi/autostart \
  ~/.config/lxsession/LXDE-pi/autostart
```

## Pi-hole

This host serves LAN DNS. Pi-hole owns the live config; this repo
holds reference snippets only.

Intent:

- Cloudflare upstreams.
- Forward the tailnet MagicDNS suffix to Tailscale DNS.
- Unbound stays disabled unless recursive DNS is intentionally
  restored (see below).
- Router DHCP/RA advertises only the Pi-hole address for DNS.

Resolver shape on this host:

```text
nameserver 127.0.0.1
nameserver 1.1.1.1
nameserver 1.0.0.1
```

Live checks:

```bash
sudo pihole-FTL --config dns.upstreams
sudo pihole-FTL --config dns.interface
dig @<pi_lan_ip> pi.hole
dig @127.0.0.1 <tailnet_peer>.<tailnet_suffix>
sudo pihole-FTL dhcp-discover
```

## Tailscale

- Hostname: `<pi_hostname>`.
- `accept-dns=false` on this host so NetworkManager owns
  `/etc/resolv.conf`; Pi-hole handles split DNS for the tailnet.
- No exit node, no advertised routes/tags. Tailscale SSH disabled.
- `/etc/default/tailscaled`: `PORT="41641"`, `FLAGS=""`.

```bash
sudo tailscale up --hostname=<pi_hostname>
sudo tailscale set --accept-dns=false
tailscale status
```

SMB ACL in `linux/samba/smb.conf.pi` allows only localhost plus
tailnet ranges.

## Unbound (disabled)

Not part of the current DNS path. If recursive DNS is restored:

- Run on loopback `127.0.0.1#5335`.
- Point Pi-hole's upstream at it.

```bash
systemctl is-enabled unbound.service
systemctl is-active unbound.service
sudo pihole-FTL --config dns.upstreams
```
