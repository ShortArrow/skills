---
name: consultation-path
description: Settle what a consulted model returns, instead of merging it. Use when another model's reading is about to be adopted because it reads well, when two readings disagree, or when the user holds a view of their own. Not for a fact one command checks, and not where the user delegated the call — that is own-the-call.
allowed-tools: Bash, PowerShell, Read, Grep, Glob, Agent
---

# Consultation path

A second model is cheap to ask and expensive to adopt.
What comes back is fluent, confident and shaped like a conclusion,
which is exactly what an unverified claim looks like from the inside.

This skill is the path from "I asked another model" to "here is what we know",
and it has one job: to stop the consultation becoming a dump — a pile of readings nobody reconciled,
from which the turn quietly picks the one it already liked.

## The moments this replaces

| About to… | Instead |
|---|---|
| adopt a consulted model's output because it reads well | attack it as `adversarial-verify` says; fluency is not provenance |
| judge between two disagreeing readings | hand both to a third reading told to break each; the winner is what survives, not what was chosen |
| report "both models agree" as confirmation | report it as one observation made twice; shared training data is a shared blind spot |
| lay out options with your own pick first | give the options unordered and withhold your lean until the user has said theirs |
| merge a consulted reading into your own prose | keep them separate and attributed, so the user can see which is which |

## The disagreement rule: the third reading attacks, it does not judge

When two readings conflict,
the obvious move is to ask a third which is right.
Do not.

A judge cannot break a tie it shares.
Three models trained on overlapping corpora hold overlapping errors,
so where the error is in the corpus the judge lands on the same side as the reading that shares it,
and the wrong answer arrives with a 2-to-1 majority attached.
That is worse than no third reading,
because the majority is read as strength: the error is now *confirmed*,
and the next decision stands on it without looking.

So the third reading is given both claims and told to break each one.
Its output is not "A is right" but "A survives, B falls" — or,
where the blind spot is shared, "both fall",
and the question is **unresolved**.

**Unresolved is a result,
and it is reported as one.** It is the only outcome that a shared bias cannot fake.
A path that cannot return it has no defence against the case it exists for.

This is `adversarial-verify`'s machinery, not a new one:
refuted by default when uncertain,
the verdict moved to a context holding only the artifact and the criteria,
and never the author's conclusion passed along with the claim.
A consultation is a subagent report with a different vendor's name on it,
so the gate on subagent reports covers it:
what comes back is verified before it is relayed.

### The three shapes this was chosen over

Each was considered and dropped,
so the next reader does not derive them again.

**Let the third model judge which reading is right.** This is the shape the rule exists to forbid,
and it fails on the case it is needed for:
the judge cannot detect that it shares the error it is judging.
It is listed here because it is the move that suggests itself first.

**Ask no third model; present the disagreement as it stands.** Cheapest,
and it takes no side.
But neither reading has then been tested,
so a factual error and a difference in premises leave the same trace,
and the next decision cannot tell which it is standing on.

**Show the third model no readings;
have it check only the disputed fact.** This keeps it clear of the first two readings,
which is the right instinct,
and where the dispute is factual it settles the matter.
It fails where the dispute is not factual — over an interpretation,
a design judgement,
or a step that was skipped — and it depends on the disputed point being excerpted correctly,
which is itself one of the readings under dispute.

Attacking both claims is preferred because it is the only one of the four whose output can be *neither survived*.

## Order matters where the user holds a view

The user asking for a second reading usually has a first one.
Their view is the thing most easily lost,
because it arrives in their own words while the model's arrives in the register of a finding.

So, in this order:

1. **The user's position, restated.** If they gave one,
   it is stated before any model's, in their terms,
   so that what follows is compared against it rather than replacing it.
2. **The consulted reading, attributed.** Named by who produced it,
   kept out of the agent's own prose.
3. **What survived the attack.** From the rule above.
4. **The agent's own read, last.** Withheld until the three above are on the table.

