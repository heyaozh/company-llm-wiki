# CCPRM Model & Analytics — Knowledge Wiki

An LLM-friendly, version-controlled knowledge base for the **Model & Analytics** team within
**CCPRM (Central Clearing Counterparty Risk Management)**.

It tracks our documentation as a living library: what models we have, the theory behind them,
how they map to IT requirements and designs, the external sources we rely on, and how all of
this changes year over year. Plain **Markdown + YAML front matter under Git** — no proprietary
tool needed; it renders on GitHub, parses in Python, and can be served to agents without an SDK.
See [`SCHEMA.md`](SCHEMA.md) for the contract and [`CLAUDE.md`](CLAUDE.md) for the agent manual.

> **Working language is English** for all documents, fields, and commit messages.

---

## Three surfaces

```
internal/     our own documents (golden source)
  policy/                 # pol-   top of the hierarchy
  framework/              # fwk-   under a policy
  concept/                # con-   under a framework; concept_kind: methodology | pricing | risk
  manual/                 # man-   under a concept; most operational
  business-requirements/  # br-    derived from a concept
  specifications/         # spec-  implements a business requirement
external/     outside material we track
  regulation/  # reg-     paper/  # paper-     article/  # art-     other/  # other-
knowledge/    our distilled layer (renamed from "concept" to avoid clashing with internal concept)
  model/                  # model-  overview page = the spine of one model's documents
  topic/                  # topic-  atomic, model-agnostic distilled primitive
```

The internal hierarchy `policy → framework → concept → manual` is expressed by a `parent` link;
documents also cross-reference via `references`. `business_requirement` → `derives_from` a
concept; `specification` → `implements` a business requirement.

```
company-llm-wiki/
├── CLAUDE.md                 # agent operating manual
├── SCHEMA.md                 # the contract (types, front matter, vocab, rules)
├── CONTRIBUTING.md           # how to add / update a document + annual review
├── index.md  ·  log.md       # map of content · change log
├── internal/ · external/ · knowledge/   # the three surfaces above
├── assets/                   # figures referenced from documents
├── tools/validate_wiki.py    # front-matter + reference-integrity checker (CI)
├── mcp_server/ · agent/      # MCP capability layer + Google ADK agent
└── docs/architecture.md      # agent & MCP design: diagram, roles, deployment
```

## Core principles

1. **Don't guess.** State only what is sourced; mark unknowns in `open_questions` and set
   `completeness` (`theory_only` / `partial` / `complete`). Never fabricate.
2. **Traceability.** Hierarchy via `parent`; requirements → concepts → models; links validated
   in CI.
3. **Annual review.** `review_year` / `last_reviewed` per doc; tag each review `review-YYYY` so
   year-on-year change is a `git diff`.

## How to use it

- **Read:** browse the folders, or start from a model page under `knowledge/model/`.
- **Add a document:** copy the matching `_TEMPLATE.md`, fill the front matter, open a PR. CI runs
  [`tools/validate_wiki.py`](tools/validate_wiki.py). See [`CONTRIBUTING.md`](CONTRIBUTING.md).
- **Agent / MCP:** see [`docs/architecture.md`](docs/architecture.md).
