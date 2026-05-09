# Core rebuild resources

This folder lists repos needed to rebuild the local working environment after a
fresh machine install or repave.

It is not a full repo inventory.

`repos.toml` records public-safe metadata:

- repo name
- GitHub clone URL
- expected local path
- short purpose

GitHub repo visibility is the source of truth for public/private handling.
This folder does not duplicate that state.

If visibility matters, check GitHub:

```bash
gh repo view brfid/<repo> --json visibility
```

If visibility cannot be checked, treat the repo as private.
