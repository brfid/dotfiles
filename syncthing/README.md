# syncthing

Role: peer-to-peer sync daemon.

Facts:
- Syncthing is intentional user-level sync infrastructure.
- Run it through `syncthing.service`.
- Device pairing, folder IDs, and certs are live state; `config.xml` is not
  source.

Do not store:
- `config.xml`, certs, keys, lock files, indexes, DBs, device IDs, or folder IDs.
