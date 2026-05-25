# dotfiles+

Durable machine and tool configuration, plus reusable LLM agent config.

This repo is a systematic description of preferred setup, not a universal
symlink target. An LLM should use it to reconstruct or update local config on a
machine, adapting paths, package names, installed tools, and runtime state to
the current environment.

Each root folder owns its own setup capsule in `README.md`. A capsule should
record durable preferences, roles, live paths, dependencies, source-vs-state
boundaries, and high-value snippets that would be hard or ambiguous for a
strong model to infer.

Track exact config files only when they are durable, portable, secret-free, and
more precise than prose. Prefer compact rebuild facts for stateful tools or
machine-local systems. Do not track generated config, credentials, logs, caches,
sessions, private paths, machine inventories, package/plugin state, or lockfiles
that belong to local runtime setup.

The `agents/` folder owns reusable LLM personas, rules, and instructions. Local
LLM client config is generated output; do not symlink client config back to this
repo unless explicitly requested.
