# cron

Role: sparse personal schedules that have not moved to user systemd timers.

Facts:
- Cron remains intentional alongside user systemd timers.
- A weekly job runs cloud backup in archive mode.
- An hourly job runs the host agent heartbeat.
- The live crontab loads local secret env with `BASH_ENV`; keep that env outside git.

Overnight staggering (2–3–4 AM):
- One job per hour to avoid I/O contention on Pi 5.
- 2:00 hermes backup, 3:00 pihole gravity, 4:00 e2scrub.
- e2scrub moved from Debian default (3:10) to 4:00 for clean separation.

Do not store:
- Secrets, private env files, or private project paths.
