# reference

Host-level configs and templates that need manual review.

- `pi.md` — Raspberry Pi 5 home server: services, install steps,
  per-service notes.
- `edcloud.md` — EC2 cloud workstation: how it consumes this repo
  and where the rest of its host state is documented.
- `linux/<service>/` — `/etc/`-shaped files installed verbatim with
  sudo. Names mirror their target paths.
- `python/`, `templates/` — project templates, copied into new
  projects manually.

Never auto-apply `linux/`. For each file:

1. Diff against the live `/etc/` file.
2. Explain what the change does.
3. Ask before `sudo cp`.
4. Run `sudo systemctl daemon-reload` after systemd changes.
