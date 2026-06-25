name: ingest-source
category: data processing
description: Distill a source document into the right internal doc(s) + the knowledge layer (model + topics), honestly, and open a PR. Never write main, never guess.

---

# Ingest Source → Internal Doc + Knowledge Layer

Distill ONE source into the wiki per `SCHEMA.md` + `CLAUDE.md`. ALWAYS read both first and
follow them verbatim. Working language: **English**.

## Inputs (any one)
- A path/link in SharePoint or GCS, or a connected SharePoint MCP file.
- A PDF the user uploaded to the conversation / Knowledge base.
- A URL (regulation, paper, article).

Do NOT copy raw source files into the repo. Reference them via `source_refs`.

## Steps
1. READ the full source (read PDFs natively; do not rely on RAG chunks for ingest).
2. PLACE the internal document. Decide its level in the hierarchy
   (`policy` / `framework` / `concept` / `manual`); for a `concept`, set `concept_kind`
   (`methodology` | `pricing` | `risk`). Set `parent` to its place in the tree.
   - If a doc for this source already exists → UPDATE it: keep `id`, bump `version`,
     refresh `last_reviewed` / `review_year`. Never duplicate.
   - `id` = filename stem, with the correct type prefix (`pol-`/`fwk-`/`con-`/`man-`/…).
3. HONESTY (SCHEMA §5, hard rule). Set `source_refs`. Set `completeness` honestly
   (`theory_only` | `partial` | `complete`). Record every unknown in `open_questions`.
   **Do NOT guess** data schemas, results, or IT/implementation details.
4. DISTILL the knowledge layer:
   - Create/update the `model` overview page (`knowledge/model/model-<slug>.md`).
   - Extract atomic, model-agnostic `topic` notes (`knowledge/topic/topic-<slug>.md`),
     one idea per file; merge into an existing topic, never duplicate.
   - Cross-link concept ↔ model ↔ topics with relative Markdown links.
5. LINK every new page to ≥ 2 existing pages. If too few exist, link the relevant
   `index.md` and note the gap.
6. VALIDATE: run `python tools/validate_wiki.py` and fix any failures before proposing.
7. LOG one line to `log.md`; update `index.md` (and per-folder index).
8. OPEN A PULL REQUEST with all changes. **Never write `main`** — CI gates, a human merges.
9. (Optional) Mirror distilled pages to Memory as a tagged cache: `surface:internal|knowledge`,
   `type:<type>`, `model:<id>`. Git stays the source of truth.

## Hard rules
- All writes go through a PR. Never commit to `main`.
- Front matter must satisfy SCHEMA §2 exactly (required + type-specific fields; every id named
  in `model`/`parent`/`derives_from`/`implements`/`references` must exist).
- Preserve every `> [!review]` callout and `<!-- review: … -->` comment verbatim (CLAUDE §3).
- Do not extend the controlled vocabulary (SCHEMA §3) without explicit approval.
