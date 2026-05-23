# OpenCode adapter

Agent policy, private agents, and private skills live in `~/src/agents`.

OpenCode consumes them by symlink:

```text
~/.config/opencode/agents -> ~/src/agents/opencode/agents
~/.config/opencode/skills -> ~/src/agents/skills
```

Shared policy lives in `~/src/agents/policy/`. OpenCode agent markdown files
embed only the rules needed by that agent.

- Keep auth, session state, node modules, generated config, package locks, and
  plugin caches out of git.
