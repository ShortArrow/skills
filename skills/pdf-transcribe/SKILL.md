---
name: pdf-transcribe
description: Discipline for transcribing a PDF into Markdown with the current host's PDF reader or PDF skill. Write only what the page shows — never infer a table, relation, or entity that is not there. Use when asked to convert a PDF to Markdown or document a specification, especially for design documents, data models, and forms where one invented line misleads whoever implements from it.
---

# PDF to Markdown

Use the PDF capability native to the current host.

- In Claude Code, the `Read` tool opens PDFs directly. `pages` selects the
  range, up to 20 pages per call, and is required for a PDF longer than 10
  pages.
- In Codex, use the installed PDF skill or the runtime's PDF
  extraction/rendering tools. Follow that skill's render-and-verify
  procedure when visual layout affects the transcription.

```
Read(file_path="spec.pdf", pages="1-5")
```

The example above is Claude Code syntax. Do not emit it as a Codex tool
call. In Claude Code no conversion to images is needed. In Codex, render
pages when its PDF workflow requires visual verification.

## What this skill governs

Not the procedure — the discipline. Reading a PDF is easy; transcribing
one faithfully is not the same thing.

## Not allowed

Nothing may reach the output that the page does not show.

- **Do not infer.** No table or relation that the diagram does not draw
- **Do not complete.** No entity conjured from the shape of an attribute
  name
- **Do not fill silently.** Mark what cannot be read:
  `(illegible: note at lower right of p.12)`

When in doubt, ask rather than fill. In a design document, one completed
line sends the whole implementation the wrong way.

## Working through it

1. **Agree the range and the destination** — which pages, and whether
   this appends to an existing file or starts a new one
2. **Read 5 to 10 pages at a time** — the limit is 20, but accuracy rises
   as the window narrows
3. **Write only what was read** — do not scaffold sections for pages you
   have not seen
4. **Report per range** — pages covered, what they contained, what comes
   next

## Conversion

| Source | Markdown |
|---|---|
| Major / minor heading | `#` `##` / `###` |
| List | `- item` / `1. item` |
| Table | Markdown table, columns aligned |
| Figure, illustration | `[Figure] <caption>` plus the content in prose |
| Quotation, comment | `> quoted` |
| Emphasis | `**bold**` |

Keep page numbers as `(p.12)`. Someone will need to check the transcript
against the original.

## Long documents

Anything past 20 pages spans sessions. Track the ranges in `task.md`.

```markdown
# PDF transcription

## Progress
- [x] p1-20: overview and use cases
- [ ] p21-40: data model (resume here)
- [ ] p41-60: screen specifications
```

Because the work crosses sessions, "resume here" is the handover.

## Before calling it done

- [ ] Table columns line up
- [ ] Heading levels match the original
- [ ] Figures are described
- [ ] Page numbers are traceable
- [ ] Nothing was written from inference
