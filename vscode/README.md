# vscode

VS Code configuration. GitHub settings sync manages the live `settings.json`;
this capsule documents setup and non-obvious preferences.

Live path: `~/.config/Code/User/settings.json`

## Installation

```sh
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=arm64 signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update && sudo apt install code
```

## Key Decisions

**Python tooling**: Uses black/isort/flake8 @ 100 chars to match CI. Ruff is
disabled to avoid formatter disagreements. Type checking set to standard.

**TypeScript**: Uses Biome for formatting (not Prettier). Format and organize
imports on save.

**Font size**: 15px across all surfaces (editor, terminal, chat, debug, etc.).
Applied to all profiles via `workbench.settings.applyToAllProfiles`.

**Themes**: Ayu Light Bordered (light) / Ayu Mirage Bordered (dark). Auto-detect
system theme. Material Icon Theme with Angular pack.

**Git**: Smart commit enabled, autofetch on, no parent folder repo detection.
GitHub authentication disabled (uses CLI auth instead).

**AI tools**: Claude Code configured for terminal use. AI features disabled by
default. GitLab Duo disabled.

**Spell checker**: Domain words added (networking/security: BGP, DNSSEC, RPKI,
OSINT, pentest, etc.).

## Extensions

Settings sync restores the full list. For fresh installs before sync:

- `ms-python.python`, `ms-python.black-formatter`, `ms-python.isort`, `ms-python.flake8`
- `biomejs.biome`
- `pkief.material-icon-theme`
- `streetsidesoftware.code-spell-checker`
- `redhat.vscode-yaml`
- `ms-vscode-remote.remote-ssh` (optional)
