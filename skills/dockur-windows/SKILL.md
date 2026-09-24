---
name: dockur-windows
description: |
  A Windows guest in a dockur/windows container, run the way hyperv-clean-vm and hyperv-screenshot run a Hyper-V guest: a qcow2 snapshot is the checkpoint, and a screendump through the QEMU monitor is the screenshot. Triggered by the moments that lose either: about to run a Windows guest on a Docker host that has no Hyper-V, about to create the container with the default raw disk, which has no snapshots, about to snapshot while QEMU holds the image, about to `docker stop` a Windows guest with the default ten-second grace, about to publish port 8006 or 3389 beyond localhost, about to read a guest through the web viewer when one monitor command returns a PNG, or about to rebuild a guest for a clean run instead of restoring one. Use when the host is Linux or a remote Docker context, when a run must repeat from identical state there, and when a headless guest must be seen. Hyper-V hosts stay with the hyperv skills.
allowed-tools: Bash, Read, Write
---

# A Windows guest in a container you can rewind

**dockur/windows runs Windows under QEMU with KVM inside a Docker container.** The host needs `/dev/kvm` and nothing else:
no Hyper-V, no VirtualBox,
and the Docker daemon may be on another machine entirely.
This skill is `hyperv-clean-vm` and `hyperv-screenshot` for that host.
The checkpoint is a qcow2 internal snapshot,
taken with `qemu-img` while the guest is stopped,
and the screenshot is a `screendump` sent to the QEMU monitor,
which comes back as a PNG without a session, an agent or a viewer.

The monitor and snapshot mechanics below were run on 2026-09-24 against `qemux/qemu`,
the image dockur/windows is built on,
with an Alpine guest on a remote Ubuntu 24.04 host.
The Windows-only steps,
the unattended install and the OEM script that turns on sshd,
are the ones a production runner uses and were not rerun here.

## The moments this replaces

| About to… | Instead |
|---|---|
| run a Windows guest on a Linux box or a remote Docker context | this container; Hyper-V is not there to reach for |
| create the container with the default disk format | `DISK_FMT: qcow2` before the first start; raw has no snapshots, and the format cannot change once Windows is installed on it |
| take a snapshot while the guest is running | stop the guest first; `qemu-img` is refused with `Failed to get "write" lock` while QEMU holds the image, and a copy taken by other means is a disk mid-write |
| `docker stop` a Windows guest with the default grace | `stop_grace_period: 2m` in the compose file, or shut Windows down from inside; the default ten seconds is a power cut for Windows |
| publish 8006 or 3389 as `8006:8006` | bind to `127.0.0.1:` and reach it through an SSH port forward; the web viewer has no authentication and the RDP password is in the compose environment |
| open the web viewer to see what the guest is doing | `screendump` through the monitor socket and `docker cp` the PNG out; it works during the install and at the logon screen |
| rebuild the guest for a clean run | `qemu-img snapshot -a clean`, then start; the restore takes seconds and the install took an hour |

## What the host needs

`/dev/kvm` on the machine the Docker daemon runs on. dockur's readme (read 2026-09-24) states that Docker Desktop on Linux,
macOS and Windows 10 does not hand KVM to containers,
and that Windows 11 works with nested virtualization enabled.
A Linux host with the `kvm` module, or a remote context to one,
is the case this skill is written for.

Check the device from the container the daemon will run,
not from the shell you are typing in:

```sh
docker run --rm --device /dev/kvm alpine ls -l /dev/kvm
```

From Git Bash on Windows this fails before reaching Docker,
with `error gathering device information while adding custom device "C"`:
the shell rewrote `/dev/kvm` into a Windows path.
`MSYS_NO_PATHCONV=1` in front of the command stops it,
and every `--device` and `-v /storage` path below needs the same.

## The compose file

