# iterm2

2026 Dark/Light terminal colors matching the VS Code roles (`../colors`).
Accent colors (foreground, cursor, selection, link, badge) are orange/green;
ANSI 0–15 stays GitHub-derived for readability.

Applied by hand or via LLM — no preset file is tracked. New-window defaults:
Monaco 15, 214x55.

## Palette

| Key | Dark | Light |
|-----|------|-------|
| Background | `#191A1B` | `#FAFAFD` |
| Foreground | `#D4753A` | `#D4753A` |
| Bold | `#FFFFFF` | `#8A3A00` |
| Cursor | `#FD7E14` | `#202020` |
| Cursor text | `#191A1B` | `#FAFAFD` |
| Selection | `#FD7E14` | `#E58200` |
| Selected text | `#FFFFFF` | `#FFFFFF` |
| Link | `#E89556` | `#8A3A00` |
| Badge | `#FD7E14AA` | `#E58200AA` |
| Cursor guide | `#FD7E1433` | `#E5820033` |
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

## Applying

iTerm rewrites its plist from memory on quit, so edit only while it's closed:

1. Quit iTerm2.
2. Patch `~/Library/Preferences/com.googlecode.iterm2.plist` (back it up first).
3. Reopen.

Plist mechanics: each color is a dict of sRGB float components (`Red/Green/Blue/Alpha
Component`, 0–1), not hex. Profiles live under `New Bookmarks`. For appearance
auto-switching, set `Use Separate Colors for Light and Dark Mode = true` and
write each color under both `"<Key> (Dark)"` and `"<Key> (Light)"`; the bare key
is the fallback when that flag is off.
