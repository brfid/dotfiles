# neomutt

Neomutt is configured for a Gmail-backed account with cached headers, HTML rendering, server-side search, and a light orange/green theme.

Live paths:
- `neomuttrc` -> `~/.config/neomutt/neomuttrc`
- `mailcap` -> `~/.config/neomutt/mailcap`

Notes:
- Account settings are generated into `~/.config/neomutt/account.muttrc`.
- The source secret is `~/src/dotfiles/secrets/neomutt.sops.yaml`.
- Render account settings with
  `~/src/dotfiles/secrets/render-neomutt-account`.
- Account credentials and mail cache stay outside git.
