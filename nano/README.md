# nano

Small terminal editor config for quick edits in Markdown, Python, YAML, JSON,
and JavaScript.

Live path:
- `nanorc` -> `~/.config/nano/nanorc`

Notes:
- Use soft wrapping, not hard wrapping, so long lines display comfortably
  without changing file contents.
- Wrap display at the terminal window width, prefer blank boundaries where
  possible, show line numbers, and show the minibar with constant cursor
  position.
- Use 2-column indentation and convert typed tabs to spaces.
- Include packaged nano syntax files from `/usr/share/nano/*.nanorc`; this
  covers the common text and code formats on Debian-style installs.
- The private restore note records the live path and capsule relationship only;
  these preferences are publishable.
