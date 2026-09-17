# Fixture: brokenskill

A project with one installed skill, `daily-summary`,
whose fetch script stops after the first page of 100 records and whose SKILL.md repeats the same `--limit 100` command as its example.
`session.jsonl` is the transcript of a run in which the skill fetched 100 of 125 issues,
reported success, and was corrected by the user.
`data/issues.json` is the local stand-in for the API, three pages long,
so the fix can be tried at 125 and at 25 without a network.

The scenarios in `tests/repair-skill/firing-tests.md` run here.