Putting the agent's pick first is the failure this ordering exists to prevent.
It anchors: the user reads the rest as agreement or dissent from a position already on the table,
and the second reading they asked for is spent confirming the first one they were shown.
`own-the-call` requires a pick with its evidence,
and that holds — the pick is still made and still carries its reasons.
What changes is only *when* it is shown,
and only where the user has said they want to weigh their own view against the options.
Where they have not, `own-the-call` governs unchanged and the pick leads.

## What is actually available to consult

Checked on this machine on 2026-11-10 and 2026-11-11 by running each binary,
not only its help, because a consultation command that does not exist produces a reading nobody ran — and because a flag that is documented can still have been removed.

| CLI | One-shot form | Keeping it read-only |
|---|---|---|
| `codex` | `codex exec --sandbox read-only --cd <dir> "<request>" < /dev/null` | the OS sandbox denies the write |
| `copilot` | `copilot -p "<request>" -s -C <dir>` | plain `-p` already denies it: there is no one to approve |
| `gemini` | unusable here today — see below | — |
| `antigravity` | `antigravity chat "<prompt>"` exists but opens a window | — |

Two further routes into the same models, both confirmed by running them:
`codex review` is a second non-interactive subcommand (`exec` also answers to the alias `e`),
and **`copilot` needs no flag at all** — piping a prompt into a bare `copilot` returns an answer.
The second matters beyond this table:
it is why the gate below cannot key on flags.

So the roster is **two**,
and a panel of three distinct models is not available from this machine today.
Where only two readings exist,
the third attacker is a fresh local subagent under `adversarial-verify`,
which is a different context but not a different corpus — state that limit when reporting,
because it is the exact case where a shared error survives.

`codex` carries its own skill;
`skills/codex/SKILL.md` holds the flag meanings,
the host-detection table,
and the two refusals that look like a failed reading — the Git-repository check and the piped stdin that gets appended to the prompt.

### The two levers differ, and so does what a clean run proves

**Codex's sandbox is enforced by the operating system.** Asked to overwrite a named file by shell command,
every route failed with the OS refusing:
PowerShell `Set-Content` and `cmd /c echo` both got "Access to the path … is denied",
`python` could not start, `git commit` could not create `index.lock`,
a write to `%TEMP%` outside the working directory was denied and the file never appeared,
and `New-Item -ItemType Directory` was denied.
No write landed.

Two cautions came out of testing it rather than trusting it:

- **The exit code is not the signal;
  the file is.** A PowerShell `Set-Content` whose write was denied,
  followed by another statement,
  reported **exit 0** while the file stayed unchanged.
  Check the file.
- **A model saying "denied" proves nothing.** In one run reported by an adversarial verifier,
  the model declined to attempt any route and still reported "write denied" for each.
  That single observation was not reproduced here,
  and it is recorded as the verifier's rather than this session's.
  It needs no more weight than that:
  the reasoning stands on the exit-code case above, which was reproduced,
  and both say to read the file.
  Only the executed commands in the log, plus the file being unchanged,
  are evidence.
  This is `adversarial-verify`'s rule arriving in miniature:
  a report is a claim, not an observation.

**Copilot denies the write without any flag.** `--allow-all-tools` is *not* required for non-interactive mode;
its own help says non-interactive mode "denies tool requests that no allow rule … approves",
because there is nobody to ask.
Run with a bare `-p`, a request to overwrite a file returned `✗ Edit … Denied, no one to approve write` and `✗ Shell … Denied, no one to approve shell command`,
and neither the target nor a new file changed.
So the simplest form is already read-only,
and the denial comes from the approval layer rather than the kernel.

`--available-tools view glob grep` remains useful as an explicit narrowing — it prints `Disabled tools: create, edit, powershell, …` and no tool name got a write through — but it is belt alongside braces,
not the only lever.
Copilot does have a `--sandbox`, OS-level and MXC-backed;
it is not a read-only switch (by default it permits writes to the working directory, and its help says built-in file edits are not OS-sandboxed),
so it does not replace the above.

**`gemini` is not a consultee here today,
and the reason is not the shim.** The `gemini` on `PATH` is a mise shim with no version set,
which exits non-zero; but the package is installed,
and bypassing the shim reaches the real blocker:
`IneligibleTierError: This client is no longer supported for Gemini Code Assist for individuals` (reason code `UNSUPPORTED_CLIENT`, tier `free-tier`).
An account tier, not a missing binary — so this row may change without anything being reinstalled.

