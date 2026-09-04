---
name: github-paths
description: |
  The paths GitHub reads by name, triggered by the moments a file lands where nothing reads it: about to write a contributing or security section into the README, about to save FUNDING.yml, CITATION.cff or dependabot.yml somewhere other than the one directory GitHub scans for it, about to add a second CODEOWNERS or README without knowing which one wins, about to put an issue or pull request template on a feature branch and expect it to appear, about to delete or gitignore a generated file so it stops flooding review, about to hand-write release notes GitHub would categorise from labels, or about to copy the same community files into every repository of an organisation. A file at the wrong path is not wrong, it is invisible, and the page that would have shown it stays blank. Use when adding a repository-level file, when a sidebar button or template fails to appear, when a diff is dominated by generated output, and when setting up several repositories at once.
allowed-tools: Read, Edit, Write, Grep, Glob, Bash
---

# GitHub reads some paths by name

A repository is a tree of files, and GitHub reads most of it as
files. A few dozen paths it reads as *slots*: put a file there and a
button, a template chooser, a review request or a sidebar link
appears; put the same file one directory over and nothing does. The
failure never raises. The sponsor button is simply not there, and the
person who wrote the file assumes the feature is off.

## The moments this replaces

| About to… | Instead |
|---|---|
| write "How to contribute" or "Reporting a vulnerability" into the README | `CONTRIBUTING.md` and `SECURITY.md` in `.github/`, the root or `docs/`; GitHub links them from the issue and pull request flows and the Security tab, and the README can point at them |
| save `FUNDING.yml` at the root | `.github/FUNDING.yml` on the default branch is the only place the sponsor button reads |
| put `CITATION.cff` in `docs/` | the root, on the default branch, or "Cite this repository" never appears |
| add a second `CODEOWNERS` or `README` "for the docs" | GitHub uses the first it finds, `.github/` before root before `docs/`; the other is dead |
| commit an issue or pull request template on a feature branch to try it | templates take effect only from the default branch; test them there or not at all |
| gitignore or delete `dist/` so review stops showing it | `dist/** linguist-generated` in `.gitattributes`: the file stays, the diff collapses and the language bar ignores it |
| paste the same `CODE_OF_CONDUCT.md` into forty repositories | one copy in the organisation's `.github` repository serves every repository that lacks its own |
| write release notes by hand from the merged pull requests | `.github/release.yml` categorises them by label; hand-writing is for what the labels cannot say |

## Three directories, one order

Community health files can live in three places, and when more than
one holds the same file GitHub reads only the first: **`.github/`,
then the repository root, then `docs/`**. README, CODEOWNERS and the
pull request template follow the same three locations and the same
order. So a `docs/README.md` beside a root `README.md` is ignored
rather than merged, and a `.github/CODEOWNERS` silently retires the
one at the root. Pick one location for the repository and keep every
slot file there.

Two files ignore the rule. `FUNDING.yml` is read from `.github/`
only, and `CITATION.cff` from the root only. `LICENSE` is detected at
the root, and is also the one file that cannot be inherited from an
organisation default, because a clone or a package has to carry its
own.

## The default branch is the only branch GitHub reads these from

Templates, `FUNDING.yml`, `CITATION.cff`, `dependabot.yml` and the
release notes configuration are read from the default branch. A pull
request that adds a template shows nothing until it merges, and a
CODEOWNERS file is read from the **base** branch of the pull request
it is reviewing, not from the branch that changed it. Trying a slot
file on a branch and concluding it does not work is the ordinary way
to be wrong here.

## Templates are a chooser, not a file

`.github/ISSUE_TEMPLATE/` holds one file per template: Markdown for a
prefilled body, YAML for an issue form with fields. `config.yml` in
the same directory turns the blank issue off (`blank_issues_enabled:
false`) and adds `contact_links` that route to a discussion board or
a support address instead of an issue. The chooser orders templates
by filename, YAML before Markdown, so `01-bug.yml`, `02-feature.yml`
is how the order is set.

Pull requests take one template from `pull_request_template.md` in
any of the three locations, or several from a `PULL_REQUEST_TEMPLATE/`
directory, chosen with `?template=name.md` on the new-pull-request
URL.

## Generated files are marked, not removed

A minified bundle, a lockfile, a schema emitted by a tool: review
should not read it and the language bar should not count it, and
neither is a reason to stop committing it. `.gitattributes` carries
the marks:

```gitattributes
dist/**          linguist-generated
vendor/**        linguist-vendored
docs/api/**      linguist-documentation
*.pkl            linguist-language=Python
```

`linguist-generated` hides the diff by default and removes the file
from the statistics; `linguist-vendored` and `linguist-documentation`
remove it from the statistics only; `linguist-language` reclassifies
a file the detector misreads. The change is a one-line commit, and
the file keeps its history.

## One repository serves the rest

A repository named `.github` under an organisation or a user account
holds default community health files — `CONTRIBUTING.md`,
`SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `FUNDING.yml`,
issue and pull request templates — for every repository under that
owner that has no file of its own. A repository's own file wins
whole: if it defines any issue template, none of the defaults appear.
The same repository's `profile/README.md` is the organisation's
profile page, and a public repository named after the user with a
root README is the user's.

Copying the files into each repository instead works until the first
edit, after which the copies drift and nobody can say which one is
current — the `clean-docs` failure, forty times.

## Agents read paths by name too

`.github/copilot-instructions.md` is read for every Copilot request
in the repository; `.github/instructions/*.instructions.md` with an
`applyTo` glob scopes instructions to paths; `AGENTS.md` anywhere in
the tree is read by agents with the nearest one winning, and
`CLAUDE.md` or `GEMINI.md` at the root the same way. These are slots
in the same sense as the rest: a well-written instruction file at a
path no agent reads has instructed nobody.

## What this is not

Not a style guide for what the files should say — `clean-docs` for
that, and `regulated-claims` when the README sells something. Not a
rule that every slot must be filled: a repository with no sponsor and
no citation has no reason to carry the files. The rule is only that a
file meant for a slot goes in the slot.

## Sources

- GitHub Docs, docs.github.com, read on 2026-09-04: "Creating a
  default community health file" (the file list, the three locations,
  the `.github` > root > `docs` precedence, the organisation `.github`
  repository, and that a license cannot be defaulted); "About code
  owners" (three locations, first found wins, read from the base
  branch); "About READMEs" (three locations and their order, the
  profile README); "Creating a pull request template for your
  repository" and "Configuring issue templates for your repository"
  (locations, `PULL_REQUEST_TEMPLATE/`, `config.yml` keys, default
  branch requirement, filename ordering); "About CITATION files" (root
  only, default branch, "Cite this repository"); "Displaying a sponsor
  button in your repository" (`.github/FUNDING.yml`, default branch);
  "Licensing a repository" (root, Licensee); "Automatically generated
  release notes" (`.github/release.yml`); "Dependabot options
  reference" (`.github/dependabot.yml`, default branch); "Adding
  repository custom instructions for GitHub Copilot" (the three
  instruction paths). GitHub Docs carry no version number; the date is
  the reference.
- github-linguist, `docs/overrides.md`, read on 2026-09-04: the five
  `linguist-*` attributes and which affect statistics, diffs, or both.
- joelparkerhenderson/github-special-files-and-paths (GPL-2.0-or-later)
  was the map of what to look up; it lists locations for LICENSE and
  CITATION that GitHub Docs do not confirm, so no rule here rests on it.
