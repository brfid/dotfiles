# Troubleshooting

## signal-cli device linking

### Symptoms

- **"QR code is not valid"** — phone scans QR but Signal rejects it immediately
- **"Linking device failed / invalid response from service"** — phone connects to Signal servers but handshake fails
- **"Link request error: Connection closed!"** — signal-cli log shows WebSocket closing after ~60 seconds

### Root causes identified (March 2026)

Signal's provisioning WebSocket closes after **60 seconds**. The phone must scan *and* complete the handshake within that window. Repeated failed attempts within a session trigger server-side rate limiting, which causes subsequent attempts to fail even if timing is fine.

The `sgnl://linkdevice?uuid=...&pub_key=...` URI format is still current (the old `tsdevice:/` format is deprecated but `sgnl://linkdevice` is correct as of signal-cli 0.14.1).

### Checklist before attempting

1. Check **Settings > Linked Devices** on your phone — Signal allows max 5 linked devices.
2. Pre-navigate to **Settings > Linked Devices > +** *before* starting `signal-setup`.
3. If you've had multiple failed attempts, **wait 30–60 minutes** for rate limiting to clear.

### Best linking procedure

```bash
# Generate QR and open it in a browser (better rendering than feh)
~/dotfiles/scripts/signal-setup.sh
# or manually:
rm -f /tmp/signal-link.log /tmp/signal-qr.png
signal-cli link --name "rpi" > /tmp/signal-link.log 2>&1 &
SPID=$!
while ! grep -q '^sgnl://' /tmp/signal-link.log 2>/dev/null; do sleep 0.1; done
grep '^sgnl://' /tmp/signal-link.log | qrencode -t PNG -s 15 -l H -o /tmp/signal-qr.png
DISPLAY=:0 chromium /tmp/signal-qr.png &   # or: firefox, feh
echo "Scan now — 60s window. PID: $SPID"
wait $SPID; echo "Exit: $?"
cat /tmp/signal-link.log
```

Key flags: `-s 15` (larger modules) and `-l H` (high error correction) improve scan reliability.

### If it still fails

- Try a different device name: `signal-setup --name "mypi"` — some reports suggest non-default names succeed where defaults fail.
- Open the PNG in a browser (`chromium` / `firefox`) rather than `feh`; browsers render at full quality.
- Check that `DISPLAY=:0` is set if running from a tmux session without a display.
- Wait until the next day and try fresh — Signal's provisioning endpoint has known flakiness with third-party clients.

### References

- [signal-cli-rest-api #651](https://github.com/bbernhard/signal-cli-rest-api/issues/651) — "QR code not valid" on Android, Jan 2025+
- [AsamK/signal-cli #1567](https://github.com/AsamK/signal-cli/issues/1567) — "Connection closed" during provisioning
- [AsamK/signal-cli #190](https://github.com/AsamK/signal-cli/issues/190) — "Linking Device Failed" history