The exit code is not a reliable marker of that error,
which is worth stating because an earlier draft here read it as one.
The run exits 55 only when an untrusted-directory check also fires;
with the directory trusted, or with `--skip-trust`,
the same tier error exits 1,
and the bare shim exits 1 for the unrelated reason that no version is set.
So three different exit codes attach to one blocker.

**`antigravity` has a `chat` subcommand**,
which takes a prompt and `--mode ask|edit|agent`.
Its remaining options are window options (`--new-window`, `--reuse-window`, `--maximize`),
and its help describes no way to return the answer on stdout,
so it is not usable unattended; it was not run,
because it would open a window on the user's desktop.
"No one-shot prompt mode" would be wrong;
"no headless mode" is what the help supports.

A consultation that could write is not a consultation;
it is a second agent editing the repository.
Confirm the read-only lever is in the command before running it,
and confirm the file afterwards.

## The cost, and when not to pay it

Three readings cost roughly three times one,
and the attack costs a fourth.
Spending that on a question one command answers protects nothing — `adversarial-verify`'s "when not to bother" applies here unchanged,
and a version, a flag or a line count is checked, not consulted on.

Two more cases do not belong here:

- **The user delegated the call.** "Decide and tell me why" is `own-the-call`;
  convening a panel spends three model calls on a decision already handed to the agent.
- **There is one right answer and no competing reading.** A complexity,
  a return type, a documented default.
  Consultation adds a second voice, not a second fact.

The gate: would a wrong answer here survive a week unnoticed,
and cost something when found?
Below that, read it yourself and say so.

## The rule, mechanised

The rule above is prose,
and prose that asks for a step decays while a gate does not.
So the step this skill most depends on — that a consulted reading is attacked before it is relayed — is enforced rather than requested.

`adversarial-verify` already refuses `git push`, `gh pr create`,
`gh pr ready` and `gh issue create` while any subagent report in the session has no verification after it,
and sends back a turn that would end on one.
A consultation now counts as such a report.

That gap was real and not hypothetical.
The host has no tool for "ask a different vendor's model",
so a consulted reading arrives as a shell call,
and the gate read only `Agent`, `Task` and `Workflow`.
The one kind of claim nobody in the session observed was therefore the one kind that could leave it unopposed.

### Three narrower rules, each broken

What separates a consultation from any other shell call is only the command.
Three attempts were made to read that command precisely,
each passed its own tests, each scored well on real data,
and each was then broken by an adversarial verifier.
The record is the finding; the final rule is almost an afterthought.

