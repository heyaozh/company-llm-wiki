# SCHEMA — Document Contract

The strict contract for every document in this wiki. Enforced by
[`tools/validate_wiki.py`](tools/validate_wiki.py) in CI. Working language is **English**.

The wiki has three surfaces:

- **`internal/`** — a mirror of our company documents (the 4-level hierarchy + BR/spec).
- **`external/`** — external sources we track (regulation, papers, articles, …).
- **`knowledge/`** — our **distilled** layer: model overviews and atomic topics. (This is the
  renamed former "concept" layer — renamed to avoid clashing with the internal *concept* level.)

---

## 1. File layout — types, folders, id prefixes

| Surface | `type` | Folder | `id` prefix |
|---------|--------|--------|-------------|
| internal | `policy` | `internal/policy/` | `pol-` |
| internal | `framework` | `internal/framework/` | `fwk-` |
| internal | `concept` | `internal/concept/` | `con-` |
| internal | `manual` | `internal/manual/` | `man-` |
| internal | `business_requirement` | `internal/business-requirements/` | `br-` |
| internal | `specification` | `internal/specifications/` | `spec-` |
| external | `regulation` | `external/regulation/` | `reg-` |
| external | `paper` | `external/paper/` | `paper-` |
| external | `article` | `external/article/` | `art-` |
| external | `other` | `external/other/` | `other-` |
| knowledge | `model` | `knowledge/model/` | `model-` |
| knowledge | `topic` | `knowledge/topic/` | `topic-` |

Rules:

- **`id` = filename stem**, and must start with the type's prefix. Never rename casually.
- `index.md` and files starting with `_` (e.g. `_TEMPLATE.md`) are not documents.
- Figures go in `assets/<id>/<id>-figN-<slug>.png`.

### 1.1 The internal hierarchy

```
policy  ──▶  framework  ──▶  concept  ──▶  manual
(highest)                  (methodology |
                            pricing | risk)
```

The tree is expressed by the **`parent`** field (a doc names its parent's id). Documents also
reference each other freely via `references`. `business_requirement` and `specification` sit in
parallel under `internal/` and are linked by `derives_from` / `implements`.

---

## 2. Front matter

### 2.1 Common fields (every document)

```yaml
---
id: con-example                  # must equal the filename stem; prefix per §1
type: concept                    # see §1 / §3
title: "Human-readable title"
status: draft                    # draft | review | stable | deprecated
owner: firstname.lastname
version: 1
review_year: 2026
last_reviewed: 2026-06-24
completeness: theory_only        # complete | partial | theory_only
open_questions: []               # known gaps / unknowns (§5)
source_refs: []                  # provenance: file paths, URLs, citations
references: []                    # "see also" links to any document id
tags: []
---
```

### 2.2 Type-specific fields

| Type | Extra required | Extra optional |
|------|----------------|----------------|
| `policy` / `framework` / `manual` | — | `parent` |
| `concept` | `concept_kind` (`methodology`\|`pricing`\|`risk`) | `parent`, `model` |
| `business_requirement` | `derives_from: [con-…]` | `model` |
| `specification` | `implements: [br-…]` | `model` |
| `regulation` / `paper` / `article` / `other` | — | `authors`, `year`, `url` |
| `model` | — | — |
| `topic` | — | — |

Every id named in `model`, `parent`, `derives_from`, `implements`, `references` **must exist**
(checked in CI).

---

## 3. Controlled vocabulary

- **`type`**: the 12 values in §1.
- **`status`**: `draft` · `review` · `stable` · `deprecated`
- **`completeness`**: `complete` · `partial` · `theory_only`
- **`concept_kind`**: `methodology` · `pricing` · `risk`

Do not extend these without explicit approval (record any change in `log.md`). `tags` are
free-form — reuse before inventing.

---

## 4. internal vs external vs knowledge

- **internal** documents are our own, mirrored and tracked. They are the golden source for our
  models. They carry the hierarchy (`parent`) and traceability (`derives_from`/`implements`).
- **external** documents (regulation/paper/article/other) are records of outside material we
  reference. We summarise and link them; we never treat their text as our own golden source.
- **knowledge** documents are **distilled by us**:
  - `model` — an overview page that is the spine of one model's documents.
  - `topic` — an atomic, model-agnostic primitive extracted across documents (the renamed
    former "concept"). One idea per file; merge, never duplicate.

---

## 5. The "don't guess" rule (hard constraint)

We hold the theory but usually not the full downstream picture.

- State only what a `source_refs` entry supports. If you cannot cite it, it does not go in the
  body as fact.
- Record every unknown in **`open_questions`** and set **`completeness`** honestly
  (`theory_only` / `partial` / `complete`).
- Prefer an explicit `open_questions` entry over a guessed schema, result, or implementation
  detail. An agent answering over this wiki replies **"Not documented."** when unsourced.

---

## 6. Page structure (body)

- **internal hierarchy (`policy`/`framework`/`concept`/`manual`)**: Summary · Content (theory
  for a `concept`) · Inputs & data (only if sourced) · Relationships (parent / model / topics).
- **`business_requirement`**: Requirement · Rationale · Scope & acceptance · Open questions.
- **`specification`**: Design · Data & interfaces · Validation · Open questions.
- **external (`regulation`/`paper`/`article`/`other`)**: Summary · Why it is relevant · Reference.
- **`model`**: Overview · Documents (traceability) · Distilled topics · Status & review.
- **`topic`**: Definition · Why it matters · Used by · Related topics.

Cross-link with **relative Markdown links**, e.g.
`[Black-76](../../knowledge/model/model-black76.md)` (portable; renders on GitHub).

---

## 7. Versioning & annual review

Bump `version` on material change; update `last_reviewed` / `review_year`. Tag each annual
review `review-YYYY` (see `CONTRIBUTING.md`); the year-on-year diff is
`git diff review-2026 review-2027`.

---

## 8. Lint rules (CI)

Fails on: missing required field; `id` ≠ filename or wrong prefix/folder; value outside the
controlled vocabulary; concept without `concept_kind`; specification without `implements`; BR
without `derives_from`; any dangling reference. Warns on: non-`complete` with empty
`open_questions`; stale `review_year`. Every structural change appends one line to `log.md`.
