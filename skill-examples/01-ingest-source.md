name: ingest-source
category: data processing
description: Distill a source document into the right internal doc(s) + the knowledge layer (model + topics), honestly, and publish to Confluence as a new version under review. Never overwrite a stable page silently, never guess.

---

# Ingest Source → Internal Doc + Knowledge Layer (Confluence backend)

Distill ONE source into the wiki per `SCHEMA.md` + `CLAUDE.md`. ALWAYS read both first and
follow them verbatim. Working language: **English**.

Backend = **internal Confluence** via the **Confluence MCP**. Authoring format is Markdown;
Confluence stores ADF/XHTML, so treat Markdown as *input only* (the round-trip is lossy — never
rely on reading Markdown back out unchanged). Security profile: **restricted** (never
privileged). Raw source files stay in SharePoint/GCS — never paste their content into Confluence.

## Confluence layout (assumed)
- **One space**, three top-level parent pages: `internal`, `external`, `knowledge`.
- Hierarchy = **page tree**: a doc's `parent` field → its parent page; surface → top-level page.
- Front matter has no native home — map it (see "Front-matter mapping" below).

## Inputs (any one)
- A path/link in SharePoint or GCS, or a connected SharePoint MCP file.
- A PDF the user uploaded to the conversation / Knowledge base.
- A URL (regulation, paper, article).

## Steps
1. READ the full source (read PDFs natively; do NOT rely on Knowledge-base RAG chunks for
   ingest — ingest needs the complete document).
2. PLACE the internal document. Decide its level in the hierarchy
   (`policy` / `framework` / `concept` / `manual`); for a `concept`, set `concept_kind`
   (`methodology` | `pricing` | `risk`). Set `parent` to its place in the tree.
   - CHECK FOR AN EXISTING PAGE FIRST: search Confluence by the `id` property/label
     (see mapping). If the source already has a page → UPDATE it (this becomes a new version;
     go to step 7's versioning rules). Keep `id`, bump `version`, refresh
     `last_reviewed` / `review_year`. Never duplicate.
   - `id` = stable key, with the correct type prefix (`pol-`/`fwk-`/`con-`/`man-`/…). The
     page *title* may be the human title; `id` lives in a page property AND a label so it
     survives renames.
3. HONESTY (SCHEMA §5, hard rule). Set `source_refs`. Set `completeness` honestly
   (`theory_only` | `partial` | `complete`). Record every unknown in `open_questions`.
   **Do NOT guess** data schemas, results, or IT/implementation details.
4. DISTILL the knowledge layer:
   - Create/update the `model` overview page under `knowledge` (id `model-<slug>`).
   - Extract atomic, model-agnostic `topic` pages under `knowledge` (id `topic-<slug>`),
     one idea per file; merge into an existing topic, never duplicate.
   - Cross-link concept ↔ model ↔ topics with real **Confluence page links** (not Markdown
     relative paths — those don't resolve in Confluence).
5. LINK every new page to ≥ 2 existing pages. If too few exist, link the surface's top-level
   page and note the gap in `open_questions`.
6. VALIDATE (agent-side, replaces CI). Run the `lint-wiki` checks against the page you are
   about to publish: required fields present, `id` prefix matches `type`, value in controlled
   vocabulary, `concept` has `concept_kind`, `specification` has `implements`,
   `business_requirement` has `derives_from`, and every id named in
   `model`/`parent`/`derives_from`/`implements`/`references` resolves to an existing page.
   Fix all failures BEFORE publishing.
7. PUBLISH to Confluence via the MCP (each publish = a new page version):
   - Create or update the page in the correct page-tree position.
   - Set page properties + labels per the mapping below.
   - **Versioning / annual review:** if this updates an existing page, this publish creates a
     new Confluence version. Add a **"Changes in this version"** section at the top of the body
     summarising what changed vs. the prior version and why (do this REGARDLESS of whether the
     MCP can produce a native diff — if it can, reference/attach it; if it cannot, the summary
     IS the diff record). Apply a `review-YYYY` label when this publish is the annual review.
   - **Review gate (replaces PR):** never silently overwrite a `stable` page. Publish with
     `status: review` (property) + a `needs-review` label, and notify the `owner`. A human flips
     `status` to `stable`. New pages start at `status: draft` or `review`, never `stable`.
8. LOG: append one row to the **Change log** Confluence page (date · id · action · version).

## Front-matter mapping (SCHEMA §2 → Confluence)
- **Page properties** (queryable via Page Properties Report): `id`, `type`, `status`, `owner`,
  `version`, `review_year`, `last_reviewed`, `completeness`, `concept_kind`, `model`,
  `derives_from`, `implements`, `source_refs` (as SharePoint/GCS pointers — never file content).
- **Labels**: `type:<t>`, `status:<s>`, `surface:internal|external|knowledge`, free-form `tags`,
  `id:<id>` (for lookup), `review-YYYY`, `needs-review` while under review.
- **Page tree**: `parent` and surface grouping.
- **In-body Confluence links**: `references`, `model`, topic cross-links.

## Hard rules
- All writes publish as a new version under review. Never overwrite a `stable` page silently;
  never set `status: stable` yourself.
- Front matter (now properties+labels) must satisfy SCHEMA §2 exactly; every referenced id must
  resolve to a real page.
- Preserve every human review note verbatim (CLAUDE §3). In Confluence these live as inline
  comments / `> [!review]`-style callout panels — never delete, reword, or distill them; strike
  superseded body text instead and keep the note.
- Do not extend the controlled vocabulary (SCHEMA §3) without explicit approval.
- Raw PDFs stay in SharePoint/GCS. Never use the `privileged` profile.
