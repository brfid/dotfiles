# rclone

Role: cloud remotes used by sync and backup services.

Facts:
- Cloud mount and backup services depend on configured rclone remotes.
- Live rclone config is credential-bearing state, not source config.

Do not store:
- `~/.config/rclone/rclone.conf`
- OAuth tokens, refresh tokens, account IDs, mount caches, or logs.
