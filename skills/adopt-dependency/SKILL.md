---
name: adopt-dependency
description: Deciding whether to take on third-party code — a package, a skill, a plugin, a tool — and what to do when an installer refuses one. A guard firing is a question to answer, not an obstacle to route around, and the checks that feel like verification (a matching version number, a familiar-looking maintainer handle) establish nothing. Use before adding a dependency, and whenever an install is blocked by a download threshold, a release-age hold, or a signature check.
allowed-tools: Bash, Read, WebFetch
---

# Adopting a Dependency

## A guard that fires is a question

```
refusing to add X: only 198 weekly downloads (threshold: 1000)
1 newer release hidden by minimum_release_age
```

These are heuristics for the two shapes malicious packages take: freshly
published, and barely used. Both fire on plenty of legitimate software —
that is what a heuristic does.

So the guard has asked a question. Answer it, or do not proceed. Looking
for the bypass flag first is answering a different question, which is how
to make the message stop.

## Separate what is asserted from what you inferred

The decisive test is mechanical: **what does the artifact itself claim,
and what did you supply?**

An npm package with no `repository` field claims no link to any
repository. That is not thin evidence — it is the absence of a claim. If
you connected the package to a GitHub project, you did that, not the
package.

Two things that feel like verification and are not:

- **A version matching an upstream tag.** Anyone can publish that version
  number. Matching upstream is what a convincing impostor does.
- **A maintainer handle resembling the repository owner.** Circumstantial.
  Similar names are the mechanism of the attack, not evidence against it.

## What actually verifies

A **provenance attestation** binds the published artifact to the
repository and CI job that built it, cryptographically. It cannot be
asserted by someone who does not control that pipeline.

```bash
curl -s https://registry.npmjs.org/<package> | jq '.versions[."dist-tags".latest].dist'
```

```jsonc
"signatures": [ ... ]        // npm served this. Says nothing about who built it.
"attestations": {
  "provenance": { "predicateType": "https://slsa.dev/provenance/v1" }
}                            // this is the one that matters
```

mise verifies SLSA provenance for its aqua and github backends, and
reports it during install — `[2/3] verify SLSA provenance`.

**Absence is not guilt.** Most packages are published by hand and carry no
attestation. It means provenance cannot be established mechanically, so
adopting it is a judgement someone makes and owns, rather than a check
that passed.

## Match the fix to the exception

A per-package problem gets a per-package answer.

Reaching for a global setting to admit one package removes the guard for
**everything declared now and later**, and does it silently — the guard
is not overridden, it stops being consulted. Nothing will warn at the next
addition.

If the tool offers no narrow escape, that is the answer: **do not manage
that package with that tool.** Install it directly, outside the manifest,
where the decision stays visible and local.

Where a bypass is genuinely right, make it surface — a check that reports
it, not a comment in a config file nobody reads again.

## Skills are code

A skill is not documentation. `SKILL.md` is instruction an agent follows
and `scripts/` is executed, both with the agent's full permissions.
Everything above applies to adopting one, and install counts on a public
registry measure popularity rather than review. See `find-skills`.

## The four questions

1. What does the artifact assert, and what did I infer?
2. Is there an attestation, or only a signature?
3. Does my fix apply to exactly what needed the exception?
4. If this cannot be verified, am I stating that plainly — or reporting it
   as verified?
