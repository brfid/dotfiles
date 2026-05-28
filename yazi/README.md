# yazi

Yazi should use a real local config directory, not a symlink back to this repo.
This folder is a rebuild capsule: it records durable Yazi preferences an LLM can
apply to `~/.config/yazi/` on the current machine.

Live path:
- `~/.config/yazi/`

Do not symlink `~/.config/yazi` to `~/src/dotfiles/yazi`. Copy, generate, or
edit real local config files instead. Runtime package state, downloaded flavors,
plugin files, caches, and generated files stay outside git.

## Durable Preferences

- Balanced three-pane layout: `[1, 1, 3]`
- Natural sorting, case-insensitive
- Directories first
- No line mode
- Scrolloff of 6
- Hidden files shown by default
- Wrapped previews
- `?` and `~` both open help
- Gruvbox dark flavor when installed

## Rebuild Snippets

`~/.config/yazi/yazi.toml`:

```toml
[mgr]
ratio = [1, 1, 3]
sort_by = "natural"
sort_sensitive = false
sort_dir_first = true
linemode = "none"
scrolloff = 6
show_hidden = true

[preview]
wrap = "yes"
image_delay = 80
image_filter = "triangle"
image_quality = 70
max_width = 900
max_height = 1400
```

`~/.config/yazi/keymap.toml`:

```toml
[mgr]
prepend_keymap = [
  { on = "?", run = "help", desc = "Open help" },
  { on = "~", run = "help", desc = "Open help" },
]
```

`~/.config/yazi/theme.toml`:

```toml
[flavor]
dark = "gruvbox-dark"
```

Install the flavor locally when needed:

```sh
ya pkg add bennyyip/gruvbox-dark
```
