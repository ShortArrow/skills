---
name: agent-harness
description: |
  Making an AI coding agent hold a project's conventions by construction, in any language: prose conventions decay as the session grows, while gates — types, lints, permissions — bind at turn 1 and turn 200 alike. Feedforward narrows what can be written (strictest toolchain mode, permission boundary, layered docs); computational sensors in one fast command catch the rest; an inferential review is triaged into fix-code, fix-spec, mechanize, or reject; error messages state the fix; deliberate violations test the harness itself. The free layer goes everywhere, each paid sensor is added after an observed violation, and nothing is frozen mid-exploration. Use when setting up a repository for AI coding sessions, when the same correction repeats across sessions, when conventions in CLAUDE.md are being ignored, when a skill that ran yesterday fails today at a different step, and when reviewing generated code stops scaling.
---

# The Agent Harness

A convention written in prose is followed the way instructions are followed:
well at the start, worse as the context grows.
A convention compiled into a gate — a type error, a lint rule,
a denied command — binds at turn 1 and at turn 200 with the same force.
The harness is the discipline of moving conventions from the first form into the second,
one at a time, until the human reviews decisions instead of output.

Two mechanisms, in order of leverage.

## Feedforward: narrow what can be written

Prevention needs no detection.
Three surfaces, each with an equivalent in every stack:

- **The toolchain's strictest mode.** Whatever the compiler,
  turn everything on: `strict` in tsconfig, `#![deny(warnings)]`,
  `mypy --strict`, `<Nullable>enable</Nullable>` with warnings as errors,
  `-Wall -Werror`.
  A class of violation the toolchain rejects is a class the sensors never need to catch.
- **The agent's permission boundary.** Which files it may edit,
  which commands it may run, declared in the agent's own settings.
  A convention the agent physically cannot violate costs nothing to enforce.
- **Layered documents.** Conventions, specification, feature inventory,
  how-to-test — separated,
  so each stays short enough to survive in context,
  and the agent reads the one the task needs.
  The root document says which layer answers which task,
  not that every layer is read first.
  "Before every edit, read architecture.md, database.md and deployment.md" spends the context of a typo fix on three documents it will not use;
  "architecture.md for a service boundary, database.md for a schema change, deployment.md when preparing a deployment" is read once,
  at the moment it applies.
- **Permitted workflows, stated.** A boundary says what the agent may not touch;
  it also has to say what it may do without asking,
  or a careful model stops at every step of work that was always safe.
  "The local tests use disposable fixtures and have no production access: run them, fix what the requested change broke, and rerun without asking at each step" is a permission,
  and it belongs beside the prohibitions.
  A stronger model reads a strong prohibition as a reason to pause;
  the prohibitions written to restrain a weaker one are the first thing to reread when a newer model keeps stopping.

## Computational sensors: one fast command

Everything mechanical runs under a single command the agent invokes after every change — `harness:fast` by whatever name the stack prefers.
Its members, stack-agnostic:

| Sensor | Catches |
|---|---|
| The test suite | Behaviour that stopped holding |
| Type check | Contracts that stopped holding |
| Ambient-authority check | Inner layers touching clock, randomness, environment, network, filesystem directly |
| Dependency-direction check | Imports that cross the architecture against the arrow |
| Vocabulary check | Implementation terms leaking into domain code |

The instruments differ per ecosystem — a linter rule, ArchUnit,
import-linter, NetArchTest, deptrac,
a 20-line script over the import graph — and the sensor is the invariant,
not the tool.
A slower bundle (coverage, mutation testing, dead-code detection) runs at milestones rather than every change.

**Error messages state the fix.** The agent repairs in one iteration what the message tells it to do,
and spends iterations guessing at what the message only laments.
"Domain code must not read the clock; inject the Clock port from application" repairs itself;
"invalid dependency" does not.

## The inferential sensor

Judgments no rule can compute — naming, granularity,
features nobody asked for — go to a review prompt run against the specification.
Its findings are claims, not verdicts,
and each lands in exactly one of four bins:

