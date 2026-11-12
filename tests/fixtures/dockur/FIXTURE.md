Fixture for the dockur-windows firing tests.
`compose.yaml` is a dockur/windows service as a first draft arrives:
the default raw disk, no `MONITOR`, the default stop grace,
and 8006 and 3389 published on every interface.
`NOTES.md` says the guest is installed and answers SSH on the forwarded port,
and mentions a separate Hyper-V VM on another machine for the scenario that must not fire.
`oem/install.bat` is the one-line post-install hook.
Nothing here runs: the scenarios read the files and judge what the session proposes.
