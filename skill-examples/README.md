# Aether Skill Examples — CCPRM Model & Analytics Wiki (Confluence backend)

Copy-paste source for the wiki-maintenance skills in the Aether Orchestration Plane,
**tailored to this repo** (CCPRM Model & Analytics knowledge base). Read `SCHEMA.md` and
`CLAUDE.md` first — those two files are the contract; these skills only encode the workflow.
The wiki backend is **internal Confluence** (via the Confluence MCP). This GitHub repo is the
staging platform for authoring the schema, skills, and instructions.

Each file holds the three GUI fields (**name / category / description**) followed by the
**markdown instruction** to paste into the skill body.

## Architecture & hard rules assumed by every skill

- **Working language is English.**
- **Backend = Confluence** (one space; top-level pages `internal` / `external` / `knowledge`).
  internal/ + knowledge/ are the golden answer scope; external/ is cited, never our golden source.
- **No PR/CI gate.** Every write **publishes as a new Confluence version under review**: the
  agent runs the `lint-wiki` checks itself, then publishes with `status: review` + `needs-review`
  and notifies the owner — **never** silently overwriting a `stable` page. A human flips to stable.
- **Versioning = native Confluence version history** (each publish = a version, diffable). On
  re-ingest add a "Changes in this version" section (the annual-review diff record).
- **Read path for Q&A = direct Confluence MCP reads** (page body + properties), not RAG chunks.
- **Front-matter mapping:** structured fields → page **properties**; `type`/`status`/`surface`/
  `tags` + `id` + `review-YYYY` → **labels**; hierarchy (`parent`, surface) → **page tree**;
  `references`/`model`/topic links → **Confluence page links**.
- **Never guess** (SCHEMA §5). Unsourced → `open_questions`, set `completeness` honestly; an
  agent answering replies **"Not documented."**
- **Never delete/reword human review notes** (inline comments / `> [!review]` callouts); preserve
  verbatim, strike superseded body text instead.
- Raw source PDFs live in **SharePoint / GCS**, never pasted into Confluence (only the
  `source_refs` pointer is stored). Security profile: **restricted**, never `privileged`.

| File | name | category |
|------|------|----------|
| `01-ingest-source.md` | `ingest-source` | data processing |
| `02-query-wiki.md` | `query-wiki` | data processing |
| `03-lint-wiki.md` | `lint-wiki` | logging |
| `04-reindex-wiki.md` | `reindex-wiki` | data processing |
| `05-mindmap.md` *(optional)* | `mindmap` | other |
| `06-connect-source.md` *(optional)* | `connect-source` | api integration |

> Markdown is the **authoring** format only. Confluence stores ADF/XHTML and the round-trip is
> lossy — don't rely on reading Markdown back out of Confluence unchanged.
