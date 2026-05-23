# dotfiles+

Durable machine and tool configuration, plus reusable LLM agent config.

Each root folder owns its setup notes in its own `README.md`. The `agents/` folder owns personas, rules, and instructions that apply across LLM clients.

An LLM adapts this repo into local config for the current machine. Local client config is generated output, not source of truth.

Prefer compact rebuild facts over copied runtime config. Track exact files only when they are durable, secret-free preferences. For stateful tools, record the role, live paths, intentional names, dependencies, and source-vs-state boundary.
