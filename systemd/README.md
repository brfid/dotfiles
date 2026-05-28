# systemd

Role: intentional user services and timers.

Facts:
- Keep `rclone-dropbox.service` and `syncthing.service` enabled.
- `rclone-dropbox.service` mounts rclone remote `dropbox:` at `%h/Dropbox`.
- Keep `edc-weekly-snapshot.timer` and `edc-monthly-snapshot.timer` enabled for snapshot workflow coverage.
- Weekly EDC snapshot runs Sunday 03:15 into `weekly-snapshot`; monthly snapshot runs on day 1 at 00:00 into `monthly-snapshot`.
- EDC units load `%h/.config/edcloud/edc.env` and run `%h/.local/bin/edc`.
- The host agent service and its MCP companion service depend on local project virtualenvs outside dotfiles.
- OpenClaw services require local drop-ins for secrets. Track unit intent, not secret-bearing drop-ins.

Do not store:
- `*.service.d/secrets.conf`
- API keys, bot tokens, passwords, private env files, logs, or generated units.