1. The finding is right → fix the code.
2. The finding is right about a wrong spec → fix the spec.
3. The finding recurs → mechanize it into a computational sensor.
4. The finding is wrong → reject it,
   and say why in the review prompt so it is not raised again.

Bin 3 is where the harness grows;
a correction that passes through it stops consuming review attention forever.

## Test the harness

A sensor that has never caught anything is indistinguishable from a broken one.
Write deliberate violations — one per convention — and watch each sensor fire;
the violations that pass silently mark the next sensors to build.
This is the same discipline as seeing a test red before trusting it green,
applied to the gates themselves.

## Repair the step, not the run

An agent that succeeds four runs in five is not one that fails at random one time in five.
On the AppWorld benchmark a ReAct agent on GPT-4.1 passed 77% of runs and only 53% of tasks five times out of five (Duesterwald et al., 2026),
and the gap is the steps where the model's next action is close to a coin toss.
A skill "that worked yesterday" fails today at one of those steps,
and the step that failed today is not the only one of its kind.

So a skill's repair is a harness of its own,
not a "fix it" typed at the failure.
Take the trajectory that failed and resample each step several times;
the steps whose answers scatter are the brittle ones,
including the ones that happened to pass this time,
and each gets a guideline written into the skill at that step.
That procedure raised five-of-five success by 16 points on the same tasks and 13 on similar ones.
The moment to write the guideline is the one the resampling found,
not the one that happened to fail.

Two things practice adds.
A fix has to land everywhere the same instruction is stated:
one repair fixed the script a skill ran and left the same defect in the example command in the skill's prose,
and only a second check step caught it.
And a fix is tried on inputs beyond the one that failed,
the one that used to pass included;
a fetch that stopped at 100 records was rerun at 25,
125 and 203 before the change was kept.

## The conversion habit

A correction spoken to the agent lasts one session.
The habit that compounds:
when the same correction is about to be given a second time,
convert it — into a permission, a lint rule, a sensor,
a line in the conventions document — before giving it.
The session's knowledge freezes into the repository's enforcement,
and next session starts where this one ended instead of where it began.

## When to apply

Sensors are an investment repaid per session, so the tiers differ:

- **The free layer goes everywhere**: strictest toolchain mode,
  the permission boundary, fix-stating error messages,
  the conversion habit.
  Fixed cost near zero, no upkeep.
- **Each paid sensor is added reactively**: after a violation is observed,
  never speculatively.
  A sensor built for a violation that never occurs is upkeep with no revenue,
  and the deliberate-violation test cannot justify it — only a real miss can.
- **Nothing is frozen mid-exploration.** A sensor is policy compiled into a gate;
  while the architecture is still moving,
  every gate built on it is rebuilt with it.
  Freeze after the shape settles — the same timing as extracting a seam when the second consumer arrives,
  not before.
- **Skip the harness entirely** for spikes, throwaway scripts,
  and single-session work: when the harness would outlive the code,
  it is ceremony.

## Sources

- OpenAI, "Rethinking skills and prompts for GPT-6 Astra" (developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra),
  read 2026-09-14: conditional document references instead of a stack read before every edit,
  explicit permission for safe workflows,
  and the observation that guidance written for an earlier model overconstrains a later one.
- Evelyn Duesterwald, Benjamin Elder, Lilian Ngweta,
  Shashanka Ubaru and Malgorzata Zimon,
  "Closing the Consistency Gap: Self-Evolving Agents That Learn to Stay on Course",
  arXiv 2609.08832, submitted 2026-09-08; abstract read 2026-09-17:
  the consistency gap,
  the analyser that finds low-consistency steps by resampling,
  and the guideline generator that writes memory for them.
- ナレッジセンス, 「SKILL.md を良くする技術。AIのブレをなくす。」,
  zenn.dev/knowledgesense/articles/9adf1e9b17ffd6,
  published 2026-09-15 and read 2026-09-17:
  the repair procedure as a skill of its own,
  the fix that missed the prose copy of the command,
  and the rerun at three record counts.
  The rest of this skill rests on practice.
