# cron

Role: sparse personal schedules that have not moved to user systemd timers.

Facts:
- Cron remains intentional alongside user systemd timers.
- Weekly Sunday 03:00 job runs gdrive backup archive mode and logs as `gdrive-backup`.
- Hourly job runs the Jean-Claude heartbeat and logs through `logger` with tag `<heartbeat-tag>`.
- Backup cron depends on the rclone `gdrive` remote.
- The live crontab loads local secret env with `BASH_ENV`; keep that env outside git.
- Current live cron references `~/src/dotfiles/scripts/gdrive_backup.py`, but this repo does not currently contain that script. Resolve before relying on a rebuild from this repo.

Do not store:
- Secrets, private env files, or private project paths.