```yaml
services:
  windows:
    image: dockurr/windows:<tag>          # pin the tag; the guest was installed under it
    container_name: win-fixture
    environment:
      VERSION: "11"
      USERNAME: "fixture"
      PASSWORD: "<from .env>"
      RAM_SIZE: "8G"
      CPU_CORES: "4"
      DISK_SIZE: "64G"
      DISK_FMT: "qcow2"                   # the checkpoint depends on this
      MONITOR: "/storage/monitor.sock"    # the screenshot depends on this
    devices:
      - /dev/kvm
      - /dev/net/tun
    cap_add:
      - NET_ADMIN
    volumes:
      - ./storage:/storage
      - ./oem:/oem:ro
    ports:
      - 127.0.0.1:8006:8006
      - 127.0.0.1:2222:22
    stop_grace_period: 2m
    restart: "no"
```

`MONITOR` and `DISK_FMT` are documented variables of the image (docs/environment.md, read 2026-09-24).
Without `MONITOR` the monitor still exists,
at `/run/shm/monitor.sock` inside the container,
but that path is the image's internal layout and moves without notice;
the documented one does not.
`restart: "no"` because a fixture that restarts itself after a restore has a state nobody chose.

## Order of operations

The order is the skill, as it is for Hyper-V:
each step after the install invalidates the snapshot before it,
and the snapshot is taken last.

1. **Put the sshd script in `oem/`.** dockur runs `/oem/install.bat` once,
   at the end of the unattended install.
   Have it call a PowerShell script that adds the OpenSSH capability,
   starts the service, opens port 22, and writes the public key.
   An administrator's key goes in `C:\ProgramData\ssh\administrators_authorized_keys` with inherited permissions stripped,
   as `hyperv-clean-vm` says; the same file and the same `icacls` line.
2. **Create and start.** `docker compose up -d`.
   The image downloads the ISO and installs unattended;
   with the readme's defaults that is tens of minutes,
   and nothing in the container's log says when Windows has reached the desktop.
   Watch with a screendump every few minutes (below),
   not with the web viewer.
3. **Confirm SSH from the host.** Through the forward:
   `ssh -p 2222 fixture@127.0.0.1 hostname`.
   The snapshot is not taken before this succeeds.
4. **Stop the guest from inside.** `ssh -p 2222 fixture@127.0.0.1 'shutdown /s /t 0'`;
   the container exits when QEMU does.
   `docker stop` also works once `stop_grace_period` is two minutes:
   the image sends ACPI power-off and waits.
5. **Snapshot.**

   ```sh
   docker run --rm -v "$PWD/storage:/storage" --entrypoint qemu-img dockurr/windows:<tag> \
     snapshot -c clean /storage/data.qcow2
   ```

   The disk is named after its format: `data.img` for raw,
   `data.qcow2` for qcow2.
   `qemu-img snapshot -l` lists what exists.
   Name the snapshot for what it contains, not for the date.
6. **Start.** `docker compose start windows` (or `up -d`).
   The monitor socket appeared 5 seconds after a warm start in the run above;
   Windows itself takes longer to reach the logon screen.

## Screenshot

The monitor is QEMU's human monitor on a Unix socket,
and `nc` is in the image,
so the command runs inside the container and the file is copied out:

```sh
C=win-fixture
docker exec "$C" sh -c 'printf "screendump /tmp/screen.png -f png\n" | nc -q 1 -w 2 -U /storage/monitor.sock >/dev/null'
docker cp "$C":/tmp/screen.png ./screen.png
```

`-f png` goes before the optional device and head;
`screendump /tmp/screen.png 0 0 png` is refused with `extraneous characters at the end of line`.
Without `-f` the result is a PPM,
which is the same picture at 3 MB instead of 20 KB and which few viewers open.
`nc -q 1` closes the connection after the command is written;
without it `nc` waits for input that never comes.

Check the file before believing it, as `any-screenshot` says:
count the distinct colours, and close to one is a failed capture.
The capture in the run above was 1280×800,
which is the image's default display size.

A guest whose display has slept returns a black frame,
as a Hyper-V guest does.
Wake it through the same monitor and capture again:

```sh
docker exec "$C" sh -c 'printf "sendkey shift\n" | nc -q 1 -w 2 -U /storage/monitor.sock >/dev/null'
```

