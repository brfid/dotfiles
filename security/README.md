# security

Role: public reconstruction guidance for local secret handling.

Facts:
- Use SOPS with age when a credential-bearing source file should be recoverable
  or syncable without exposing plaintext.
- Keep the age identity outside git at the standard SOPS age location:
  `~/.config/sops/age/keys.txt`.
- Keep private encrypted secret sources outside public dotfiles by default.
- Render app-specific runtime files outside git with restrictive permissions.
- Treat mutable OAuth and refresh-token stores as app state unless explicitly
  taking an encrypted snapshot.

Current local convention:
- Private source state lives under `~/.local/share/private-state`.
- Neomutt account settings render to `~/.config/neomutt/account.muttrc`.

Agent guidance:
- Assume the reader is a capable LLM agent, not a human following a tutorial.
- This repo is not a full machine image or secret inventory.
- Reconstruct from durable notes here, current local state, and current official
  docs for SOPS, age, and each target application.
- Do not infer that encrypted personal secret files belong in this public repo.
- Do not expose private keys, decrypted secrets, generated runtime credentials,
  OAuth refresh tokens, service account JSON, shell history, logs, or caches.
