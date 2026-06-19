# dotfiles+

A showcase of my configuration stack and preferences, plus reusable LLM agent config.

Each root folder owns a `README.md` capsule documenting what I use and why.
Capsules record durable preferences, design rationale, and high-value snippets
that would be hard or ambiguous for a strong model to infer. An LLM can use
these to reconstruct or update local config, adapting to the current
environment.

Include config files or snippets only when prose would not get a SOTA model to
a working result within a few iterations. Strip system-identifying details
before committing — hostnames, usernames, and local addresses are excluded by
default. Benign details are harmful in aggregate: individually minor, they
collectively form a system fingerprint. Use generic placeholders where specific
values are needed for context.

Do not track generated config, credentials, logs, caches, sessions, private
paths, machine inventories, package/plugin state, or lockfiles that belong to
local runtime setup.

The `agents/` folder owns reusable LLM personas, rules, and instructions. Local
LLM client config is generated output; do not symlink client config back to this
repo unless explicitly requested.

Machine-specific values (hostnames, ports, partition labels, etc.) live on the
machine itself and are preserved by the system backup. This repo documents
stack choices and conventions, not machine inventory.
