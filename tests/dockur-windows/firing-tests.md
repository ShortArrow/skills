# Firing tests for dockur-windows

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/dockur`:
a compose file for a dockur/windows guest written the way a first draft arrives,
with the raw disk, the default stop grace and the ports published to every interface,
beside `NOTES.md`, which records that the guest is installed and reachable over SSH.
Run them with `tests/run-firing-tests.sh dockur-windows`.

Fixture: `tests/fixtures/dockur`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the answer takes the snapshot with the guest stopped,
takes the screenshot through the monitor socket rather than the web viewer,
and turns the compose file's disk to qcow2 before the first start.
No scenario needs Docker: the fixture has no daemon,
and what is judged is what the session proposes to run.

## Should fire

### S1 — a clean state to return to

> compose.yaml の Windows ゲストを、毎回同じ状態から始められるようにして。
> 今の状態をチェックポイントにしたい。

Expected: the skill fires,
or the answer stops the guest before snapshotting,
uses `qemu-img snapshot -c` on the qcow2 disk,
and notes that the compose file's raw disk has to become qcow2 before a snapshot is possible.

### S2 — what the guest is showing

> ゲストのインストールが進んでいるか見たい。
> 画面を PNG で取って。

Expected: the skill fires,
or the answer sends `screendump ... -f png` to the monitor socket with `docker exec` and copies the file out with `docker cp`,
instead of opening port 8006 in a browser.

### S3 — the compose file for a new host

> compose.yaml を Linux のサーバーで動かす前に直すところがあれば直して。

Expected: the skill fires, or the revision sets `DISK_FMT: qcow2`,
adds `MONITOR`, raises `stop_grace_period`,
and binds 8006 and 3389 to `127.0.0.1`.

## Should not fire

### S4 — a Hyper-V host

> NOTES.md にある Hyper-V の VM のチェックポイントを取って。

Expected: no skill call from this skill.
The guest named in that note is on Hyper-V,
which is `hyperv-clean-vm`'s.

### S5 — a value check

> compose.yaml で RAM_SIZE に指定されている値は何？

Expected: no skill call.
Nothing is being run or changed.

## Recorded runs

None yet.
The scenarios were written on 2026-09-24 with the skill and have not been run.
