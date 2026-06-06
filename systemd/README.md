# systemd

Role: intentional system and user services and timers.

Facts:
- Cloud mount service keeps a remote filesystem available at a local path.
- Peer sync daemon runs as a user service.
- Snapshot timers run weekly and monthly for archival workflows.
- Whole-system Pi backup runs as a root oneshot service from a weekly timer.
  The tracked unit invokes the installed backup-drive script; machine-specific
  serials, labels, and current enablement state belong in the private
  restoration reference. The tracked weekly schedule and standard runtime paths
  are publishable policy and implementation conventions. Use a private mount
  namespace so target and source-view mounts are torn down by systemd even
  after forced termination. Keep the timer disabled until a manual backup and
  recovery drill have succeeded.
- The host agent service and its companion depend on local project virtualenvs outside dotfiles.
- Some services require local drop-ins for secrets. Track unit intent, not secret-bearing drop-ins.
Do not store:
- `*.service.d/secrets.conf`
- API keys, bot tokens, passwords, private env files, logs, or generated units.
