# nchat

Role: terminal client for Telegram and Signal.

Build nchat with Signal support enabled:

```sh
NCHAT_CMAKEARGS="-DHAS_SIGNAL=ON" ./make.sh build
sudo ./make.sh install
```

Use one config directory per protocol:

- Telegram: `~/.config/nchat`
- Signal: `~/.config/nchat-signal`

The shell capsule defines `telegram` and `signal` aliases for these paths.
Set up or re-pair an account with `telegram -s` or `signal -s`.

Do not track either config directory. They contain account databases, pairing
state, message caches, logs, and other generated runtime data.
