# SCHEMA — Document Contract

The strict contract for every page in this wiki. The wiki lives in **internal Confluence**
(one space), maintained by Aether agents via the **Confluence MCP**. There is no CI: the
contract is enforced **agent-side** by the `lint-wiki` skill before every publish. Working
language is **English**.

> Metadata note: Confluence stores pages as ADF/XHTML, so Markdown is only an *authoring*
> convenience and the round-trip is lossy. The "front matter" fields below do not live as YAML;
> they are mapped onto **page properties + labels** (see §2.3).

The wiki has three surfaces, each a **top-level parent page** in the single space:

- **`internal`** — a mirror of our company documents (the 4-level hierarchy + BR/spec).
- **`external`** — external sources we track (regulation, papers, articles, …).
- **`knowledge`** — our **distilled** layer: model overviews and atomic topics. (This is the
  renamed former "concept" layer — renamed to avoid clashing with the internal *concept* level.)

---

## 1. Page layout — types, page tree, id prefixes

| Surface | `type` | Lives under (page tree) | `id` prefix |
|---------|--------|-------------------------|-------------|
| internal | `policy` | `internal` → Policy | `pol-` |
| internal | `framework` | `internal` → Framework | `fwk-` |
| internal | `concept` | `internal` → Concept | `con-` |
| internal | `manual` | `internal` → Manual | `man-` |
| internal | `business_requirement` | `internal` → Business Requirements | `br-` |
| internal | `specification` | `internal` → Specifications | `spec-` |
| external | `regulation` | `external` → Regulation | `reg-` |
| external | `paper` | `external` → Paper | `paper-` |
| external | `article` | `external` → Article | `art-` |
| external | `other` | `external` → Other | `other-` |
| knowledge | `model` | `knowledge` → Model | `model-` |
| knowledge | `topic` | `knowledge` → Topic | `topic-` |

Rules:

- **`id` is the stable key**, and must start with the type's prefix. It lives in the `id` page
  property **and** an `id:<id>` label so it survives page renames. The page **title** may be the
  human title. Never change an `id` casually.
- Index pages, the **Wiki Contract** pages (this SCHEMA + AGENT), and the **Change log** page
  are metadata, not documents.
- Figures are attached to the page, or stored in SharePoint/GCS and linked — never large binaries
  pasted inline.

### 1.1 The internal hierarchy

```
policy  ──▶  framework  ──▶  concept  ──▶  manual
(highest)                  (methodology |
                            pricing | risk)
```

The tree is expressed by the **`parent`** property (a page names its parent's id) **and** by the
actual Confluence page-tree parentage. Documents also reference each other freely via
`references` (Confluence page links). `business_requirement` and `specification` sit in parallel
under `internal` and are linked by `derives_from` / `implements`.

---

## 2. Metadata (formerly "front matter")

### 2.1 Common fields (every document)

| Field | Example | Notes |
|-------|---------|-------|
| `id` | `con-example` | stable key; prefix per §1; also an `id:` label |
| `type` | `concept` | see §1 / §3 |
| `title` | `"Human-readable title"` | may equal the page title |
| `status` | `draft` | `draft` \| `review` \| `stable` \| `deprecated` |
| `owner` | `firstname.lastname` | notified on publish-under-review |
| `version` | `1` | mirrors the Confluence page version; bump on material change |
| `review_year` | `2026` | annual review |
| `last_reviewed` | `2026-06-24` | |
| `completeness` | `theory_only` | `complete` \| `partial` \| `theory_only` |
| `open_questions` | (list) | known gaps / unknowns (§5) |
| `source_refs` | (list) | provenance: SharePoint/GCS paths, URLs, citations — pointers only |
| `references` | (list) | "see also" links to any document id |
| `tags` | (list) | free-form labels |

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

Every id named in `model`, `parent`, `derives_from`, `implements`, `references` **must resolve to
an existing page** (checked by `lint-wiki` before publish).

### 2.3 How metadata maps onto Confluence

- **Page properties** (rendered in a Page Properties macro, queryable via Page Properties
  Report): `id`, `type`, `status`, `owner`, `version`, `review_year`, `last_reviewed`,
  `completeness`, `concept_kind`, `model`, `derives_from`, `implements`, `source_refs`.
- **Labels**: `type:<t>`, `status:<s>`, `surface:internal|external|knowledge`, `id:<id>`, the
  free-form `tags`, `review-YYYY` (annual snapshot), and `needs-review` while under review.
- **Page tree**: `parent` and the surface grouping.
- **In-body Confluence page links**: `references`, `model`, and topic cross-links.

---

## 3. Controlled vocabulary

- **`type`**: the 12 values in §1.
- **`status`**: `draft` · `review` · `stable` · `deprecated`
- **`completeness`**: `complete` · `partial` · `theory_only`
- **`concept_kind`**: `methodology` · `pricing` · `risk`

Do not extend these without explicit approval (record any change on the **Change log** page).
`tags` are free-form — reuse before inventing.

---

## 4. internal vs external vs knowledge

- **internal** documents are our own, mirrored and tracked. They are the golden source for our
  models. They carry the hierarchy (`parent`) and traceability (`derives_from`/`implements`).
- **external** documents (regulation/paper/article/other) are records of outside material we
  reference. We summarise and link them; we never treat their text as our own golden source.
- **knowledge** documents are **distilled by us**:
  - `model` — an overview page that is the spine of one model's documents.
  - `topic` — an atomic, model-agnostic primitive extracted across documents (the renamed
    former "concept"). One idea per page; merge, never duplicate.

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

Cross-link with **Confluence page links** (relative Markdown paths do not resolve in Confluence).
On a re-published (updated) page, put a **"Changes in this version"** section at the top (§7).

---

## 7. Versioning & annual review

Each **publish is a new Confluence page version** — this is the native version history and is
diffable page-to-page. Bump the `version` property on material change; update `last_reviewed` /
`review_year`. For the annual review, apply a `review-YYYY` label to the reviewed version.

On any update, add a **"Changes in this version"** section summarising what changed vs. the prior
version and why. This section is authoritative as the diff record if the Confluence MCP cannot
produce a native version diff; if it can, reference/attach that diff too. (There is no
`git diff` — Confluence version history replaces it.)

---

## 8. Validation rules (agent-side, via `lint-wiki`)

There is **no CI**. The `lint-wiki` skill runs these checks (a) pre-publish inside
`ingest-source`, and (b) as an on-demand audit across the space.

**Fails on:** missing required property; `id` prefix ≠ `type`, or wrong surface/page-tree
position; value outside the controlled vocabulary; `concept` without `concept_kind`;
`specification` without `implements`; `business_requirement` without `derives_from`; any dangling
reference (`model`/`parent`/`derives_from`/`implements`/`references`).

**Warns on:** non-`complete` `completeness` with empty `open_questions`; stale `review_year`;
orphan `topic` pages (no inbound links); pages stuck at `status: review` / `needs-review`.

**Publish gate (replaces PR/CI):** an agent publishes a new version with `status: review` +
`needs-review` and notifies the `owner`; it never silently overwrites a `stable` page and never
sets `status: stable` itself — a human does. Every structural change appends one row to the
**Change log** page.
