# CCPRM Model & Analytics — Knowledge Wiki

An LLM-friendly, version-controlled knowledge base for the **Model & Analytics** team
within **CCPRM (Central Clearing Counterparty Risk Management)**.

The goal is to **track our documentation as a living library**: what models we have, the
theory behind them, how they are turned into IT requirements and designs, what data they
use, and how all of this changes year over year.

This repository is **plain Markdown + YAML front matter under Git**. No proprietary tool is
required to read or write it — it renders on GitHub, parses trivially in Python, and can be
served to agents (Databricks Genie / RAG) without any SDK. See [`SCHEMA.md`](SCHEMA.md) for
the exact contract every document must follow.

> **Working language is English.** All documents, fields, and commit messages are in English.

---

## What lives here

We track three document types that form a **traceability chain**:

```
methodology  ──derives_from──▶  business_requirement  ──implements──▶  specification
(theory & maths)                (model-based asks on IT)               (IT design)
```

| Type | Folder | Purpose |
|------|--------|---------|
| `methodology` | [`methodology/`](methodology/) | The theory and mathematical models. **We start here.** |
| `business_requirement` | [`business-requirements/`](business-requirements/) | Requirements on IT derived from a methodology. |
| `specification` | [`specifications/`](specifications/) | The IT design that implements a business requirement. |
| `concept` | [`concepts/`](concepts/) | Atomic, model-agnostic primitives **distilled** from methodology docs (shared vocabulary). |

A **model** (e.g. an initial-margin model) is the spine that links one chain together. Each
model has an overview page under [`models/`](models/) that aggregates its methodology →
requirements → specifications. **Concepts** are the reusable building blocks the methodology
documents are distilled into — one idea per note, shared across models.

The agent that maintains this repo follows [`CLAUDE.md`](CLAUDE.md) (operating manual:
query scope, the `/ingest` · `/lint` · `/reindex` workflows, the "don't guess" rule, and the
human-review-note protocol). [`SCHEMA.md`](SCHEMA.md) is the structural contract beneath it.

```
company-llm-wiki/
├── CLAUDE.md                 # agent operating manual (workflows + guardrails)
├── SCHEMA.md                 # the contract (front matter, vocab, rules)
├── CONTRIBUTING.md           # how to add / update a document + annual review
├── index.md                  # map of content (registered models & documents)
├── log.md                    # one line per structural change
├── methodology/              # ← we begin populating here
│   ├── index.md
│   └── _TEMPLATE.md
├── concepts/                 # atomic primitives distilled from methodology
├── business-requirements/    # scaffolded, populated later
├── specifications/           # scaffolded, populated later
├── models/                   # one overview page per model
├── assets/                   # figures, diagrams (referenced from docs)
├── tools/
│   └── validate_wiki.py      # front-matter + reference-integrity checker (runs in CI)
├── mcp_server/               # MCP capability layer (tools over the repo)
├── agent/                    # Google ADK agent (reasoning layer)
└── docs/
    └── architecture.md       # agent & MCP design: diagram, roles, deployment
```

## Agent & MCP layer

An LLM agent sits on top of this wiki via the **Model Context Protocol (MCP)** for tools and
**Google ADK** for reasoning. The MCP server ([`mcp_server/`](mcp_server/)) exposes the repo
as tools (search, traceability, gaps, validate, PR-only writes); the ADK agent
([`agent/`](agent/)) runs a read-only Q&A agent plus a maintainer that writes through PRs.
Full design — architecture diagram, agent roles, the "don't guess" gates, and deployment to
Cloud Run / Vertex AI Agent Engine — is in [`docs/architecture.md`](docs/architecture.md).

## Core principles

1. **Don't guess.** We have the theory documents but *not* all downstream information. State
   only what is sourced. Mark everything unknown explicitly via `completeness` and
   `open_questions` — never fabricate data fields, results, or implementation details.
2. **Traceability.** Every requirement points back to a methodology; every specification
   points back to a requirement. Links are validated in CI.
3. **Annual review.** Documents carry `review_year` / `last_reviewed`. Each yearly review is
   tagged `review-YYYY` so changes between years are a simple `git diff`.

## How to use it

- **Read:** browse the folders on GitHub, or open the per-model pages under `models/`.
- **Add a document:** copy the matching `_TEMPLATE.md`, fill the front matter, open a PR. CI
  runs [`tools/validate_wiki.py`](tools/validate_wiki.py) to check the schema and references.
- **Serve to Databricks:** a downstream job parses these files into Delta tables for Genie /
  search; the format requires no SDK. (Out of scope for this repo — this repo is the source
  of truth.)

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full workflow.
