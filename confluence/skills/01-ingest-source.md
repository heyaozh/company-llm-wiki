name: ingest-source
category: data processing
description: Distill a source document into the right internal doc(s) + the knowledge layer (model + topics), honestly, and publish to Confluence as a new version under review. Never overwrite a stable page silently, never guess.

---

# Ingest Source → Internal Doc + Knowledge Layer

**FIRST, read the Wiki Contract.** Before anything else, read the two **Wiki Contract** pages —
**SCHEMA** and **AGENT** — in the wiki space via the **Confluence MCP**, and follow them verbatim.
Everything below is the workflow; those two pages are the contract.

Distill ONE source into the wiki. Working language: **English**. Backend = **internal Confluence**
via the **Confluence MCP**. Authoring format is Markdown; Confluence stores ADF/XHTML, so treat
Markdown as *input only* (the round-trip is lossy). Security profile: **restricted** (never
privileged). Raw source files stay in SharePoint/GCS — never paste their content into Confluence.

## Confluence layout
- **One space**, three top-level parent pages: `internal`, `external`, `knowledge`.
- Hierarchy = **page tree**: a doc's `parent` → its parent page; surface → top-level page.
- Metadata maps onto **page properties + labels** (SCHEMA §2.3).

## Inputs (any one)
- A path/link in SharePoint or GCS, or a connected SharePoint MCP file.
- A PDF uploaded to the conversation / Knowledge base.
- A URL (regulation, paper, article).

## Steps
1. READ the full source (read PDFs natively; do NOT rely on Knowledge-base RAG chunks for
   ingest — ingest needs the complete document).
2. PLACE the internal document. Decide its level (`policy` / `framework` / `concept` / `manual`);
   for a `concept`, set `concept_kind` (`methodology` | `pricing` | `risk`). Set `parent`.
   - CHECK FOR AN EXISTING PAGE FIRST: search Confluence by the `id:` label. If the source
     already has a page → UPDATE it (new version; see step 7). Keep `id`, bump `version`, refresh
     `last_reviewed` / `review_year`. Never duplicate.
   - `id` = stable key with the correct prefix (`pol-`/`fwk-`/`con-`/`man-`/…), stored as a
     property AND an `id:<id>` label so it survives renames.
3. HONESTY (SCHEMA §5, hard rule). Set `source_refs`. Set `completeness` honestly. Record every
   unknown in `open_questions`. **Do NOT guess** data schemas, results, or IT details.
4. DISTILL the knowledge layer:
   - Create/update the `model` overview page under `knowledge` (id `model-<slug>`).
   - Extract atomic, model-agnostic `topic` pages under `knowledge` (id `topic-<slug>`), one idea
     per page; merge into an existing topic, never duplicate.
   - Cross-link concept ↔ model ↔ topics with real **Confluence page links**.
5. LINK every new page to ≥ 2 existing pages. If too few exist, link the surface's top-level page
   and note the gap in `open_questions`.
6. VALIDATE (agent-side, replaces CI): run the `lint-wiki` checks on the page about to be
   published; fix all failures BEFORE publishing.
7. PUBLISH via the MCP (each publish = a new page version):
   - Create/update the page in the correct page-tree position; set properties + labels (SCHEMA §2.3).
   - **Versioning / annual review:** on an update, add a **"Changes in this version"** section at
     the top summarising what changed vs. the prior version and why (do this regardless of native
     diff support). Apply a `review-YYYY` label when this publish is the annual review.
   - **Review gate:** never silently overwrite a `stable` page. Publish with `status: review` +
     a `needs-review` label and notify the `owner`. A human flips `status` to `stable`. New pages
     start at `draft` or `review`, never `stable`.
8. LOG: append one row to the **Change log** page (date · id · action · version · note); update
   the **index** page.

## Hard rules
- All writes publish as a new version under review. Never overwrite a `stable` page silently;
  never set `status: stable` yourself.
- Properties/labels must satisfy SCHEMA §2 exactly; every id in
  `model`/`parent`/`derives_from`/`implements`/`references` must resolve to a real page.
- Preserve every human review note verbatim (AGENT §3) — inline comments / `> [!review]` callouts;
  strike superseded body text instead and keep the note.
- Do not extend the controlled vocabulary (SCHEMA §3) without explicit approval. Never `privileged`.
