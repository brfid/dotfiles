# cron

Role: sparse personal schedules that have not moved to user systemd timers.

Facts:
- Cron remains intentional alongside user systemd timers.
- A weekly job runs cloud backup in archive mode.
- An hourly job runs the host agent heartbeat.
- The live crontab loads local secret env with `BASH_ENV`; keep that env outside git.

Do not store:
- Secrets, private env files, or private project paths.
