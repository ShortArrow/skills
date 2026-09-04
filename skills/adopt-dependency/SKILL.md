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

What that line has established depends on the level. SLSA's Build
track (v1.2) has four: **L0** "No guarantees"; **L1** "Provenance
exists", generated automatically and distributed, but trivial to
forge; **L2** "Hosted build platform", where the platform signs the
provenance itself and the consumer validates its authenticity; **L3**
"Hardened builds", where the platform prevents runs from influencing
one another and keeps the signing secret away from user-defined build
steps. A provenance file with no signature from the platform is L1,
and L1 "can be used to prevent mistakes but is trivial to bypass or
forge" — it tells you what the producer says happened, not that it
did. The line in an installer's output is worth the level behind it.

## Count against a checklist someone else wrote

"Does this project look maintained" is a judgement that a familiar
README satisfies. OpenSSF Scorecard replaces it with twenty named
checks and a score from 0 to 10, each check with a stated risk level:

```bash
scorecard --repo=github.com/<owner>/<repo>
```

The checks marked **Critical** are Dangerous-Workflow (CI workflows
with exploitable patterns) and Webhooks (unauthenticated hooks). The
**High** ones are Binary-Artifacts, Branch-Protection, Code-Review,
Dependency-Update-Tool, Maintained, Signed-Releases, Token-Permissions
and Vulnerabilities (open, unfixed, against the OSV database). The
rest — CI-Tests, License, Fuzzing, SAST, SBOM, Pinned-Dependencies,
Security-Policy, Packaging, Contributors, CII-Best-Practices — are
Medium or Low.

Two things the score is not. It scores the **repository**, so it says
nothing about whether the artifact you are about to install came from
that repository — that is the provenance question above, and the two
checks compose rather than substitute. And it is a snapshot: a
Maintained check that passed in one quarter is a rumour by the next,
the way `measured-claims` treats any dated number.

When the project publishes an SBOM (SPDX or CycloneDX are the two
formats Scorecard's SBOM check looks for), the transitive question —
what did this bring with it — has a document to count against instead
of a lockfile to read.

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

## The five questions

1. What does the artifact assert, and what did I infer?
2. Is there an attestation, or only a signature — and at which SLSA
   level?
3. What does Scorecard say, and which Critical or High checks failed?
4. Does my fix apply to exactly what needed the exception?
5. If this cannot be verified, am I stating that plainly — or reporting it
   as verified?

## Sources

- SLSA Specification v1.2 (Approved), slsa.dev — Build track levels
  L0–L3 and their requirements, from the build-track-basics page;
  wording checked on 2026-09-04. v1.0's levels page is marked retired.
- OpenSSF Scorecard, `docs/checks.md` in github.com/ossf/scorecard —
  the twenty check names and their risk levels as listed on
  2026-09-04. Checks are added over time; the list here is that date's.
- SPDX and CycloneDX are named as formats only; neither is relied on
  for a rule here.
