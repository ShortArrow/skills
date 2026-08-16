---
name: agent-harness
description: |
  Making an AI coding agent hold a project's conventions by construction, in any language: prose conventions decay as the session grows, while gates — types, lints, permissions — bind at turn 1 and turn 200 alike. Feedforward narrows what can be written (strictest toolchain mode, permission boundary, layered docs); computational sensors in one fast command catch the rest; an inferential review is triaged into fix-code, fix-spec, mechanize, or reject; error messages state the fix; deliberate violations test the harness itself. The free layer goes everywhere, each paid sensor is added after an observed violation, and nothing is frozen mid-exploration. Use when setting up a repository for AI coding sessions, when the same correction repeats across sessions, when conventions in CLAUDE.md are being ignored, and when reviewing generated code stops scaling.
---

# The Agent Harness

A convention written in prose is followed the way instructions are
followed: well at the start, worse as the context grows. A convention
compiled into a gate — a type error, a lint rule, a denied command —
binds at turn 1 and at turn 200 with the same force. The harness is
the discipline of moving conventions from the first form into the
second, one at a time, until the human reviews decisions instead of
output.

Two mechanisms, in order of leverage.

## Feedforward: narrow what can be written

Prevention needs no detection. Three surfaces, each with an
equivalent in every stack:

- **The toolchain's strictest mode.** Whatever the compiler, turn
  everything on: `strict` in tsconfig, `#![deny(warnings)]`,
  `mypy --strict`, `<Nullable>enable</Nullable>` with warnings as
  errors, `-Wall -Werror`. A class of violation the toolchain
  rejects is a class the sensors never need to catch.
- **The agent's permission boundary.** Which files it may edit,
  which commands it may run, declared in the agent's own settings.
  A convention the agent physically cannot violate costs nothing to
  enforce.
- **Layered documents.** Conventions, specification, feature
  inventory, how-to-test — separated, so each stays short enough to
  survive in context, and the agent reads the one the task needs.

## Computational sensors: one fast command

Everything mechanical runs under a single command the agent invokes
after every change — `harness:fast` by whatever name the stack
prefers. Its members, stack-agnostic:

| Sensor | Catches |
|---|---|
| The test suite | Behaviour that stopped holding |
| Type check | Contracts that stopped holding |
| Ambient-authority check | Inner layers touching clock, randomness, environment, network, filesystem directly |
| Dependency-direction check | Imports that cross the architecture against the arrow |
| Vocabulary check | Implementation terms leaking into domain code |

The instruments differ per ecosystem — a linter rule, ArchUnit,
import-linter, NetArchTest, deptrac, a 20-line script over the import
graph — and the sensor is the invariant, not the tool. A slower
bundle (coverage, mutation testing, dead-code detection) runs at
milestones rather than every change.

**Error messages state the fix.** The agent repairs in one iteration
what the message tells it to do, and spends iterations guessing at
what the message only laments. "Domain code must not read the clock;
inject the Clock port from application" repairs itself; "invalid
dependency" does not.

## The inferential sensor

Judgments no rule can compute — naming, granularity, features nobody
asked for — go to a review prompt run against the specification. Its
findings are claims, not verdicts, and each lands in exactly one of
four bins:

1. The finding is right → fix the code.
2. The finding is right about a wrong spec → fix the spec.
3. The finding recurs → mechanize it into a computational sensor.
4. The finding is wrong → reject it, and say why in the review
   prompt so it is not raised again.

Bin 3 is where the harness grows; a correction that passes through
it stops consuming review attention forever.

## Test the harness

A sensor that has never caught anything is indistinguishable from a
broken one. Write deliberate violations — one per convention — and
watch each sensor fire; the violations that pass silently mark the
next sensors to build. This is the same discipline as seeing a test
red before trusting it green, applied to the gates themselves.

## The conversion habit

A correction spoken to the agent lasts one session. The habit that
compounds: when the same correction is about to be given a second
time, convert it — into a permission, a lint rule, a sensor, a line
in the conventions document — before giving it. The session's
knowledge freezes into the repository's enforcement, and next
session starts where this one ended instead of where it began.

## When to apply

Sensors are an investment repaid per session, so the tiers differ:

- **The free layer goes everywhere**: strictest toolchain mode, the
  permission boundary, fix-stating error messages, the conversion
  habit. Fixed cost near zero, no upkeep.
- **Each paid sensor is added reactively**: after a violation is
  observed, never speculatively. A sensor built for a violation that
  never occurs is upkeep with no revenue, and the deliberate-violation
  test cannot justify it — only a real miss can.
- **Nothing is frozen mid-exploration.** A sensor is policy compiled
  into a gate; while the architecture is still moving, every gate
  built on it is rebuilt with it. Freeze after the shape settles —
  the same timing as extracting a seam when the second consumer
  arrives, not before.
- **Skip the harness entirely** for spikes, throwaway scripts, and
  single-session work: when the harness would outlive the code, it
  is ceremony.
