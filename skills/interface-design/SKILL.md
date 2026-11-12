---
name: interface-design
description: |
  Deciding how a screen looks and behaves, triggered by the moments that hand the decision to the user unworked: about to ask which layout, which colour, which placement, how to draw a diagram, how wide a pane, how to split a view; about to call a visual choice a matter of taste; about to treat "it looks fine" as having checked it; about to ship a control sized by eye; about to read an automated accessibility pass, or a Lighthouse score of 100, as a clean bill of health. Most of these have an answer in a published standard, a measurable threshold, or one screenshot — WCAG 2.2 fixes contrast, target size, reflow and focus; a design system fixes spacing and components; axe-core finds about 57% of WCAG issues, and Lighthouse's accessibility score is that same engine weighted, so both leave the rest to a person. What survives is a genuine question, asked with the evidence attached. Use before asking any question about appearance, layout or interaction, and before calling a UI done.
allowed-tools: Bash, PowerShell, Read, Grep, Glob, WebFetch
---

# Interface design

A question about a screen is not a question about taste.
Contrast has a ratio, a target has a size,
a reflow has a width at which it must still work,
and a layout has an information order that follows from what the reader does first.
These are decided by measurement and by published standards,
so handing them to the user as "which do you prefer" spends their attention on work that was the agent's.

What remains after measuring is a real question,
and this skill exists to make that remainder small and to attach the evidence to it.
`own-the-call` governs how it is then asked.

## The moments this replaces

| About to… | Instead |
|---|---|
| ask which colour, size, spacing or placement the user prefers | measure against the standard below; ask only what no threshold settles |
| call a visual choice subjective | name the criterion it fails or passes — contrast, target size, reflow width, focus visibility, information order |
| say "it looks fine" | open it, screenshot it, and say what was measured at which viewport |
| size a control by eye | 24×24 CSS px is the WCAG AA floor; a design system may set a stricter one (Material: 48dp) |
| pick colours from a palette by appearance | compute the ratio: 4.5:1 body text, 3:1 large text and non-text |
| ship a layout checked at one window size | check 320 CSS px wide and 256 CSS px high, where reflow must still work |
| read a green axe run as accessible | axe finds about 57%; the rest is keyboard, focus order, and meaning |
| design a component that a design system already defines | take theirs, and say which one |
| ask how to draw a diagram | decide from what the reader traces first, then show one rendering |

## Decide from the standard before asking

Four bodies answer most of it,
and they do not fully agree — where they differ,
the stricter number is the one to meet,
because meeting it satisfies both.

**WCAG 2.2** is the floor, and it is normative: a W3C Recommendation,
and ISO/IEC 40500.
Target Level AA; AAA is not reachable for all content and the W3C says so.

| Criterion | Level | Threshold |
|---|---|---|
| 1.4.3 Contrast (Minimum) | AA | 4.5:1 text; 3:1 for large text (≥18 pt, or 14 pt bold) |
| 1.4.11 Non-text Contrast | AA | 3:1 against adjacent colours |
| 1.4.4 Resize Text | AA | usable at 200% |
| 1.4.10 Reflow | AA | no two-axis scrolling at 320 px wide or 256 px high |
| 1.4.12 Text Spacing | AA | line height ≥1.5×, paragraph ≥2×, letter ≥0.12×, word ≥0.16× font size |
| 2.4.7 Focus Visible | AA | a mode where the focus indicator is visible |
| 2.4.11 Focus Not Obscured | AA | the focused control is not entirely hidden |
| 2.5.8 Target Size (Minimum) | AA | 24×24 CSS px, or 24 px spacing |
| 2.4.13 Focus Appearance | AAA | ≥2 px perimeter, 3:1 between focused and unfocused |
| 2.5.5 Target Size (Enhanced) | AAA | 44×44 CSS px |

**A design system** settles what WCAG leaves open: spacing scale,
type scale, component anatomy, colour roles.
Taking its component is not a shortcut,
it is the decision — and it carries the accessibility work already done.
Material Design 3 sets 48×48 dp touch targets,
stricter than WCAG's 24 px,
and asks that colour be chosen as roles (`primary`, `on-primary`, `surface`) rather than fixed hex,
so theming and dark mode follow without a second decision.
For Japanese public-facing work the Digital Agency design system (`design.digital.go.jp`, β版 as a living standard) carries components,
guidance and tokens, with the tokens and sample components on GitHub under MIT.

**axe-core** measures what can be measured, and states its own limit:
about 57% of WCAG issues on average.
A green run is therefore evidence about 57% of the question,
and saying "axe passes" without that number overstates it — `measured-claims` applies to this figure like any other.

```bash
npx @axe-core/cli http://localhost:5173 --tags wcag2a,wcag2aa,wcag22aa
npx lighthouse http://localhost:5173 --only-categories=accessibility --quiet
```

**Lighthouse's accessibility score is the same engine wearing a number.** Its audits are axe-core rules — each one links to Deque's rule page — so the 57% is inherited,
and the score adds two ways to be misread.
It is a *weighted* average,
weights 3 to 10 by axe's user-impact assessment,
and manual and best-practice audits are excluded from it entirely,
so the arithmetic cannot reach the part a person has to check.
Each audit is also binary:
one unlabelled button fails "Buttons have an accessible name" outright,
with no partial credit.
So 100 means "the weighted automatic subset passed",
and the honest report of a perfect score says that, not "accessible".
Use it for the ranked list of what to fix;
use axe's JSON when the finding matters more than the ranking.
Lighthouse's *performance* categories are `web-perf`'s,
not this skill's.

