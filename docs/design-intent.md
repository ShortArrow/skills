# Design intent

The forces of this repository's design as they stand:
what each part protects, which forces pull against each other,
what is refused and why while that reason holds,
and how the next case of the same kind is decided.
This file is edited in place when the forces change;
its history is the series of snapshots a pile of decision records would otherwise hold.
Each section names the gate that enforces it, where one exists.

## Host-specific skill procedures

**Protects.** A skill works through its concreteness.
"Call `AskUserQuestion`" tells the model what to do;
"use the host's approval mechanism" hands the choice back to the reader.
Tool names and approval mechanisms are runtime protocol,
and the protocol is the part that must stay exact.

**In tension.** The same skill is wanted on many hosts,
and each host names its own tools.
Every added host grows the prose.
A generalisation reads as an improvement in review,
and what it deleted does not show in the diff.

**Refused, while these reasons hold.**

- Generalising a host-specific instruction into host-neutral prose.
  The dilution is invisible in a diff and permanent in effect.
- Writing a tool name or mechanism no official document states.
  A wrong concrete is worse than an honest gap;
  an undocumented capability is written as `not documented (checked <date>)` and falls through to the last row.
- Substituting one host's procedure or script on another host,
  simulating a missing tool in prose, or pretending a subagent ran.
- One section per host.
  Sections multiply the words around the procedure;
  a capability table grows by one row per host per capability instead.

**The next case.** A new host is one row per capability table,
holding only documented mechanisms with a check date,
placed above the final `Any other host` row,
which states a substitute procedure and the prohibitions.
Existing hosts' rows are not touched by the addition.

**Gate.** `tests/check-portability.ps1`:
every branching skill must name each host and `Any other host`,
and per-host invariant strings (`AskUserQuestion`, `runSubagent`, `ask_user`, `browser_agent`, …) fail the run when a row is generalised away.
Deleting a row's key string or renaming `Any other host` makes the script exit 1.

## Contracts are written as obligations, not as names

**Protects.** A rule fires when it names the moment it applies to.
The moment sits before the act:
a description written as "about to …" constrains what is about to be written,
where a rule written as "avoid …" can only be applied to what was written.
Prevention costs one reading at the moment;
correction costs a second pass,
and the habit that produced the text is still there for the next paragraph (natural-japanese states the same as 事後修正より生成時制約, read 2026-09-14).
"The caller guarantees a non-empty id" tells the next reader which side to fix when it breaks;
"follow Clean Architecture" tells them a vocabulary and leaves the decision where it was.

**In tension.** Architecture names are how the field talks,
and the stack in front of us has real layer names that appear in project files and namespaces.
Dropping them costs recognition;
keeping them invites a skill that lists vocabulary and fires on nothing.
The catalogue's own form is the tiebreaker:
every skill here states the moments it replaces,
and a skill that cannot is not yet a rule.

**Refused, while these reasons hold.**

- A skill whose body is a glossary of layer or pattern names.
  If the reader still has to decide what to do at the moment it matters,
  the rule has not been written.
- Restating an architecture's packaging as though it were the rule.
  Layer names are one arrangement of dependency direction;
  the obligation is what transfers to a stack that names its layers differently.
- Splitting one obligation across two skills because the literature splits the words.
  The contract and the interface are the same decision seen from two sides,
  so they live in one place.
- Language-specific placement inside a language-agnostic rule,
  and the reverse.
  `architect` says where a type sits,
  with the stack's spelling in its layer;
  `design-by-contract` says which way the dependency may point.

**The next case.** A new design rule is written as its firing moments first.
If the "About to… | Instead" table cannot be filled,
the material belongs in an existing skill's section, or nowhere yet.

**Gate.** `tests/<skill>/firing-tests.md` with five scenarios and `tests/run-firing-tests.sh`:
three that must fire and two that must not,
each recorded with the run that produced it.
A skill that names concepts without replacing a moment cannot pass S1–S3,
because there is no wrong action for it to catch.

## Rules rest on public standards, or say that they rest on practice

**Protects.** A reader who doubts a rule can go and check it.
"ISTQB says" is checkable only when the reader can open the same document,
so the standard has to be free, versioned and cited to the section.

**In tension.** The most precise sources are often paid (ISO/IEC/IEEE 29119, IEEE 1012),
a certification textbook,
or a well-known blog post that restates a standard from memory.
Citing the paid one looks rigorous and cannot be verified;
citing the restatement inherits its errors — a section number that names the right heading and the wrong number propagates to every file that copies it.
And some rules have no standard at all: red-green-refactor, tidy first,
the slice, the state named before the operation are practice,
and dressing them in a standard's name borrows authority the standard never gave.

**Refused, while these reasons hold.**

- A citation to a document the reader cannot open.
  Name it as a pointer if it exists, and rest the rule on the free one.
- A section number that was not read in the cited version.
  The heading is checked against the document,
  not against memory or a secondary source.
- A standard's name on a practice-derived rule.
  `tdd-cycle`, `tidy-first`, `slice-first`,
  `state-first` and `diagnose-first` say where they come from and do not cite a standard.
- A version-less citation.
  Syllabi and specifications are revised;
  the version and its date are part of the reference.

**The next case.** When a rule can be grounded,
it is grounded in the free public document, cited as name, version,
date, section, and the date it was checked,
the way `measured-claims` makes a number carry its method.
When it cannot, the skill says the rule is practice.

