# Contributing

## Layout

```
skills/<name>/SKILL.md           the skill
skills/<name>/scripts/           anything it executes
skills/<name>/references/        material the body links to, read only when needed
hooks/                           scripts the plugin hooks run (Claude Code only)
tests/<name>/firing-tests.md     its scenarios and recorded runs
tests/fixtures/<name>/           the repository a scenario runs in
tests/check-portability.ps1      manifests, hosts, invariants, sources
tests/check-descriptions.sh      the description length cap
tests/skill-doctor.py            health of every skill, as the host will see it
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
In Claude Code, `claude plugin details <plugin>@shortarrow-skills` shows that split for one plugin,
skill by skill.
Codex applies a discovery budget when many skills are installed and shortens descriptions to fit it.

So the description is paid for continuously, and it has one job:
to let the model decide whether the skill applies.
Detail goes in the body, where it costs nothing until it is used.
Synonyms of words the description already contains add nothing,
and a second language adds nothing either;
the skills Anthropic ships are English-only and fire in every language.
What the description should spend its words on is the boundary with its siblings:
four skills here answer to the word "screenshot",
and the description is the only place that can say which one owns which case before one of them fires.

Descriptions here are written as the moments the skill replaces ("about to …"),
because a skill fires on a moment and a glossary fires on nothing.
`docs/design-intent.md` carries the reasoning.

Claude Code caps the listing twice,
and both caps were read from the client's own code on 2026-09-10 (`skillListingMaxDescChars`, `skillListingBudgetFraction`).
One description is cut at 1,536 characters.
GitHub Copilot CLI is stricter:
its skill schema rejects a description over 1,024 characters and the skill is not listed at all (read from its bundle on 2026-09-11; four skills here were missing from Copilot until they were shortened).
`tests/check-descriptions.sh` and `tests/skill-doctor.py` refuse one over 1,000 so both the tail and the Copilot listing survive.
The whole listing is also capped at 1% of the context window in characters,
8,000 at a 200k window.
Over that, the skills with the fewest recorded uses lose their descriptions first and are listed by name only,
so a skill that has never fired cannot fire on its description,
and a new skill starts at the back of that queue.
This catalogue's forty-one descriptions total about 28,000 characters,
so with two or more of its plugins installed the default budget is exceeded.
`tests/skill-doctor.py` prints the per-plugin totals and the fraction that would hold this catalogue alone;
the README tells installers to raise `skillListingBudgetFraction` (0.05 holds the whole catalogue) or to install one plugin.
The budget is shared with every other plugin and the bundled skills,
and the real figures are in the debug log:
on 2026-09-10 a session with this catalogue,
two other plugins and the bundled skills listed 59 skills at 37,792 characters against a 30,000-character budget at the default fraction,
and nothing was truncated at 0.05.

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

## A hook for the moment a description cannot see

A description fires when the model decides what to do next.
A body typed inside a Bash call (`gh pr create --body ...`) is written without that pause,
at the end of a long session, from the conversation,
and that is where pull request bodies go sloppy.
The writing-skills entry in `.claude-plugin/marketplace.json` declares a PreToolUse hook on `gh pr *` that injects the rule as context before the command runs:
the body is written from the commits and the diff, says what changed,
why and what is left, carries no conversation-local labels,
and is checked against `clean-docs`,
`document-structure` and `plain-language`. the body is written from the commits and the diff,
says what changed, why and what is left,
carries no conversation-local labels,
and is checked against `clean-docs`,
`document-structure` and `plain-language`.
The hook is written inline in the marketplace entry,
because that is the only form a marketplace entry accepts (a file path is not, and a `hooks/hooks.json` at the shared plugin root would register once per plugin);
the script it runs, `hooks/pr-body-context.sh`,
prints one JSON object. the script it runs prints one JSON object.
Hooks are Claude Code's mechanism and no other host runs them,
so the descriptions still carry the moment for Codex and Copilot;
the hook is the backstop for the one place a description is blind.

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
python tests/skill-doctor.py --strict
```

The first checks every manifest and resource reference,
marketplace membership, the host rows and invariants above,
the Sources blocks, and the README headings an installer looks for.
Failures print one per line and the run exits 1.

The second is this repository's answer to the health report Claude Code does not have.
Claude Code's own `/skill-doctor` reports usage and context cost,
and `claude plugin validate` checks manifests;
on 2026-09-10 the latter passed a SKILL.md whose description the runtime cannot parse and one 2,600 characters long.
`tests/skill-doctor.py` reads each skill the way the runtime does and prints one row per skill:
the frontmatter parses as YAML with a matching name and a non-empty description (a plain scalar containing ": " is not YAML, and the runtime then loads no description at all, which `claude plugin details` shows as `< 20` always-on tokens);
the description is under 1,000 characters (warning),
1,024 (error: Copilot CLI drops the skill) and 1,536 (error: Claude Code truncates);
every `references/*.md` is named in the body and every named path exists;
a skill with `references/japanese.md` has a Language layers section;
and the files follow the one-sentence-per-line rule.
It ends with the listing budget per plugin.
It exits 1 on an error, and with `--strict` on a warning;
`--json` prints the same report as one object.
It takes any skills directory as its argument,
so it also serves for a catalogue that is not this one.

`tests/check-descriptions.sh` is the description cap alone, in bash,
meant to run as this clone's pre-commit hook.
Wire it once:

```bash
printf '#!/usr/bin/env bash\nexec bash "$(git rev-parse --show-toplevel)/tests/check-descriptions.sh"\n' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## The checkout in Codex and Copilot CLI

Both hosts read `~/.agents/skills/<name>/SKILL.md`.
On the machine that holds this checkout,
link the working tree there instead of installing a copy,
so an edit is live in every host at once and the firing tests,
the doctor and the hosts all read the same files:

```powershell
$dst = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force $dst | Out-Null
Get-ChildItem skills -Directory | ForEach-Object {
  New-Item -ItemType Junction -Path (Join-Path $dst $_.Name) -Target $_.FullName
}
```

A skill added later needs its own junction;
removing one is deleting the junction.
Checked on 2026-09-11: Codex 0.146.0 listed all 42 skills through the junctions,
and Copilot CLI 1.0.83 listed 38 until the four descriptions over its 1,024-character cap were shortened,
then all 42.
Elsewhere, `npx skills add ShortArrow/skills -g` installs a copy,
as the README says.

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
