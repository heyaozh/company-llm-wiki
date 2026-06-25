name: ingest-source
category: data processing
description: Distill a raw source (PDF / SharePoint doc / blog / screenshot) into an atomic wiki note per SCHEMA, commit to git, mirror to Memory with tags.

---

# Ingest Source → Wiki Note

You turn ONE raw source into ONE distilled, atomic wiki note. The Git MCP repo is the
source of truth; Memory is a tagged cache. ALWAYS load `SCHEMA.md` first and follow it
verbatim.

## Inputs (any one)
- A PDF the user uploaded to the Knowledge base, or a file in a connected SharePoint MCP.
- A URL (blog / arXiv / docs).
- A screenshot (read the image directly — no OCR).
- A chat transcript file.

## Steps
1. READ the source. Screenshots → read image. URLs → fetch. PDFs → read natively
   (do NOT convert PDF to markdown; math gets mangled).
2. For papers: identify the underlying paper (title/authors), search for arXiv/DOI,
   and set the Better BibTeX citekey as the slug. Confirm with the user if ambiguous.
3. CHECK `index.md` for an existing note on this topic.
   - If found → UPDATE it: keep `slug`, bump `updated`. Do not duplicate.
   - Else → CREATE a new note.
4. ARCHIVE the raw source:
   - Papers: the PDF stays in Zotero/Knowledge base — do NOT commit PDFs to git.
   - Non-papers (blog/screenshot/transcript): save the text as markdown under the matching
     raw/external bucket (`external/article`, `external/paper`, etc.).
5. DISTILL into the matching wiki path (`paper|concept|method|project`) using the matching
   SCHEMA template:
   - Full YAML front matter (global + the type's additions).
   - Prose: Chinese-primary, English on technical terms.
   - `## Key figures & formulas`: transcribe key equations to LaTeX, headline results as a
     markdown table, extract the 1 key figure into `assets/<citekey>/` and embed by basename.
   - Set `reading: "unread"`. NEVER set `priority`. NEVER change `reading` after this.
   - `source_refs`: raw path(s) + URL. `zotero_link` for papers.
6. LINK to ≥2 existing wiki notes (link rule). If <2 exist, link to index sections.
7. COMMIT to git via the Git MCP (note + raw + assets in one commit).
8. MIRROR to Memory: upsert the note body, with tags derived from front matter:
   `scope:wiki`, `type:<type>`, `domain:<domain>`, `reading:unread`, plus topic tags.
9. LOG: append `YYYY-MM-DD — ingested <slug>` to `log.md` (git).

## Hard rules
- Git is written BEFORE Memory. Memory must always be reconstructable from git.
- Preserve every `[^me-*]` footnote and `[!me]` callout verbatim (user-annotation protocol).
- Never invent data tokens — use the SCHEMA controlled vocabulary only; `Other` requires `data_note`.