| Attempt | Rule | Broken by |
|---|---|---|
| 1 | the invocation: `codex exec` at the start of a segment | **21 misses** — a quoted `$(…)`, a quoted absolute path, `xargs`, `nice`, `timeout 5m`, `bash -c`, global options before the subcommand, the alias `codex e`, `codex review`, a stdin prompt, `copilot -sp` |
| 2 | the binary's name, minus a list of what runs no model | **56 false positives** — every package manager, process tool, file tool and search tool that can take the word as an argument; and **two rules that read the prompt**, so the prompt could switch them off |
| 3 | an allowlist of documented answer-returning subcommands | **~40 misses** — a bare `copilot` reading its prompt from a pipe, `timeout -v codex exec` (the wrapper's own flag read as a version request), `codex review help` (where `help` is the prompt), quoted subcommands, PowerShell argument arrays |

Attempt 2's failure is the instructive one twice over.
Its exclusion list had no end:
the next tool that can take `codex` as an argument is always missing,
and the list grows with every round.
And two of its exclusions read the prompt — `which` followed by any word matched `codex exec "Decide which reading is right"`,
and a `#` inside a quoted commit message swallowed the `&&` and the real call behind it. **A rule that reads the prompt can be switched off by the prompt.**

Attempt 3's failure settled the question.
A verifier ran the binary and got an answer from `echo "…" | copilot` — no flag at all — which means no rule keyed on flags or subcommands can be right.

### The rule that holds, and the cost it accepts

The consultee's name appearing as a word in the command.
That is all.

Shell text cannot be classified reliably:
a command reaches a binary through a variable, a quoted path, a pipe,
an interpreter, a line continuation,
a PowerShell argument array or an alias,
and no pattern over the text sees every route.
So the only real question is which way to be wrong,
and the two costs are not close.
A false flag costs one `Verify:` subagent that finds nothing.
A miss lets a claim nobody in the session observed leave it unopposed,
which is the single thing the gate exists to prevent.

**So the name alone triggers,
and the looseness is the design rather than a defect in it.** Three exclusions remain,
all structural rather than enumerated — each is text no shell would run:

- a heredoc body, keeping the opener's own line,
  because `cat <<EOF | codex exec -` consults on it;
- the text after an unquoted `#`,
  where tracking quotes is what separates it from `git commit -m "fix #12" && codex exec`;
- a path segment following the name,
  since this repository documents these tools and `skills/codex/SKILL.md` appears far more often than a call.

### What it scores

Against one session's transcript, 1004 shell calls,
each candidate judged by **its output** and not its command:
**5 of 5 readings a model actually answered were caught,
0 missed.** 21 further calls are flagged that asked no model — the accepted cost,
one verification each.

Two earlier counts in this document were wrong, both in the same way.
"5 of 5" and then "7 of 7" were computed by labelling commands that *looked* like consultations;
two of the seven had died on a removed flag and a trusted-directory refusal without reaching a model,
and `| tail` had hidden the non-zero exit. **A command that looks like a consultation is not evidence that a model answered.** The output is.

57 consultation shapes and 20 non-consultations are fixtures in `tests/test_verify_reports.py`,
every one produced by a verifier or an attack rather than invented,
and each component of the check fails a test when it is removed.

### A fourth round, from a different direction

An automated security review of the pushed commit found two more,
both in the only step that can hide a call — the one that drops lines.

A `<<` inside quotes or after a `#` is text, not a heredoc opener,
and treating it as one discarded every line that followed:
`echo "a <<EOF b"` or `# <<EOF` on one line,
the consultation on the next, and the gate saw nothing.
Worse, a heredoc whose terminator never arrived swallowed the rest of the command outright,
so `cat <<EOF > f` with no closing `EOF` was a one-line way past the gate.
Separately, a backslash was not handled in the quote walk,
so one escaped quote desynchronised it and the rest of the command read as quoted.

Both are fixed by failing toward flagging, the same principle as above:
openers are looked for only in what a quote-aware pass leaves outside quotes and comments,
an unterminated heredoc gives its held lines back instead of discarding them,
and a backslash escapes the next character outside single quotes.

One of the review's examples was wrong,
and checking rather than accepting it is the point.
It offered `echo "he said \"hi\"" # ; codex exec q` as a bypass;
running it in `bash` shows the `#` really does start a comment there,
so nothing after it executes and ignoring it is correct. **A security finding is a claim too.** Seven of the eight cases reproduced and are now fixtures;
the eighth was refuted at the shell.

A fifth round raised three more,
and only one of the three applied — which is itself the point about a finding being a claim.

The one that applied is that **the hook was reading PowerShell with Bash's grammar.** A backslash is literal in PowerShell,
a backtick escapes, and `''` inside a single-quoted string is one escaped quote;
which set of rules holds decides whether a given `#` opens a comment.
Rather than carry two grammars,
the one place the difference can hide a call is given up:
where an escape character and a `#` meet in the same command,
the comment is not cut and the text behind it is kept.

The other two were checked and did not reproduce.
One claimed the delimiter-unquoting step could invent an opener inside a string;
it cannot, because the quote-aware blanking runs after it,
so a `<<` inside quotes is blanked either way.
The other claimed `$'…'` quoting was unhandled; it is already handled,
because the `'` opens quote mode on its own.
Both were tested with several commands each before being set aside.

A sixth round raised two, split the same way: one real,
one refuted by running it.

The real one is PowerShell's **block comment**.
`<# … #>` ends, and the code after `#>` runs — `Write-Output x <# a #> ; codex exec q` reaches the consultation,
confirmed in `pwsh`.
The `#` inside the delimiters was being read as opening a line comment,
which took the rest of the command with it.
Either delimiter now abandons the cut.

The refuted one was **curly quotes**:
the claim was that `“…”` quotes a `#` so the comment should not be cut.
Running it shows otherwise — `bash` printed the quote character literally and did not execute what followed the `#`,
so the `#` really is a comment and cutting it is correct.
A curly quote is an ordinary character to every shell here,
which is why it cannot shelter anything.

Three of the round's findings also had to be checked against the shells themselves rather than reasoned about.
Two of the PowerShell examples turn out to be cases where the gate's verdict was already right:
in `Write-Output 'it''s' # ; …` the `''` really does close the string,
so the `#` really is a comment and nothing after it runs.
Running the command was the only way to know that.

This round is also the clearest evidence for the section above.
Six independent attempts to read shell text — three adversarial rounds and three automated reviews — each found a way through,
and every one of them went through the quoting,
commenting or line-dropping logic rather than through the match itself.
That is why the match is the consultee's name and nothing more.

### One change here was reverted

The gate's own `git push` detection matches its text anywhere in the command,
so writing *about* a push is refused as though it were one — a verifier hit this on a command whose only `gh pr create` sat inside a heredoc string.
Narrowing it to what a segment runs fixed those cases and broke seven real publishes:
`eval "git push"`, `bash -c`, `sh -c`, `pwsh -c`, `cmd /c`,
`Invoke-Expression` and `iex`,
because the command to run sits inside the quoted argument the narrowing blanked.
The narrowing was reverted and the false refusal kept,
for the same reason as above: it costs one rewritten command,
while a missed publish costs the guarantee.

## Where this sits

`adversarial-verify` supplies the attack,
the refute-by-default verdict and the gate that stops an unverified report leaving the session;
this skill says who to ask and in what order to report.
`own-the-call` governs the pick and its four parts,
and is suspended only in its ordering,
only where the user asked to weigh their own view.
`codex` holds one consultee's command surface.
`measured-claims` applies to any number this path reports back.

## Sources

Every row below was observed on this machine.
Where a first reading was wrong, the correction is kept beside it,
because what the error was is part of what the row establishes.

- `codex --version`, `codex --help` and `codex exec --help` of codex-cli 0.164.0,
  read 2026-11-10 and 2026-11-11:
  `--full-auto` no longer exists and `codex exec --full-auto` exits **2** with "unexpected argument";
  `-s`/`--sandbox` takes `read-only`,
  `workspace-write` or `danger-full-access`;
  `--skip-git-repo-check` is required outside a repository;
  a piped stdin is appended to the prompt as a `<stdin>` block;
  `e` is a documented alias for `exec`,
  and `review` is a second non-interactive subcommand.
  An earlier draft of this skill said exit code 1;
  the observed code is 2.
- Write attempts against a named file in the session scratchpad,
  2026-11-10 and 2026-11-11.
  Under `codex exec --sandbox read-only` in a throwaway Git repository:
  PowerShell `Set-Content`, `cmd /c echo`, `python`, `git commit`,
  a write to `%TEMP%` outside the working directory,
  and `New-Item -ItemType Directory` all executed and all were refused by the OS ("Access to the path … is denied"),
  and no write landed.
  One of those execs reported **exit 0** while its write was denied,
  so the file and not the exit code is the signal.
  In a separate run the model declined to attempt any route and still reported "denied" for each,
  so a model's "denied" is not evidence.
  Under `copilot` with no allow flags at all,
  an overwrite request returned `✗ Edit … Denied, no one to approve write` and `✗ Shell … Denied, no one to approve shell command`,
  and nothing changed.
  Under `--allow-all-tools --available-tools view glob grep`,
  copilot printed `Disabled tools: create, edit, powershell, …` and no tool name got a write through.
- `copilot --help` and `copilot help sandbox` of GitHub Copilot CLI 1.0.108,
  read 2026-11-10 and 2026-11-11:
  `-p`/`--prompt` with `-s`/`--silent` as the non-interactive form;
  a prompt may instead arrive on stdin,
  and `copilot -sp` combines the short flags,
  both confirmed by running them; `--allow-tool`, `--deny-tool`,
  `--available-tools` and `--excluded-tools`;
  a `--sandbox` that is OS-level and MXC-backed but permits writes to the working directory by default and does not OS-sandbox built-in file edits.
  An earlier draft of this skill claimed non-interactive mode *requires* `--allow-all-tools`;
  the help says the opposite — non-interactive mode denies what no rule approves,
  because there is nobody to ask — and a bare `-p` run confirmed it.
- The `gemini` shim and the installed package, 2026-11-11:
  `gemini --help` fails with `mise ERROR No version is set for shim`,
  but `mise ls` shows `npm:@google/gemini-cli 0.52.0` present,
  and running it directly returns `IneligibleTierError: This client is no longer supported for Gemini Code Assist for individuals` (`UNSUPPORTED_CLIENT`, `free-tier`).
  So the blocker is the account tier, not a missing install.
  Two earlier drafts were wrong here in turn:
  the first named only the shim,
  and the second read exit 55 as the tier error's own code.
  It is not — 55 comes from an untrusted-directory check that fires alongside it,
  and with the directory trusted the same error exits 1.
- `antigravity --help` of Antigravity 1.104.0, 2026-11-11:
  a `chat [prompt]` subcommand exists,
  with `--mode ask|edit|agent` and otherwise window options,
  and no documented way to return the answer on stdout.
  It was not run, because it opens a window.
  An earlier draft said it had no one-shot prompt mode,
  which is false as worded.
- Three rounds of adversarial verification, 2026-11-11,
  each given the claims and how to break them and not the conclusion.
  The first refuted two of five claims and corrected a third,
  and broke the invocation-matching consultation check with 21 missed shapes.
  The second broke its replacement with 56 false positives and 11 further misses,
  two of which could be triggered from inside a prompt,
  corrected the real-data count from 7 of 7 to 5 of 5 by labelling each run's *output* rather than its command,
  and found that the gate's own publish detection matched a `gh pr create` written inside a heredoc.
  Every finding was reproduced here before being adopted;
  all 149 command shapes are fixtures in `tests/test_verify_reports.py`.
  One observation from the first round — a model reporting "denied" without attempting anything — was not reproducible on demand and is attributed to that verifier rather than claimed here.
  The third round broke the allowlist in turn, with about forty misses:
  it ran `echo "…" | copilot` with no flag and got an answer,
  which is why the rule that survives keys on nothing but the name.
  It also found that a narrowing of the gate's own publish check,
  made in the second round, had broken seven real publishes;
  that change was reverted.
  Its finding that `PRINTS_SOURCE` was pinned by no test was correct at the time and is now moot,
  since the simplification removed that pattern along with five others.
- An automated security review of the pushed commit, 2026-11-11,
  which found two parser differentials in the line-dropping step:
  a `<<` inside quotes or after a `#` read as a heredoc opener,
  an unterminated heredoc discarding the rest of the command,
  and an unhandled backslash desynchronising the quote walk.
  Seven of its eight example commands reproduced here and are now fixtures;
  the eighth was refuted by running it in `bash`,
  where the `#` it relied on really does open a comment.
- A second automated security review, 2026-11-11,
  which found that Bash escape rules were being applied to PowerShell commands:
  a backslash is literal there, a backtick escapes,
  and `''` inside a single-quoted string is one escaped quote.
  Its other two findings — an invented heredoc opener inside a string,
  and unhandled `$'…'` quoting — were each tested with several commands and did not reproduce,
  because the quote-aware blanking runs after the unquoting step and because `'` already opens quote mode.
  Two of its PowerShell examples were cases where the verdict was already correct,
  which only running them in `pwsh` established.
- A third automated security review, 2026-11-11:
  PowerShell's block comment `<# … #>` ends,
  and `Write-Output x <# a #> ; codex exec q` reaches the consultation,
  confirmed in `pwsh`.
  Its other finding, that curly quotes shelter a `#`,
  was refuted by running it:
  `bash` prints the character literally and does not execute what follows the `#`,
  so cutting there is correct.
