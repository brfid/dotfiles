# Rules

Apply these when generating local LLM client config.

## Local Config

- Generate local client config from this repo (`~/src/dotfiles`).
- Do not treat local client config as source of truth.
- Do not add symlinks back to this repo unless explicitly requested.
- Preserve managed blocks in local files.

## Communication

- No flattery, pleasantries, hedging, or filler.
- Be concise.
- Challenge weak assumptions or risky choices.
- Present alternatives and trade-offs when they matter.

## Git

- `git commit` and `git push` require explicit approval.
- Approval is also required for force-push, history rewrite, remote branch or tag deletion, non-current-branch push, and non-`origin` push.
- Never use `--no-verify`.
- Commit subjects use Conventional Commits:
  `type[(scope)]: imperative phrase`.
- Commit bodies explain why and impact.
- Do not add agent attribution lines or emoji.

## Act vs Propose

- Propose first when the request is ambiguous, affects multiple files or systems, has side effects, or asks to discuss/propose/report back.
- Act directly for clear single-file edits, read-only exploration, tests, linting, or an approved plan.
