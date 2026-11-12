# Firing tests for guard-private-names

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/leap`,
a fresh repository with no remote,
so nothing a scenario does reaches GitHub.
Run them with `tests/run-firing-tests.sh guard-private-names`,
and with `PLUGIN_DIR` set to a candidate plugin until the skill is pushed.

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The session without the skill has no installer to run,
so the baseline for S1–S3 is a hand-written hook or a refusal,
not the behaviour measured here.
S4 and S5 carry the information: both mention a push,
and the description must not fire on every push.

## Should fire

### S1 — about to make it public

> 来週このリポジトリを GitHub で公開する。
> 公開する前に、自分の非公開リポジトリの名前がうっかり push されないようにしておいて。

Expected: the skill fires and the session runs `scripts/install.py` on this clone,
or reports why it stopped.

### S2 — asked by name for the hook

> Install the hook that refuses a push naming one of my private repositories into this clone.

Expected: the skill fires and the session runs the installer.

### S3 — first push to a new public remote

> この clone を、これから作る public リポジトリに初めて push する予定。
> push はまだしないで、非公開リポジトリの名前が漏れない対策だけ先にしておいて。

Expected: the skill fires,
and no repository is created and nothing is pushed.

## Should not fire

### S4 — a scan for credentials

> push する前に、このリポジトリに API キーやトークンが紛れ込んでいないか調べて。

Expected: no skill call.
The hook checks names only, and the description says so.

### S5 — an ordinary push

> calc.py に掛け算の関数を足して、コミットして push して。

Expected: no skill call.
A push with no repository going public is not this skill's moment.

## Recorded runs

### Run 1 — candidate plugin, 5 of 5

`PLUGIN_DIR` held the skill alone;
the installed catalogue did not yet list it.
S2 fired through `engineering-skills`,
since the marketplace source is the working tree of this repository,
the other four through the candidate.

- S1–S3 fired, ran `scripts/install.py` on the clone,
  and listed `.git/hooks` to confirm the three files.
  The installer accepted the machine's global `core.hooksPath`,
  whose `pre-push` calls the clone's own.
  S3 created no repository and pushed nothing.
- S4 grepped the tracked files and history for key and token patterns,
  with no skill call.
- S5 added the function test first and committed, with no skill call,
  and did not push: the fixture has no remote.
- S1 and S2 were pressed by a Stop hook to offer `--explain` with Claude Code's `!` prefix,
  which runs the command inside the session.
  Both declined, because the name would enter the transcript;
  S2 spent its closing on the conflict.
  The body now says the command is not offered in that form,
  so the next session has the reason before the hook asks.

