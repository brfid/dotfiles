# systemd

Role: intentional user services and timers.

Facts:
- Cloud mount service keeps a remote filesystem available at a local path.
- Peer sync daemon runs as a user service.
- Snapshot timers run weekly and monthly for archival workflows.
- The host agent service and its companion depend on local project virtualenvs outside dotfiles.
- Some services require local drop-ins for secrets. Track unit intent, not secret-bearing drop-ins.

Do not store:
- `*.service.d/secrets.conf`
- API keys, bot tokens, passwords, private env files, logs, or generated units.