**Gate.** `tests/check-portability.ps1`:
a skill whose body names a standard or a paper (ISTQB, ISO/IEC, RFC, SemVer, SLSA, GSN, Diátaxis,文化庁, 消費者庁, arXiv and the rest of the pattern in the script) must carry a `## Sources` block,
and that block must contain a check date in `YYYY-MM-DD`.
Deleting the block, or the date, makes the script exit 1.

## A term read in two senses is pinned to a criterion

**Protects.** A skill is an instruction to a model,
and a model reads a term in the sense most of its training text gave it,
often not the source's: "refactoring" as any rework,
"CI" as a build server, "technical debt" as poor code.
The instruction is then carried out in the looser sense,
and the transcript does not show it,
because both sides used the same word.
A yes-or-no criterion gives the same result from either sense:
`tidy-first` does not ask what a structural change is;
it says every test stays green with none edited.

**In tension.** The field talks in these terms,
and a body that avoids them is neither found nor recognised.
Pinning costs words in a body.
A table of terms sits close to the glossary the section on contracts refuses,
and stays a rule only while every row is a test with an action attached.

**Refused, while these reasons hold.**

- "Use the term in its original sense", in any wording, as the whole rule.
  The model recalls the source's sense from the same text that loosened it,
  and answers with the looser sense under the source's name.
- A pin written from memory,
  which is the restatement the section above refuses.
  The criterion is read in the source,
  the quotation matched against the page, the date recorded.
- A pin that cannot be answered yes or no.
  A source that states a preference yields no criterion.
- Calling one sense the original or the correct one.
  The pin names whose usage it is;
  which came first is a dispute the document does not need.
- Pinning a term whose looser sense has replaced the source's.
  There the source's sense would be misread.
- A pointer to a definition in place of the criterion.
  A reader that does not doubt its own sense does not follow the pointer.

**The next case.** A skill body that leans on such a term states the criterion where the term is used.
A term with no skill of its own gets a row in `plain-language` under One sense per term,
with its quotation, source and read date in that skill's `references/pinned-senses.md`.

**Gate.** None mechanical for the sense:
a script can find the word and cannot tell which sense the sentence used.
`tests/plain-language/firing-tests.md` S1 and S2 carry a new retry reported as a refactoring;
a run passes on the Skill call alone,
so whether the term was dropped is read in the transcript.
The sources of the pinned senses do not match the pattern of the gate above,
so their read dates are kept by review.

## Language-neutral rules, with language layers

**Protects.** A writing rule that holds in every language is written once,
in English, and fires on English and Japanese drafts alike.
What holds only in Japanese (the constructions, the endings, the courtesy grammar, the worked examples) sits in `references/japanese.md`,
named from one fixed section of the body,
so a session revising Japanese reads it and a session revising English never pays for it.

**In tension.** The examples that make a rule land are bound to a language,
and a body full of Japanese examples fires only for Japanese.
The opposite pull is as real:
a body kept neutral by deleting the specifics becomes a glossary that fires on nothing.
The layer is what lets the body stay a rule and the examples stay concrete.

**Refused, while these reasons hold.**

- A Japanese-only form in a body, or a neutral rule in a layer file.
- A layer file the body does not name.
  Unlinked, it is never read.
- A skill whose whole rule is Japanese.
  `plain-japanese` was one; one claim per sentence,
  a subject that meets its predicate,
  one head per modifier and one spelling per term hold in English too,
  so it became `plain-language` with a Japanese layer.
- A translated copy of the neutral rule inside the layer.
  The layer says what is different, not what is the same.

**The next case.** A new writing skill is written neutral first.
Each moment in its table is checked against an English and a Japanese draft,
and whatever holds in only one goes to the layer.
A second language is a second layer file, named from the same section.
A stack layer is decided the same way: `architect` is written neutral,
and a language,
a framework or a binary boundary is one file under `references/`,
named from its Stack layers section and holding only what that stack spells differently.

**Gate.** `tests/check-portability.ps1`:
every `references/<language>.md` must be named in its skill's `SKILL.md`,
and every `references/` path a body names must exist.
`tests/reflow-prose.py` gives line wrapping the same shape:
one neutral rule,
and the sentence ends and separators of each language chosen from the characters in the paragraph.

## A negative scenario stands clear of the trigger

**Protects.** The two "should not fire" scenarios are what prove a skill is not always-on.
They prove it only when the skill has nothing legitimate to say:
a negative that sits beside a real instance of the trigger tests whether the skill will stay silent about a defect in front of it,
and silence there would be the wrong behaviour.

**In tension.** A fixture is built to hold the trigger,
because the positive scenarios need it,
so the easiest negative to write is an unrelated edit to the same file.
Twice that produced a session that did the edit as asked,
then named the defect beside it as out of scope — `regulated-claims` editing a page whose next section carried an unlawful claim,
`github-paths` editing a README that the fixture had pushed out of its slot.
Both were recorded as over-firing, and both were the skill working.

**Refused, while these reasons hold.**

- A negative scenario whose file or neighbourhood contains the trigger.
  If the skill would have a true sentence to add,
  the scenario is not negative.
- Weakening a description to make such a scenario pass.
  The fix is on the fixture side: a file the trigger does not touch,
  or a second fixture.
- A fixture whose own scaffolding is an instance of the trigger — a note filed under the name the skill is about,
  a README that is not where the skill says READMEs go.

**The next case.** Write S4 and S5 against a file,
a request and a neighbourhood the skill has no claim on,
and read the transcript of any negative that fires before calling it a defect:
a session that completed the request and listed the rest as out of scope has passed on behaviour,
and the scenario is what moves.

**Gate.** None mechanical.
The recorded runs in each `tests/<skill>/firing-tests.md` carry the transcript reading that decided each case,
so the next reader can check the call.
