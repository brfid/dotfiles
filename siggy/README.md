# siggy

Role: local helper CLI.

Facts:
- The executable is expected at `~/.local/bin/siggy`.
- Live TOML config exists, but its fields have not been classified as durable public config versus private machine data.

Do not store:
- Credentials, private endpoints, private file paths, generated output, or logs.
