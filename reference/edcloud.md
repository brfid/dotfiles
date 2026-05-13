# edcloud

EC2 cloud workstation. Single-instance Ubuntu 24.04 lab provisioned by
the [`brfid/edcloud`](https://github.com/brfid/edcloud) repo. Tailscale
is the only access path; no public inbound.

## How it consumes this repo

Cloud-init clones this repo into `~/src/dotfiles` on every
`edc provision` / `edc reprovision`. The repo URL and branch are
configurable on the edcloud side:

- `edc provision --dotfiles-repo <url> --dotfiles-branch <branch>`
- `EDCLOUD_DOTFILES_REPO`, `EDCLOUD_DOTFILES_BRANCH`
- Default `--dotfiles-repo auto` resolves to
  `https://github.com/<gh-user>/dotfiles.git`, then the persisted
  origin of `~/src/dotfiles` if present.

After clone, an LLM agent links the relevant `<tool>/sync.toml`
entries directly. There is no `install.sh` and no edcloud-specific
config in this repo — every tool that applies to edcloud (shell, git,
gh, nvim, tmux, claude, codex, opencode, yazi, systemd, neomutt) is
already covered by its own `sync.toml`.

## Tracked references for this host

None. edcloud has no `/etc/`-shaped files in this repo. Anything
host-side (cloud-init, IAM, snapshot policy, restore drills, Tailscale
state) lives in `brfid/edcloud`:

- `RUNBOOK.md` — durable host baseline, rebuild workflow, backup and
  restore.
- `docs/ARCHITECTURE.md` — module boundaries.
- `cloud-init/user-data.yaml` — bootstrap baseline.

## Shell on edcloud

bash. `~/.bashrc` sources `~/.config/shell/profile`, which sources
`~/.secrets`. No host-unique block needed; the shared `profile` is
enough.
