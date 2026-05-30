# node

Role: minimal JavaScript and Node.js development setup.

Use a current LTS or newer Node.js with npm available. Project dependencies,
test tools, lint tools, lockfiles, and framework-specific configuration belong
in the projects that use them.

## npm

Delay newly published package versions during dependency resolution:

```sh
npm config set min-release-age 7
```

Verify:

```sh
npm config get before
```

This keeps npm from selecting package versions published in the last 7 days
when resolving installs, updates, and lockfile changes. npm stores the relative
policy in `~/.npmrc` as `min-release-age=7` and reports the effective cutoff as
a derived `before` timestamp.

`npm ci` follows the existing lockfile. Project `.npmrc` files, environment
variables, and command-line flags can override the user config.

## Boundaries

Keep runtime and project state out of this repo:

- `node_modules`
- npm caches
- generated build output
- `.env` files
- service tokens and npm auth tokens
- project lockfiles
