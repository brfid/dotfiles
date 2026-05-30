# dotfiles+

An LLM-first build spec for machine and tool configuration, plus reusable LLM agent config.

This repo is a systematic description of preferred setup, not a universal
symlink target. An LLM should use it to reconstruct or update local config on a
machine, adapting paths, package names, installed tools, and runtime state to
the current environment.

Each root folder owns its own setup capsule in `README.md`. A capsule should
record durable preferences, roles, live paths, dependencies, source-vs-state
boundaries, and high-value snippets that would be hard or ambiguous for a
strong model to infer.

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

Machine-specific values (hostnames, ports, IPs, cron schedules, partition
labels, interface names, service unit names) live in a private restoration
reference outside this repo. Capsules here describe intent and conventions only.
