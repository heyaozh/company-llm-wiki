# CLAUDE.md — CCPRM Model & Analytics Wiki Operating Manual

This repository is an **LLM-maintained knowledge base** for the **Model & Analytics** team
under **CCPRM (Central Clearing Counterparty Risk Management)**. It mirrors our company
documents, tracks external sources, and distills both into atomic, interconnected knowledge.

**Before doing anything, read [`SCHEMA.md`](SCHEMA.md)** — the structural contract (types,
folders, front matter, vocabulary, lint rules). *This* file is the **operational layer**: what
to read, what to touch, how the workflows run. Working language is **English**.

---

## 1. Knowledge surfaces & query scope (hard rule)

| Surface | Path | Default behaviour |
|---------|------|-------------------|
| **Internal** | `internal/` (policy, framework, concept, manual, business-requirements, specifications) | Our own documents — **the golden source** for our models. Default answer scope. |
| **External** | `external/` (regulation, paper, article, other) | Outside material we track. Summarise & link; **never** treat its text as our golden source. |
| **Knowledge** | `knowledge/` (model, topic) | Our **distilled** layer — model overviews + atomic topics. Default answer scope. |
| **Raw sources** | original PDFs in SharePoint / GCS — **not in this repo** | Read **only** during `/ingest` or explicit lookup; never rewritten here. |
| **Metadata** | `SCHEMA.md`, `index.md`, `log.md` | Structure & operations. |

**Never fabricate.** Answer from internal + knowledge (and external as cited references). When
the wiki has no sourced answer, reply **"Not documented."** and surface the relevant
`open_questions` — never invent data schemas, results, or implementation details
(`SCHEMA.md` §5).

> Note on names: the internal hierarchy has a level literally called **concept**
> (methodology/pricing/risk). Our distilled atomic primitives are **`topic`** (under
> `knowledge/`), *not* `concept`. Keep the two distinct.

---

## 2. Recurring workflows

- **`/ingest <source>`** — Distill a source document into the right internal doc(s) **and** the
  knowledge layer (model + topics). Pipeline in §4.
- **`/lint`** — Run `python tools/validate_wiki.py` plus checks for stale `review_year`,
  `completeness` vs `open_questions`, and orphan topics. Report only; never auto-delete.
- **`/reindex`** — Rebuild [`index.md`](index.md) and the per-folder `index.md` files from
  front matter.

---

## 3. Human review notes are sacred

Reviewers layer annotations on top of documents as `> [!review]` callouts or
`<!-- review: … -->` comments. These are **not** golden source: never distill, quote as fact,
delete, move, or reword them. Only the author removes them. If an edit removes the text a note
refers to, keep the note and mark the old text `~~struck~~`. Preserve them verbatim on re-edit.

---

## 4. Ingest pipeline (source → internal + knowledge)

1. **Read the source.** Given a path/link (SharePoint / GCS). Do not copy raw files into the repo.
2. **Place the internal document.** Decide its level in the hierarchy (`policy` / `framework` /
   `concept` / `manual`) and, for a `concept`, its `concept_kind` (methodology/pricing/risk).
   Set `parent` to its place in the tree. If a doc for this source exists, **update** it (keep
   `id`, bump `version`, refresh `last_reviewed`/`review_year`) — never duplicate.
3. **Honesty.** Set `source_refs`; set `completeness` honestly; record every unknown in
   `open_questions`. **Do not guess** data, results, or IT details.
4. **Distill the knowledge layer.** Create/update the `model` overview page for the model, and
   extract the atomic, model-agnostic **`topic`** notes it rests on (one topic per file; merge,
   never duplicate). Cross-link concept ↔ model ↔ topics.
5. **Link.** Connect every new page to **≥ 2** existing pages.
6. **Log & reindex.** Append one line to [`log.md`](log.md); update [`index.md`](index.md).

Everything in English. All writes go through a **Pull Request** (CI gates it; a human merges).

---

## 5. Topic distillation rule

A **`topic`** is an **atomic, reusable, model-agnostic primitive** — the renamed distilled
layer (formerly "concept", renamed to avoid clashing with the internal *concept* level). One
topic = one idea = one file; several models/concepts link to the same topic; merge overlaps
into the existing topic rather than duplicating. Topics carry the same honesty rules.

---

## 6. Conventions & guardrails

- **English** everywhere. **`id` = filename**, correct prefix; never rename casually.
- **Every new page links ≥ 2 existing pages.** If too few targets exist, link the relevant
  `index.md` and note the gap.
- **One structural edit → one line in `log.md`.**
- **Do not expand the controlled vocabulary** (`SCHEMA.md` §3) without explicit approval; log it.
- **Annual review:** bump `version`/`review_year`/`last_reviewed`; tag `review-YYYY`.
- **Run `/lint` before committing.** **All agent writes go through a PR — never write `main`.**
- **Never guess** (`SCHEMA.md` §5). **Never delete human review notes** (§3).
