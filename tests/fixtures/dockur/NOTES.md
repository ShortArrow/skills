# Fixture guest

The Windows 11 guest in `compose.yaml` finished its unattended install on 2026-09-22.
`oem/install.bat` turned sshd on, and the host reaches it with:

```sh
ssh -p 2222 fixture@127.0.0.1 hostname
```

The build tools are installed and the UI suite runs against it.
Every run so far has started from whatever state the previous run left.

The older fixture, a Hyper-V VM named `WinFixture` on the desktop machine,
still exists with its `clean-sshd` checkpoint and is used when the server is busy.
