# SCHEMA — Document Contract

This file is the **strict contract** for every document in this wiki. It is enforced by
[`tools/validate_wiki.py`](tools/validate_wiki.py) in CI. Follow it verbatim.

Working language is **English** for all content, field values, and identifiers.

---

## 1. File layout

One document = one Markdown file with a YAML front-matter block.

| Type | Folder | Filename / `id` prefix |
|------|--------|------------------------|
| `methodology` | `methodology/` | `meth-<slug>.md` |
| `business_requirement` | `business-requirements/` | `br-<slug>.md` |
| `specification` | `specifications/` | `spec-<slug>.md` |
| `concept` | `concepts/` | `concept-<slug>.md` |
| `model` (overview page) | `models/` | `model-<slug>.md` |

Rules:

- **`id` = filename without extension.** Stable; never rename casually (it breaks links).
- `slug` is lower-kebab-case, ASCII only.
- `index.md` (folder map) and files starting with `_` (e.g. `_TEMPLATE.md`) are **not**
  documents and are skipped by the validator.
- Figures go in `assets/<id>/<id>-figN-<slug>.png` and are embedded by relative path.

---

## 2. Front matter

### 2.1 Common fields (every document)

```yaml
---
id: meth-example                 # must equal the filename stem
type: methodology                # methodology | business_requirement | specification | concept | model
title: "Human-readable title"
model: model-example             # the model this doc belongs to (must exist in models/)
status: draft                    # draft | review | stable | deprecated
owner: firstname.lastname        # accountable person
version: 1                       # integer, bumped on material change
review_year: 2026                # the year this content reflects
last_reviewed: 2026-06-24        # ISO-8601 date of last review
completeness: theory_only        # complete | partial | theory_only
open_questions: []               # list of known gaps / unknowns (see §4)
source_refs: []                  # provenance: file paths, URLs, ticket IDs
tags: []                         # free-form facets for filtering
---
```

`model:` is omitted on `type: model` pages (a model page *is* the model) and on
`type: concept` pages (a concept is model-agnostic and shared across models).

### 2.2 Traceability fields (the reference graph)

Add the field(s) matching the document type. Every referenced `id` must exist.

| Type | Required link field | Points to | Meaning |
|------|--------------------|-----------|---------|
| `methodology` | — (root of the chain) | — | Theory. Use `references` for related methodology and the `concept` notes it distills into. |
| `concept` | — (shared vocabulary) | — | Atomic primitive. Use `references` to link related concepts / methodology. Model-agnostic. |
| `business_requirement` | `derives_from: [meth-...]` | one or more `methodology` | The theory this requirement is based on. |
| `specification` | `implements: [br-...]` | one or more `business_requirement` | The requirement this design realises. |

Any document may also carry:

- `references: [<id>, ...]` — non-hierarchical "see also" links to any document.

Downstream links (`implemented_by`, etc.) are **derived** by tooling, not hand-maintained.

---

## 3. Controlled vocabulary

Do not invent values for these fields.

- **`type`**: `methodology` · `business_requirement` · `specification` · `concept` · `model`
- **`status`**: `draft` · `review` · `stable` · `deprecated`
- **`completeness`**: `complete` · `partial` · `theory_only`

`tags` are free-form but reuse existing tags before inventing new ones.

---

## 4. The "don't guess" rule (hard constraint)

We hold the theory but usually **not** the full downstream picture. Therefore:

- State only what a `source_refs` entry supports. If you cannot cite it, it does not go in
  the body as fact.
- Record every unknown in **`open_questions`** and reflect it in **`completeness`**:
  - `theory_only` — only the methodology/theory is documented; IT/data details unknown.
  - `partial` — some downstream detail known, gaps remain (list them).
  - `complete` — fully documented and reviewed; `open_questions` should be empty.
- Prefer an explicit `open_questions: ["Data schema for X not documented"]` over a guessed
  schema. Empty prose is better than invented prose.

An agent answering over this wiki must reply **"not documented"** when the wiki has no
sourced answer, and should surface the relevant `open_questions`.

---

## 5. Page structure (body)

### 5.1 `methodology`
1. **Summary** — one paragraph: what the model is and what problem it solves.
2. **Theory & mathematical model** — definitions, assumptions, key equations (LaTeX).
3. **Inputs & data** — what data the model consumes; schema *only if documented*, else an
   `open_questions` entry.
4. **Outputs & usage** — what it produces and how it is used in risk management.
5. **Assumptions & limitations** — conditions under which it holds / fails.
6. **References** — `[text](relative/path.md)` links to related documents.

### 5.2 `business_requirement`
1. **Requirement** — what IT must provide, derived from the methodology.
2. **Rationale** — why, linked to `derives_from`.
3. **Scope & acceptance** — what "done" means.
4. **Open questions** — mirror of front-matter gaps.

### 5.3 `specification`
1. **Design** — how the requirement is implemented (components, data flow).
2. **Data & interfaces** — tables, jobs, APIs *as documented*.
3. **Validation** — how correctness is checked.
4. **Open questions**.

### 5.4 `model` (overview page)
1. **Overview** — what the model is, one paragraph.
2. **Traceability** — links to its methodology / requirements / specifications.
3. **Status & review** — current `status`, last review.

### 5.5 `concept`
1. **Definition** — precise, atomic definition (LaTeX where it helps).
2. **Why it matters** — how the concept is used across models / risk management.
3. **Used by** — links to the methodology / specifications that rely on it.
4. **Related concepts** — links to neighbouring concepts.

One atomic idea per file; model-agnostic. See `CLAUDE.md` §5 for the distillation rule.

---

## 6. Cross-links

Link between documents with **relative Markdown links**, e.g.
`[Initial Margin methodology](../methodology/meth-initial-margin.md)`.
These render on GitHub and are portable (no Obsidian-style `[[...]]`).

---

## 7. Versioning & annual review

- Bump `version` on material change; update `last_reviewed` and `review_year`.
- Each annual review is committed and tagged `review-YYYY` (see `CONTRIBUTING.md`), so the
  diff between two years is `git diff review-2026 review-2027`.

---

## 8. Lint rules (enforced by CI)

The validator fails the build on:

1. Missing required front-matter field, or `id` ≠ filename.
2. Value outside the controlled vocabulary (§3).
3. A traceability/`references`/`model` link to a non-existent `id` (dangling reference).
4. A `specification` with no `implements`, or a `business_requirement` with no
   `derives_from` (broken chain).

It **warns** (does not fail) on:

- `completeness` ≠ `complete` with empty `open_questions`.
- `review_year` older than the current year (stale — needs review).

Every structural change appends one line to [`log.md`](log.md): `YYYY-MM-DD — <change>`.
