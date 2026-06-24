# CLAUDE.md — CCPRM Model & Analytics Wiki Operating Manual

This repository is an **LLM-maintained knowledge base** for the **Model & Analytics** team
under **CCPRM (Central Clearing Counterparty Risk Management)**. The team holds
**methodology (theory & mathematical model)** documents and distills them into atomic,
interconnected **concept** notes plus a tracked library of methodology →
business-requirement → specification documents. The pattern is deliberate: a methodology doc
is distilled into reusable concepts the same way a research paper is distilled into concepts.

**Before doing anything, read [`SCHEMA.md`](SCHEMA.md)** — the strict contract for file
structure, YAML front matter, controlled vocabulary, and lint rules. *This* file is the
**operational layer**: what to read, what to touch, and how the recurring workflows run.

Working language is **English** for all content, fields, identifiers, and commit messages.

---

## 1. Knowledge surfaces & query scope (hard rule)

| Surface | Path | Default behaviour |
|---------|------|-------------------|
| **Curated wiki** | `methodology/`, `business-requirements/`, `specifications/`, `concepts/`, `models/` | **Default scope** — the only source of "facts" for Q&A, summaries, and agent answers. |
| **Raw sources** | The team's original documents (Confluence / SharePoint / Databricks / shared drive) — **not in this repo** | Read **only** during `/ingest` or explicit source lookup. Never the default answer source; never rewritten here. |
| **Metadata** | `SCHEMA.md`, `index.md`, `log.md` | Structure & operations. |

**Never fabricate.** Answer only from the curated wiki. When the wiki has no sourced answer,
reply **"not documented"** and surface the relevant `open_questions` — do not infer data
schemas, numerical results, or implementation details that are not in a `source_refs`
document. This is the hard "don't guess" rule (`SCHEMA.md` §4).

---

## 2. Recurring workflows

Invoke these by name (e.g. "run `/ingest <doc>`"). Each is a procedure, not a black box.

- **`/ingest <source path | link>`** — Distill a source methodology document into a
  `methodology` note **and** extract the atomic `concept` notes it rests on. Full pipeline in §4.
- **`/lint`** — Run `python tools/validate_wiki.py` plus the review checks below; report only,
  never auto-delete. Flag: dangling references, broken traceability chains, stale
  `review_year`, `completeness` ≠ `complete` with empty `open_questions`, and **orphan
  concepts** (a concept with no inbound link from any methodology/spec/other concept).
- **`/reindex`** — Rebuild [`index.md`](index.md) from every document's front matter (models,
  methodology, concepts, requirements, specifications).

---

## 3. Human review notes are sacred

The wiki **body** is the agent's golden source. Reviewers (humans) layer **annotations** on
top — questions, caveats, sign-off notes. These are **not** golden source.

- A human note is written as a `> [!review]` callout or an inline `<!-- review: … -->`
  comment.
- **Never** distill, quote, or propagate a review note as fact.
- **Never** delete, move, or reword a review note. Only the author removes it.
- When an edit removes the text a note refers to, keep the note and mark the old text
  `~~struck~~` rather than dropping it.

Preserve every `[!review]` callout and `<!-- review … -->` comment verbatim when re-editing
a page.

---

## 4. Ingest pipeline (methodology → wiki + concepts)

Runs on whatever LLM/agent maintains the repo; uses only Markdown + Python + Git.

1. **Read the source.** The agent is given a path or link to the original methodology
   document. Read it; do not copy it into the repo (raw sources live in the team's doc system).
2. **Identify the model.** Determine which model it belongs to. Create or find the model page
   `models/model-<slug>.md` (the spine of the traceability chain).
3. **Create / update the methodology note.** `methodology/meth-<slug>.md` per `SCHEMA.md`
   §5.1. If a note for this source exists, **update it** (keep `id`, bump `version`, update
   `last_reviewed` / `review_year`) — do not duplicate. Set `source_refs` to the source.
   Set `completeness` honestly and record every unknown in `open_questions`. **Do not guess**
   data fields, results, or IT details.
4. **Distill atomic concepts.** Pull the reusable primitives the document rests on (e.g. an
   initial-margin measure, an expected-shortfall estimator, a simulation scheme) into
   `concepts/concept-<slug>.md` — **one concept per file**, model-agnostic. Create if missing,
   update if it exists. Cross-link methodology ↔ concept.
5. **Link.** Connect the new note to **at least two** existing wiki pages (§6 link rule).
6. **Log & reindex.** Append one line to [`log.md`](log.md); update [`index.md`](index.md).

Everything in English.

---

## 5. Concept distillation rule

A **concept** note is an **atomic, reusable, model-agnostic primitive** — the company analogue
of a research "concept" note. It is the shared-vocabulary layer beneath the methodology
documents:

- One concept = one idea = one file. Do not bundle several concepts into one note.
- A concept is **not** tied to a single methodology; several methodologies should link to the
  same concept. If two notes overlap, **merge** into the existing one rather than duplicate
  (keep its `id`).
- Concepts carry the same honesty rules: cite `source_refs`, mark gaps in `open_questions`.

---

## 6. Conventions & guardrails

- **English** is the working language for every file and field.
- **`id` = filename**; never rename casually (it breaks links).
- **Every new page links ≥ 2 existing pages** (`SCHEMA.md` §6 cross-links). If fewer than two
  valid targets exist, link the relevant `index.md` and note the gap.
- **One structural edit → one line in `log.md`** (`YYYY-MM-DD — <change>`).
- **Do not expand the controlled vocabulary** (`SCHEMA.md` §3) without explicit human approval;
  record any approved addition in `log.md`.
- **Annual review:** bump `version`, `review_year`, `last_reviewed`; tag the review
  `review-YYYY` (see `CONTRIBUTING.md`).
- **Run `/lint` before committing.** Keep diffs clean and atomic so review and yearly diffs
  stay readable.
- **Never guess** (`SCHEMA.md` §4). **Never delete human review notes** (§3 above).