What neither can see: whether focus order follows reading order,
whether a label names the thing it labels,
whether an icon's meaning survives without colour,
whether the layout's information order matches the task.
Those are read by a person, and the person can be the agent.

## Look at it, then say what was seen

An interface claim with no observation behind it is `measured-claims`' rumour in another medium.
The host has a browser, so the observation is available:

```
mcp__claude-in-chrome__navigate      → the page
mcp__claude-in-chrome__read_page     → structure, headings, labels
mcp__claude-in-chrome__computer      → screenshot at a stated viewport
mcp__claude-in-chrome__resize_window → 320 px, to test reflow
```

Report the viewport with the finding.
"It looks right" names no width and no measurement;
"at 320 px the second column wraps under the first and nothing scrolls sideways" is a reading someone can check.
Keyboard order is walked with Tab and reported as the sequence observed,
because that is the half axe does not cover.

## Information order is derived, not chosen

Where something goes follows from what the reader does with it,
which is `reader-map`'s question applied to a screen: who arrives,
what they came to do, what they need first.
A control used once at setup and a control used every minute do not compete for the same place.

So "where should this go" is answered by naming the task,
not by listing three positions.
When two tasks genuinely compete and neither dominates,
that is the remainder worth asking about — and it is asked with the competing tasks named,
not as a choice of corners.

The same holds for a diagram.
What the reader traces first decides the direction of flow;
the shape follows the trace,
and one rendering is shown rather than three described.

## What is genuinely the user's

Three things survive measurement:

- **Which audience or market the interface serves**,
  when that is not yet fixed — it decides which standard applies at all (`regulated-claims` for a regulated market).
- **A brand constraint** — a required colour, typeface or mark.
  The constraint is theirs; whether it meets 4.5:1 is still measured,
  and a brand colour that fails is reported with the ratio and the nearest passing variant.
- **A trade-off already measured on both sides**,
  where the evidence does not decide: density against scannability,
  one screen against two.
  Asked with both measurements attached,
  it is a question `own-the-call` admits.

Everything else — contrast, spacing, target size, focus, reflow,
component choice, diagram shape,
placement that follows a task — is decided and reported.

## Checklist

- [ ] Contrast computed, not eyeballed: 4.5:1 text, 3:1 large and non-text
- [ ] Interactive targets ≥24×24 CSS px,
  or the design system's stricter figure
- [ ] Checked at 320 px wide and 256 px high with no two-axis scrolling
- [ ] Focus visible on every interactive element, and not obscured
- [ ] Tab order walked and reported as observed
- [ ] Components taken from the design system where it defines one,
  and named
- [ ] axe or Lighthouse run, and the 57% limit stated rather than implied
- [ ] A Lighthouse accessibility score reported as the weighted automatic subset,
  never as "accessible"
- [ ] Every appearance claim carries the viewport it was observed at
- [ ] Questions left for the user are the three kinds above,
  with evidence attached

## How this connects

`own-the-call` shapes the question that survives this skill;
most questions about a screen should not reach it.
`reader-map` supplies the task order this skill applies to placement.
`measured-claims` governs every ratio and percentage here,
the 57% included.
`document-structure` and `cognitive-rhythm` own prose on a page;
this skill owns the frame around it.
`any-screenshot` is how a screen is captured outside a browser.
Loading and interaction speed,
Core Web Vitals and Lighthouse's performance score belong to `web-perf` in the `cloudflare` plugin;
this skill takes only Lighthouse's accessibility category.

## Sources

- W3C, "Web Content Accessibility Guidelines (WCAG) 2.2",
  W3C Recommendation dated 12 December 2024 (www.w3.org/TR/WCAG22/):
  the four principles, the A/AA/AAA levels,
  and the removal of 4.1.1 Parsing as obsolete.
- W3C, "How to Meet WCAG 2.2 (Quick Reference)" (www.w3.org/WAI/WCAG22/quickref/):
  every threshold in the table above,
  read at Level AAA to include 2.4.13 and 2.5.5.
- Deque Labs, axe-core README (github.com/dequelabs/axe-core): MPL-2.0;
  rules mapped to WCAG 2.0, 2.1 and 2.2 at A, AA and AAA;
  "you can find on average 57% of WCAG issues automatically".
- Chrome for Developers, "Accessibility scoring in Lighthouse" (developer.chrome.com/docs/lighthouse/accessibility/scoring):
  the score is a weighted average, weights 3 to 10,
  "based on axe user impact assessments",
  with every audit linking to a Deque University axe-core 4.11 rule page;
  each audit is binary;
  manual and low-impact audits are excluded from the score.
  The page does not itself say a perfect score means the page is accessible — nor does it say the opposite,
  so the warning above is this skill's.
- デジタル庁デザインシステム (design.digital.go.jp): v2.18.2,
  labelled β版 in the sense of a living standard.
  The site states no WCAG level and no JIS X 8341-3 target.
  `digital-go-jp/design-tokens`,
  `design-system-example-components-react` and `-html` on GitHub are MIT.
- Material Design 3's 48×48 dp touch target and its colour-role guidance are taken from secondary sources citing m3.material.io,
  not from that site: its pages render by script and could not be read here.
  The 48 dp figure is a design recommendation,
  not a platform-enforced minimum.

The claim that these sources disagree,
and that the stricter figure is the one to meet,
is this catalogue owner's reading rather than any of their published positions.

Neither command above was run while this skill was written:
both fetch a package at first use,
and the sandbox here declines to execute freshly downloaded code.
The flags come from each tool's documentation rather than from a run,
so the first use in a project is also the first test of the invocation.