Shift wakes the session and types nothing.
Enter and Space dismiss the dialog you came to read.

## Restore

```sh
docker compose stop windows                     # waits stop_grace_period for ACPI shutdown
docker run --rm -v "$PWD/storage:/storage" --entrypoint qemu-img dockurr/windows:<tag> \
  snapshot -a clean /storage/data.qcow2
docker compose start windows
```

`-a` rewrites the disk to the snapshot's contents;
the snapshot itself stays and can be applied again.
What was written since the snapshot is gone,
so evidence is copied out over `scp` or the `/shared` mount before the restore,
never left in the guest.

## Facts that bite

| | |
|---|---|
| **The write lock is the guard** | `qemu-img snapshot` on a running guest fails with `Failed to get "write" lock`. That failure is correct; do not work around it by copying the file, which produces a disk QEMU was in the middle of writing |
| **Raw is the default, and it is final** | `DISK_FMT` is read when the disk is created. A guest installed on raw stays raw, and its only checkpoint is a copy of a 64 GB file taken with the guest stopped |
| **The disk name follows the format** | `data.img` for raw, `data.qcow2` for qcow2. A command written for one name fails on the other with "No such file" |
| **8006 has no login** | The web viewer is the guest's console, unauthenticated. Bind it to `127.0.0.1` and reach it through `ssh -L 8006:127.0.0.1:8006 <host>` |
| **The console is not the RDP session** | What the screendump shows is the console; a dialog on an RDP desktop is not in it, and the other way round. The same split `hyperv-screenshot` describes |
| **The OEM script runs once** | `install.bat` executes at the end of the install and never again. A change to it needs a reinstall, or the same change made over SSH |
| **`docker stop` with the default grace cuts the power** | Ten seconds is not a Windows shutdown. `stop_grace_period: 2m` gives the image's ACPI shutdown time to complete; the run above stopped a Linux guest in 9 seconds and Windows needs more |
| **The monitor answers on its own schedule** | `nc -w 2` bounds the wait. A screendump of a large display takes a moment to write; `ls -l` the file before copying it out |
| **The path convention is the shell's** | From Git Bash on Windows, `--device /dev/kvm` reaches Docker as a `C:` path. `MSYS_NO_PATHCONV=1` for every Docker command that carries a Unix path |

## Where this sits

`any-screenshot` sends a guest in a dockur/windows container here;
the Hyper-V pair, `hyperv-clean-vm` and `hyperv-screenshot`,
owns a guest on a Hyper-V host,
and `windows-sandbox` owns the one disposable desktop on a Windows host with no VM built.
Inside the guest, once SSH answers,
`windows-screenshot` and `flaui-screenshot` apply as on any Windows machine;
the screendump wins when there is no session at all.

## Sources

- dockur/windows readme, github.com/dockur/windows, read 2026-09-24:
  the compose example, the host support table (KVM under Docker Desktop),
  the `/oem/install.bat` mechanism and the `/storage` files.
- dockur/windows `docs/environment.md`, read 2026-09-24: `MONITOR`,
  `DISK_FMT`, `DISK_FLAGS`, `DISPLAY`, `VNC_PORT` and their defaults.
- qemus/qemu `docs/environment.md` and `src/{display,disk,power}.sh` at master,
  read 2026-09-24: the internal monitor path,
  `nc -q 1 -w 1 -U` as the image's own way of talking to it,
  and the disk name following the format.
- QEMU 11.1.0 `help screendump`,
  read from the running container on 2026-09-24:
  `screendump filename [-f format] [device [head]]`,
  formats `png` and `ppm`.
- The timings above (25 s cold and 5 s warm to the monitor socket, 9 s to stop, 1280×800 capture) are one run of `qemux/qemu` with `BOOT=alpine`,
  `RAM_SIZE=1G`, `DISK_FMT=qcow2` on a remote Ubuntu 24.04 host with 12 cores,
  on 2026-09-24.
  They bound the mechanism, not a Windows guest.
