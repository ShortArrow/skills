---
name: pdf-transcribe
description: Discipline for transcribing a PDF into Markdown with the current host's PDF reader or PDF skill. Write only what the page shows — never infer a table, relation, or entity that is not there. Use when asked to convert a PDF to Markdown or document a specification, especially for design documents, data models, and forms where one invented line misleads whoever implements from it.
---

# PDF to Markdown

Use the PDF capability native to the current host.

Identify the host from the tools it exposes before choosing a row:
`AskUserQuestion`, `Agent` and `Skill` mean Claude Code; a structured tool
interface with approval requests on blocked calls means Codex;
`askQuestions`, `runSubagent` and `#browser` mean Copilot in VS Code;
`/agent`, a permission prompt with a "rest of the session" option and
`--allow-all` mean Copilot CLI; an "Ask questions" tool, a Task tool and a
Browser tool mean Cursor; `ask_user`, `read_file` and subagents exposed as
tools of their own name mean Gemini CLI. A host that matches none of these
takes the last row.

| Host | How the PDF is opened |
|---|---|
| Claude Code | In Claude Code, the `Read` tool opens PDFs directly. `pages` selects the range, up to 20 pages per call, and is required for a PDF longer than 10 pages. |
| Codex | In Codex, use the installed PDF skill or the runtime's PDF extraction/rendering tools. Follow that skill's render-and-verify procedure when visual layout affects the transcription. |
| Copilot in VS Code | The PDF is attached to the chat by the user, by paste, drag-drop or context menu. A tool-read of a PDF from disk is not documented, so ask for the attachment and transcribe from the attached pages. |
| Copilot CLI | `@path` attaches the PDF, as do drag-drop and paste. Ask the user to attach it if it is not attached already. |
| Cursor | not documented (checked 2026-08-28); use the row below. The Read files tool lists images only. |
| Gemini CLI | `read_file` on the .pdf, which supports text, images, audio and PDF. There is no page range, so read the whole file and transcribe it section by section. |
| Any other host | Ask the user for a text export, or run `pdftotext -layout` where it is available and say that the layout came from a text extractor. Never write a page that was not read, never simulate a PDF tool in prose, and never fall back to another host's PDF path. |

```
Read(file_path="spec.pdf", pages="1-5")
```

The example above is Claude Code syntax.
Do not emit it as a Codex tool call, nor as any other host's.
In Claude Code no conversion to images is needed. In Codex, render pages
when its PDF workflow requires visual verification.

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
