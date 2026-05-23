# rclone

Role: cloud remote used by sync and backup services.

Facts:
- Remote names currently present: `dropbox`, `gdrive`.
- `rclone-dropbox.service` depends on `dropbox:` and mounts it at `%h/Dropbox`.
- The gdrive backup cron job depends on the Google Drive remote.
- Live rclone config is credential-bearing state, not source config.

Do not store:
- `~/.config/rclone/rclone.conf`
- OAuth tokens, refresh tokens, account IDs, mount caches, or logs.
