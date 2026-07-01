# AGENT (Confluence) — CCPRM Model & Analytics Wiki Operating Manual

This is the **LLM-maintained knowledge base** for the **Model & Analytics** team under **CCPRM
(Central Clearing Counterparty Risk Management)**. It mirrors our company documents, tracks
external sources, and distills both into atomic, interconnected knowledge.

The wiki backend is **internal Confluence** (one space), maintained by Aether agents via the
**Confluence MCP**. There is no GitHub repo, no PR, and no CI in the live system — the GitHub
repo `company-llm-wiki` is only a staging platform for authoring the contract, skills, and
instructions.

**Before doing anything, read [`SCHEMA.md`](SCHEMA.md)** — the structural
contract (types, page tree, page properties/labels, vocabulary, validation rules). *This* file is
the **operational layer**: what to read, what to touch, how the workflows run. Working language
is **English**. Security profile: **restricted** (never `privileged`).

> At runtime the agent reads this contract from the **Wiki Contract** pages in the Confluence
> space (SCHEMA + CLAUDE published there), not from any repo. The non-negotiable guardrails are
> also inlined into the agent's custom instructions so they never depend on retrieval.

---

## 1. Knowledge surfaces & query scope (hard rule)

| Surface | Location | Default behaviour |
|---------|----------|-------------------|
| **Internal** | `internal` parent page (policy, framework, concept, manual, business-requirements, specifications) | Our own documents — **the golden source** for our models. Default answer scope. |
| **External** | `external` parent page (regulation, paper, article, other) | Outside material we track. Summarise & link; **never** treat its text as our golden source. |
| **Knowledge** | `knowledge` parent page (model, topic) | Our **distilled** layer — model overviews + atomic topics. Default answer scope. |
| **Raw sources** | original files in SharePoint / GCS — **not in Confluence** | Read **only** during `/ingest` or explicit lookup; never pasted into Confluence. |
| **Metadata** | Wiki Contract pages (SCHEMA + CLAUDE), index page(s), Change log page | Structure & operations. |

**Read path for Q&A = direct Confluence MCP reads** (page body + properties). Use search/RAG only
to *locate* candidate pages, then read them in full — do not answer from chunks alone.

**Never fabricate.** Answer from internal + knowledge (and external as cited references). When
the wiki has no sourced answer, reply **"Not documented."** and surface the relevant
`open_questions` — never invent data schemas, results, or implementation details
(`SCHEMA.md` §5).

> Note on names: the internal hierarchy has a level literally called **concept**
> (methodology/pricing/risk). Our distilled atomic primitives are **`topic`** (under the
> `knowledge` surface), *not* `concept`. Keep the two distinct.

---

## 2. Recurring workflows

- **`/ingest <source>`** — Distill a source document into the right internal doc(s) **and** the
  knowledge layer (model + topics), then publish to Confluence. Pipeline in §4.
- **`/lint`** — Run the `lint-wiki` agent-side checks (schema validation, plus stale
  `review_year`, `completeness` vs `open_questions`, and orphan topics). Report only; never
  auto-delete.
- **`/reindex`** — Rebuild the Confluence index page(s) (Page Properties Report over the space)
  from page properties + labels.

---

## 3. Human review notes are sacred

Reviewers layer annotations on top of pages as Confluence **inline comments** or
`> [!review]`-style callout panels. These are **not** golden source: never distill, quote as
fact, delete, move, or reword them. Only the author removes them. If an edit removes the text a
note refers to, keep the note and mark the old text `~~struck~~`. Preserve them verbatim on
re-publish.

---

## 4. Ingest pipeline (source → internal + knowledge → Confluence)

1. **Read the source.** Given a path/link (SharePoint / GCS). Do not paste raw files into Confluence.
2. **Place the internal document.** Decide its level (`policy` / `framework` / `concept` /
   `manual`) and, for a `concept`, its `concept_kind` (methodology/pricing/risk). Set `parent`
   (property + page-tree position). If a page for this source exists, **update** it (keep `id`,
   bump `version`, refresh `last_reviewed`/`review_year`) — never duplicate. Find it by the
   `id:` label.
3. **Honesty.** Set `source_refs`; set `completeness` honestly; record every unknown in
   `open_questions`. **Do not guess** data, results, or IT details.
4. **Distill the knowledge layer.** Create/update the `model` overview page, and extract the
   atomic, model-agnostic **`topic`** pages it rests on (one topic per page; merge, never
   duplicate). Cross-link concept ↔ model ↔ topics with Confluence page links.
5. **Link.** Connect every new page to **≥ 2** existing pages.
6. **Validate.** Run the `lint-wiki` checks on the page; fix all failures before publishing.
7. **Publish & log.** Publish as a new Confluence version under review (`status: review` +
   `needs-review`, notify `owner`); on update add a "Changes in this version" section. Append one
   row to the **Change log** page; update the index page.

Everything in English. **All writes publish as a new version under review — never silently
overwrite a `stable` page; a human flips `status` to `stable`.**

---

## 5. Topic distillation rule

A **`topic`** is an **atomic, reusable, model-agnostic primitive** — the distilled layer
(formerly "concept", renamed to avoid clashing with the internal *concept* level). One topic =
one idea = one page; several models/concepts link to the same topic; merge overlaps into the
existing topic rather than duplicating. Topics carry the same honesty rules.

---

## 6. Conventions & guardrails

- **English** everywhere. **`id`** is the stable key with the correct prefix (property + `id:`
  label); never rename casually.
- **Every new page links ≥ 2 existing pages.** If too few targets exist, link the surface's
  top-level page and note the gap in `open_questions`.
- **One structural change → one row on the Change log page.**
- **Do not expand the controlled vocabulary** (`SCHEMA.md` §3) without explicit
  approval; log it.
- **Annual review:** bump `version`/`review_year`/`last_reviewed`; apply the `review-YYYY` label.
  The year-on-year comparison uses Confluence version history / the `review-YYYY` snapshots.
- **Run `/lint` before publishing.** **All agent writes publish as a new version under review —
  never silently overwrite a `stable` page, never self-promote to `stable`.**
- **Never guess** (`SCHEMA.md` §5). **Never delete human review notes** (§3).
- **Security profile is `restricted`** — never `privileged` (protects the "never delete review
  notes / never destroy history" rules).
