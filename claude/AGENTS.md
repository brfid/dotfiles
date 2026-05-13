# claude

Claude Code config. See `sync.toml`.

Copy (don't symlink) `plugins/.claude-plugin/marketplace.json` into
`~/.claude/plugins/`; that tree mixes managed and runtime state.

Keep private workspace access (`additionalDirectories`) in
`~/.claude/settings.local.json`, not in tracked settings. Never import
`.credentials.json`, plugin install state, marketplace cache, file
history, or debug output.
