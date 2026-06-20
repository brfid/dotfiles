# colors

Personal color overrides shared across VS Code and iTerm2. No theme extension:
applied by hand or via LLM on top of stock built-in themes, auto-switching with
macOS appearance.

## Principle

- Orange = interface chrome: buttons, badges, borders, selection, cursor, focus.
- Green = text and markup: headings, sidebar/nav text, inline `code`.
- Code syntax stays stock (no per-token palette).

## Roles

| Role | Dark | Light |
|------|------|-------|
| Chrome primary (buttons, borders, cursor, focus) | `#FD7E14` | `#E58200` |
| Chrome highlight (links, active line, match) | `#E89556` | `#8A3A00` |
| On-accent text | `#0A0A0A` | `#0A0A0A` |
| Heading / markup green | `#2EA82E` | `#116329` |
| Nav + inline-code green | `#83C683` | `#15692E` |
| Terminal foreground | `#D4753A` | `#D4753A` |

## VS Code

Baseline: built-in `Dark 2026` / `Light 2026` themes (`theme-defaults`
v10.0.0), not Dark/Light Modern. Overrides live in `settings.json` under
`workbench.colorCustomizations` and `editor.tokenColorCustomizations`, scoped
`[Dark 2026]` / `[Light 2026]`. Settings Sync owns the live file. If Microsoft
renames the theme ID, re-scope those blocks.

Light carries a deliberate extra contrast layer (deeper greens, darker UI label
text, stronger selection washes) absent in dark; dark uses slightly lifted,
less-saturated tones on near-black to avoid haloing.

## iTerm2

See `../iterm2`. Accent colors match the table; ANSI 0–15 stays GitHub-derived
for readability.
