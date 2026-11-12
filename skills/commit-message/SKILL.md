---
name: commit-message
description: |
  Writing a commit message that keeps its shape, triggered by the moments the shape collapses: about to write a subject with no type prefix, about to join two changes with "and" or し、, about to end the subject with a full stop or 。, about to commit with no body when the diff had a reason, about to write the body as a list of the files touched, or about to let a Japanese message keep its summary and lose its structure. The form is one line of type and summary, a blank line, then the body — and it holds in English while Japanese collapses to a single compound sentence, because 〜し、〜を変更 is grammatically easier than splitting it. Use before every commit, in any language, and when a subject is about to carry two verbs.
allowed-tools: Bash, PowerShell, Read, Grep
---

# Commit message

A commit message has one structure, and it is not a style preference:

```
<type>(<scope>): <summary>

<body>
```

Git reads it.
Everything up to the first blank line is the title,
and `git log --oneline`, `git format-patch`'s `Subject:`,
every forge's commit list and every release tool take that line alone.
A message with no blank line after the first has no body as far as git is concerned — the whole thing is the title.
So the blank line is not formatting,
it is the delimiter between two fields.

## Why this skill is mostly about Japanese

The structure is easier to keep in English than in Japanese,
and the reason is grammatical rather than careless.

English resists the compound subject because a second change needs a second sentence,
and a second sentence in the title reads as obviously wrong.
Japanese offers the 連用形 join (`〜し、` followed by the next clause),
which strings any number of changes into one grammatical sentence that still reads naturally:

```
❌ ST7789Vドライバの初期化を修正し、画面の向きをランドスケープモードに変更
```

That is two changes, one line, no body, no type.
It is not bad Japanese;
it is good Japanese doing the body's job in the title's field.
The fix is to notice that 連用形 in a subject is the signal for a split:

```
✅ fix(st7789v): 初期化シーケンスを修正

初期化中に MADCTL を送っていたため、向きの設定がリセットされていた。
送信順を入れ替え、初期化後に MADCTL を送る。

画面の向きの変更は別コミットに分けた。
```

Two changes in one subject means one of three things: two commits,
or one commit whose summary names the single outcome both serve,
or one commit whose subject names the outcome and whose body lists the parts.
Never one subject with both verbs.

## The subject line

- **A type**, from the set the repository already uses.
  `feat` for a feature and `fix` for a bug fix are the two the specification pins;
  the rest (`docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`) are conventional and a repository's own history is the authority on which it uses.
  Read it before inventing one.
- **A scope** in parentheses when the repository uses them:
  a noun naming the area, not the file path.
- **The summary**, in the imperative or as the state the change produces — "giving orders to the codebase",
  in git's own phrase.
  Not "〜を変更しました", not "[このコミットは]〜する".
- **No full stop.** No `.`, no `。`.
  Git's own convention omits it,
  and the title is a field value rather than a sentence.
- **Lowercase after the prefix** in English,
  unless the word is capitalised for another reason (`HEAD`, a product name).
  Japanese has no case, so this rule simply does not apply — which is one fewer thing to get wrong,
  not permission to drop the rest.

Fifty characters is git's soft limit for the summary,
and a soft limit is what it says:
this catalogue's own median subject is 74 and it is readable,
because the length buys the outcome rather than a second change.
A subject long because it names one thing precisely is fine;
a subject long because it carries two is the defect above.
For Japanese, count the limit in display width,
where most characters are two columns wide — so roughly 25 to 30 characters reaches the same width,
and a subject beyond that is usually compound.

## The body

The body earns its blank line by answering what the diff cannot show.
Git's own guidance asks for the problem first:

1. **What is wrong without this change**, in the present tense.
   "The code does X when given Y", not "used to do".
2. **Why this change solves it**, rather than how — the how is the diff.
3. **What else was tried and discarded**, when something was.
4. **What a reviewer raised** and how it was settled, when that happened.

A body that lists the files touched adds nothing:
`git show --stat` already has them.
A body restating the subject in longer words adds nothing either.
When the diff is genuinely self-explanatory — a typo,
a version bump — no body is the right answer.
A Japanese subject that joins two clauses with 連用形 is not that case:
its second clause is a reason or a second change,
and belongs in the body or in a commit of its own.

Wrap the body at a width a terminal can read;
72 columns is the usual choice, and `git log` indents by four,
so wider lines wrap raggedly.
In Japanese, break at the 読点 on a long sentence rather than at a column count.

What goes *in* the body as opposed to a document is `clean-docs`' question,
not this skill's: the commit answers for its own diff,
and a standing design intent is named by its title rather than copied in.

## Breaking changes and footers

A breaking change is marked, not described in passing:
`!` before the colon (`feat(api)!: …`), or a `BREAKING CHANGE:` footer,
which must be uppercase.
Footers come one blank line after the body,
each a token with `-` for spaces (`Reviewed-by:`, `Refs:`),
and tooling parses them,
so an ordinary sentence placed where a footer goes will be read as one.

Issue references go in a footer or the body, not in the subject,
where they spend the title's width on a number the forge already links.

## Before committing

```bash
git diff --staged --stat          # one change, or two?
git log --oneline -20             # which types and scopes this repository uses
```

The first command is the one that catches the defect this skill exists for.
If `--stat` shows two unrelated areas,
the subject is about to need 連用形 or "and",
and the fix is `git reset` and two commits rather than a longer line.

## Checklist

- [ ] Type present, taken from the repository's existing set
- [ ] One change in the subject — no 連用形, no "and", no second verb
- [ ] Imperative or outcome, not 〜しました
- [ ] No `.` and no `。` at the end of the subject
- [ ] A blank line after the subject, or the body is not a body
- [ ] Body says what was wrong before, in the present tense,
  not which files moved
- [ ] No body only where the diff genuinely needs none
- [ ] Breaking change marked with `!` or an uppercase `BREAKING CHANGE:` footer
- [ ] Japanese message checked against the same list as an English one

## How this connects

`clean-docs` decides what information belongs in a commit message at all,
and which questions go to a document instead;
this skill decides the message's form once that is settled.
`plain-language` and `unmachine-prose` govern the body's prose,
including the Japanese tells.
`pull-request` owns the PR body,
which answers at branch scope what a commit message answers at diff scope.
`tidy-first` is why a commit has one change to describe:
a message that cannot be written without 連用形 is usually reporting that the commit was never split.

## Sources

- Git, "SubmittingPatches" (git-scm.com/docs/SubmittingPatches):
  the 50-character soft limit, the `area: ` prefix convention,
  the omitted full stop, lowercase after the prefix,
  the imperative mood ("as if you are giving orders to the codebase"),
  the four things a body explains,
  and the present tense for the problem statement.
- Git, "git-commit" DISCUSSION (git-scm.com/docs/git-commit):
  "a single short (no more than 50 characters) line summarizing the change, followed by a blank line and then a more thorough description";
  the text up to the first blank line is the title, used throughout git,
  including `git format-patch`'s `Subject:`.
- Conventional Commits 1.0.0 (conventionalcommits.org, CC BY 3.0):
  the `<type>[(scope)]: <description>` form,
  `feat` and `fix` as the two typed by the specification,
  other types allowed,
  the body beginning one blank line after the description,
  footers one blank line after the body with `-` for whitespace in the token,
  and breaking changes marked by `!` in the prefix or an uppercase `BREAKING CHANGE` footer.

The 72-column body wrap is convention rather than a rule either source states;
neither git page gives a body width.
The claim that Japanese collapses for a grammatical reason rather than a careless one is this catalogue owner's reading of the grammar,
not a published finding.
