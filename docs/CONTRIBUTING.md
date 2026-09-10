# Contributing

## Layout

```
skills/<name>/SKILL.md           the skill
skills/<name>/scripts/           anything it executes
skills/<name>/references/        material the body links to, read only when needed
tests/<name>/firing-tests.md     its scenarios and recorded runs
tests/fixtures/<name>/           the repository a scenario runs in
tests/check-portability.ps1      manifests, hosts, invariants, sources
tests/check-descriptions.sh      the description length cap
tests/reflow-prose.py            wraps prose one sentence per line, in any language
tests/run-firing-tests.sh        the behavioural runner
.claude-plugin/marketplace.json  plugin grouping
docs/design-intent.md            the forces behind these shapes
```

`SKILL.md` opens with YAML frontmatter holding `name` and `description`.
The name matches the directory;
the portability check refuses a mismatch.

## Language-neutral rules, with language layers

A skill's body is the rule that holds in every language, in English.
What differs by language goes in `references/<language>.md` (today `references/japanese.md`),
and the body names it from a section called **Language layers**,
placed right after the introduction and worded the same way in every writing skill,
so the layer is loaded whenever the draft is Japanese and never otherwise.
Material specific to a market rather than a language takes the same shape (`regulated-claims` and its `references/japan.md`) and carries its own `## Sources` block.
The portability check refuses a layer file the body does not name,
and a named path the directory lacks.
`docs/design-intent.md` carries the reasoning.

## Prose is wrapped one sentence per line

In every language: a sentence ends a line,
a sentence wider than about 72 columns breaks after a clause separator (, ; : 、),
and a line never breaks inside a word, a bracket or a quoted phrase.
A fixed-width wrap re-flows a whole paragraph in the diff when one word changes and puts breaks where no reader pauses;
in Japanese it also splits words and can render as a stray space.
`python tests/reflow-prose.py <file>` applies the rule,
with the sentence ends and separators of each language layered on from the characters in the paragraph,
and refuses to write if anything but whitespace and blockquote markers would change.
`--check` lists the files that are not yet in shape.

## The description is the part that is always on

A host loads every installed skill's name and description into every session and reads the body only when the skill fires.
In Claude Code, `claude plugin details <name>` shows that split for one skill.
Codex applies a discovery budget when many skills are installed and shortens descriptions to fit it.

So the description is paid for continuously, and it has one job:
to let the model decide whether the skill applies.
Detail goes in the body, where it costs nothing until it is used.
Synonyms of words the description already contains add nothing,
and a second language adds nothing either — the skills Anthropic ships are English-only and fire in every language.
What the description should spend its words on is the boundary with its siblings:
four skills here answer to the word "screenshot",
and the description is the only place that can say which one owns which case before one of them fires.

Descriptions here are written as the moments the skill replaces ("about to …"),
because a skill fires on a moment and a glossary fires on nothing.
`docs/design-intent.md` carries the reasoning.

`tests/check-descriptions.sh` refuses a description over 1,200 characters.
The host's listing truncates near 1,536, the tail is what it cuts,
and the tail is where the "Use when" triggers sit.

## Host branches

A skill whose procedure names a tool (`AskUserQuestion`, `Read` with `pages`, `Agent` with a model) carries one row per host — Claude Code,
Codex, Copilot, Cursor,
Gemini CLI — and a final "Any other host" row that gives a substitute procedure.
Rows hold only mechanisms a host's own documentation states,
with the date checked;
an undocumented capability is written as `not documented (checked <date>)` and falls through to the last row.
The Claude Code and Codex rows are pinned by string invariants in the portability check,
so a later edit that generalises them into host-neutral prose fails the run.
Prose-only skills need none of this.

## Sources

A skill that names a public standard (ISTQB, an RFC, SemVer, a style guide, a regulator's guidance) carries a `## Sources` block naming the version,
the section and the date it was read.
The portability check requires the block, and a date in it,
wherever such a name appears.
Skills that rest on practice rather than a standard say so and cite nothing;
dressing them in a standard's name is refused.

## Checks

Run before every commit:

```powershell
pwsh -File tests/check-portability.ps1
```

It checks every manifest and resource reference, marketplace membership,
the host rows and invariants above, the Sources blocks,
and the README headings an installer looks for.
Failures print one per line and the run exits 1.

`tests/check-descriptions.sh` is meant to run as this clone's pre-commit hook.
Wire it once:

```bash
printf '#!/usr/bin/env bash\nexec bash "$(git rev-parse --show-toplevel)/tests/check-descriptions.sh"\n' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Firing tests

A skill's description is its implementation,
and `tests/<skill>/ firing-tests.md` is its test:
three scenarios that must make the skill fire and two that must not,
each a prompt run in a fresh headless session inside a copy of the skill's fixture.

```bash
tests/run-firing-tests.sh <skill> [out-dir] [scenario-regex]
MAX_TURNS=10 tests/run-firing-tests.sh <skill>
```

Each session costs a full context of installed skills,
on the order of a dollar, so run a scenario, not the suite,
while iterating.
Six turns shows whether the skill fired;
a scenario whose expectation is a finished edit needs `MAX_TURNS` raised,
because a session that writes the failing test first spends its budget there.

Two rules from experience, both in `docs/design-intent.md`:

- The negative scenarios stand clear of the trigger.
  A "should not fire" prompt aimed at a file that also carries a real instance of the trigger asks the skill to stay silent about a defect in front of it,
  and a session that does the edit and then names that defect as out of scope has behaved correctly.
  Move the scenario, not the description.
- Record every run under `## Recorded runs`, the failed ones included,
  with what the transcript showed and what changed because of it.
