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

## Confluence layout & target
- Publish into the **configured wiki space** — see the **Wiki location** block in the agent's
  custom instructions (space key + surface parent pages). Default there for every read and write;
  **do NOT ask the user which page to use** — derive placement from surface + `type` + `parent`
  per SCHEMA. Only ask if that block is unset or the target is genuinely ambiguous within it.
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
4. MATH & NOTATION (required — SCHEMA §6.1). The formulas and variable notation ARE the content
   of a pricing/risk model; never drop them or paraphrase them into prose.
   - Reproduce every governing equation from the source, rendered with the **LaTeX / math macro**
     (inline `$…$`-style or block) so it survives in Confluence — not as a flat-text approximation.
   - Put the **key formula(s) in the Summary**, not only deep in the body.
   - Include a **Notation table** (symbol · definition · units/domain) for every variable that
     appears, and state assumptions/conventions (e.g. discounting, day-count) when the source does.
   - Honesty still applies: transcribe only formulas the source gives; if a step is missing, note
     it in `open_questions` rather than filling in an invented expression.
5. DISTILL the knowledge layer:
   - Create/update the `model` overview page under `knowledge` (id `model-<slug>`); carry the
     governing formulas + notation table onto it (step 4 applies to the model page too).
   - Extract atomic, model-agnostic `topic` pages under `knowledge` (id `topic-<slug>`), one idea
     per page; where a topic *is* a formula/quantity, its Definition must state that formula and
     its notation. Merge into an existing topic, never duplicate.
   - Cross-link concept ↔ model ↔ topics with real **Confluence page links**.
6. LINK every new page to ≥ 2 existing pages. If too few exist, link the surface's top-level page
   and note the gap in `open_questions`.
7. VALIDATE (agent-side, replaces CI): run the `lint-wiki` checks on the page about to be
   published; fix all failures BEFORE publishing.
8. PUBLISH via the MCP (each publish = a new page version):
   - Create/update the page in the correct page-tree position; set properties + labels (SCHEMA §2.3).
   - **Versioning / annual review:** on an update, add a **"Changes in this version"** section at
     the top summarising what changed vs. the prior version and why (do this regardless of native
     diff support). Apply a `review-YYYY` label when this publish is the annual review.
   - **Review gate:** never silently overwrite a `stable` page. Publish with `status: review` +
     a `needs-review` label and notify the `owner`. A human flips `status` to `stable`. New pages
     start at `draft` or `review`, never `stable`.
9. LOG: append one row to the **Change log** page (date · id · action · version · note); update
   the **index** page.

## Hard rules
- All writes publish as a new version under review. Never overwrite a `stable` page silently;
  never set `status: stable` yourself.
- **Never drop or paraphrase math.** Every formula and variable notation from the source is
  reproduced with the math macro, the key formula appears in the Summary, and a notation table
  accompanies it (step 4). A missing derivation step goes in `open_questions`, never invented.
- Properties/labels must satisfy SCHEMA §2 exactly; every id in
  `model`/`parent`/`derives_from`/`implements`/`references` must resolve to a real page.
- Preserve every human review note verbatim (AGENT §3) — inline comments / `> [!review]` callouts;
  strike superseded body text instead and keep the note.
- Do not extend the controlled vocabulary (SCHEMA §3) without explicit approval. Never `privileged`.
