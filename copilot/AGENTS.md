# copilot agent guide

## Purpose

This folder stores canonical GitHub Copilot CLI instructions and MCP config.

## Read first

- For repo-wide context, read `../AGENTS.md`.
- `sync.toml`
- `copilot-instructions.md`
- `mcp-config.json`

## Managed scope

Managed files:

- `copilot-instructions.md`
- `mcp-config.json`

## Import

- Import only managed files.
- Do not import `config.json`, command history, logs, installed plugin caches, restart markers, or session state.
- Treat plugin install details and trusted-folder history as runtime state unless user explicitly redesigns that boundary.

## Apply

- Apply only managed files.
- Static text files may be copied or linked. Use copy when unsure.
- Leave `config.json` and runtime trees unmanaged.

## Exclusions

Unmanaged live paths include command history, logs, installed plugins, session state, restart markers, IDE state, and mixed state in `config.json`.

## Verify

- Managed files exist in `~/.copilot`.
- Run `pytest`.
