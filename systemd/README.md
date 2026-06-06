# systemd

Role: intentional system and user services and timers.

Facts:
- Cloud mount service keeps a remote filesystem available at a local path.
- Peer sync daemon runs as a user service.
- Snapshot timers run weekly and monthly for archival workflows.
- Whole-system Pi backup is a weekly root oneshot with a private mount
  namespace. Keep its timer disabled until a manual backup and recovery drill
  succeed. The canonical design and rebuild procedure is in `pi/README.md`;
  machine identity and enablement state are private restoration data.
- The host agent service and its companion depend on local project virtualenvs
  outside dotfiles.
- Some services require local drop-ins for secrets. Track unit intent, not
  secret-bearing drop-ins.
- Bluetooth backup runs as a root oneshot from a daily timer; restore runs at
  boot after bluetooth.service.
  See `bluetooth/` for the scripts and the Pi 5 adapter workaround.

Do not store:
- `*.service.d/secrets.conf`
- API keys, bot tokens, passwords, private env files, logs, or generated units.
