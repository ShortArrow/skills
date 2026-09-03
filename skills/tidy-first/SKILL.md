---
name: tidy-first
description: |
  Keeping structural change and behavioural change in separate commits, triggered by the moments that mix them: about to rename, move or extract in the same commit as a logic change, about to clean up adjacent code "while here" inside a bug fix, about to force a feature into code whose shape resists it instead of reshaping first, or about to commit a diff in which both the tests and the structure moved. The test is mechanical — a structural change keeps every test green without editing any of them — and a diff that cannot say which lines changed behaviour cannot be reviewed, reverted or bisected either. Use when editing working code and whenever the cleanup urge arrives mid-task.
allowed-tools: Bash, PowerShell, Read, Edit, Write
---

# Structure and behaviour travel separately

Two kinds of change, and one referee:

- **Structural** — rename, move, extract, inline, reorder. Every test
  stays green and **none of them is edited**. If a test had to change,
  the change was behavioural, or the test was coupled to structure and
  fixing that is its own structural change.
- **Behavioural** — the output differs for some input. Under the TDD
  cycle this is the change a failing test demanded.

One commit holds one kind. The order is a choice — tidy first so the
change drops in, or tidy after while everything is green — mixing is not.

## The moments this replaces

| About to… | Instead |
|---|---|
| rename or extract in the commit that also fixes the logic | two commits: the rename with tests untouched, then the fix with its failing test |
| clean up the code next to the bug "while here" | the fix in this diff; the cleanup in its own commit, or a note if it can wait |
| bend a feature into code whose shape fights it | reshape first — a structural commit that makes the feature a small diff — then the feature |
| commit a diff where tests and structure both moved | split it until each side answers one question |

The "while here" row is the common one. The urge is right — the code is
bad — and acting on it in place converts a reviewable diff into an
unreviewable one. The urge gets a commit of its own, not a seat in this
one.

## Why a mixed diff costs more than it looks

- **Review.** A reviewer of a mixed diff reads every renamed line looking
  for the behaviour change hidden among them, or stops looking. Both
  outcomes are worse than two small reviews.
- **Revert.** The behaviour change turns out wrong; the rename was fine.
  A mixed commit takes both back.
- **Bisect.** The commit a bisect lands on answers "structure or
  behaviour?" with "yes".

A structural commit is cheap to review at any size — its claim is "no
test changed, all green" and CI can vouch for it. All the reviewer's
attention lands on the behavioural diffs, which are now small.

## Tidy toward the next change

Structure is tidied **in the direction the coming change needs**, not
toward taste. A tidying that no upcoming change asks for is speculation
with the same cost profile as any other speculation: it churns history,
risks regressions, and buys nothing until a need arrives — and the need,
when it arrives, usually wants a different shape.

The measure of a good structural commit is the behavioural diff after
it: if reshaping did its job, the feature or the fix became a few lines
in the place a reader would look for them.

## When the diff has already grown mixed

It happens mid-flow. Split before committing, not after:

- `git add -p` when the kinds sit in different hunks
- stash, replay the structural part from the editor, commit, pop, commit
  the rest — when they interleave in the same lines
- worst case, reset and redo in order; with the shape now known, the
  second pass is minutes

"I will describe both in the message" is not one of the options. The
message cannot make a diff answer one question.

## Moving the cut itself

Regrouping folders — layers into features, or back — is the largest
structural change a codebase takes, and it is still structural: every
test passes untouched, or the move carried behaviour with it. Do it in
its own commit, one slice at a time, and leave the behaviour change
for the commit after. Which axis to move toward is `slice-first`.

## Without tests there is no referee

Structural-vs-behavioural is only checkable against tests that stay
green. Code with no tests gets a characterisation test before the
tidying starts — the tdd-cycle skill owns that entry point. Tidying
untested code on visual inspection is a behavioural change waiting to be
noticed.
