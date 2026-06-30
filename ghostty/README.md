# ghostty

2026 Dark/Light terminal colors matching the VS Code roles (`../colors`).
Accent colors (foreground, cursor, selection) are orange; ANSI 0–15 stays
GitHub-derived for readability.

Font: Monaco 15. Window default: 214×55.

macOS appearance auto-switch via `theme = dark:2026-dark,light:2026-light`.

## Palette

| Key | Dark | Light |
|-----|------|-------|
| Background | `#191A1B` | `#FAFAFD` |
| Foreground | `#D4753A` | `#D4753A` |
| Cursor | `#FD7E14` | `#202020` |
| Cursor text | `#191A1B` | `#FAFAFD` |
| Selection | `#FD7E14` | `#E58200` |
| Selected text | `#FFFFFF` | `#FFFFFF` |
| ANSI 0 black | `#191A1B` | `#202020` |
| ANSI 1 red | `#ff7b72` | `#cf222e` |
| ANSI 2 green | `#2EA82E` | `#116329` |
| ANSI 3 yellow | `#ffa657` | `#953800` |
| ANSI 4 blue | `#79c0ff` | `#0550ae` |
| ANSI 5 magenta | `#d2a8ff` | `#8250df` |
| ANSI 6 cyan | `#a5d6ff` | `#0a3069` |
| ANSI 7 white | `#bfbfbf` | `#6e7781` |
| ANSI 8 br black | `#8b949e` | `#57606a` |
| ANSI 9 br red | `#ffa198` | `#a40e26` |
| ANSI 10 br green | `#56d364` | `#1a7f37` |
| ANSI 11 br yellow | `#e3b341` | `#d18616` |
| ANSI 12 br blue | `#79c0ff` | `#218bff` |
| ANSI 13 br magenta | `#d2a8ff` | `#a475f9` |
| ANSI 14 br cyan | `#a5d6ff` | `#3192aa` |
| ANSI 15 br white | `#ededed` | `#FFFFFF` |

## Live paths

- `~/.config/ghostty/config`
- `~/.config/ghostty/themes/2026-dark`
- `~/.config/ghostty/themes/2026-light`

## terminfo (sudo nano / vi "unknown terminal type")

Ghostty sets `TERM=xterm-ghostty`, but macOS's `/usr/share/terminfo` is
SIP-protected and ships no such entry, so `sudo nano /etc/hosts` (and any
program run as root) fails with `'xterm-ghostty': unknown terminal type`.

Fix — compile the entry from the app bundle into the per-user terminfo dirs
(your user, then root so `sudo`-launched programs resolve it):

```
src=/Applications/Ghostty.app/Contents/Resources/terminfo
TERMINFO=$src infocmp -x xterm-ghostty > /tmp/ghostty.terminfo
tic -x -o ~/.terminfo /tmp/ghostty.terminfo
sudo tic -x -o /var/root/.terminfo /tmp/ghostty.terminfo
```

The per-user dirs are the only writable target — `/usr/share/terminfo` is
SIP-protected even for root. The entries survive Ghostty app updates; re-run
after a user reset. Stopgap without installing: `TERM=xterm-256color sudo nano ...`.

## Notes

- `eza --icons` glyphs require a Nerd Font. Monaco has none, matching the
  existing iTerm2 setup. Add a second `font-family = "Symbols Nerd Font Mono"`
  line in `config` if you install one.
- The `t()` shell helper's iTerm2 `-CC` control-mode path is inert under
  Ghostty; plain tmux attach runs instead. No config change needed.
