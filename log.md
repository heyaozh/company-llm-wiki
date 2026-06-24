# Change log

One line per structural change: `YYYY-MM-DD — <short description>`.
This is a human-curated complement to `git log` (which holds the full history).

2026-06-24 — Initialised CCPRM Model & Analytics knowledge wiki: schema, contributing guide, index, log, folder scaffold (methodology / business-requirements / specifications / models), templates, and CI validator. Methodology is the starting surface.
2026-06-24 — Added CLAUDE.md (agent operating manual: query scope, /ingest·/lint·/reindex workflows, don't-guess rule, human-review-note protocol) and a `concept` surface (concepts/ + template + index) for distilling methodology docs into atomic, model-agnostic primitives. Registered `concept` type in SCHEMA.md (§1/§2/§3/§5.5) and validate_wiki.py (exempt from the model-link requirement, like model pages).
2026-06-24 — Added first real documents (placeholder, to be re-ingested from source): model-black76 (model overview) + meth-black76-option-pricing (standard Black-76 theory, completeness theory_only, company specifics in open_questions). Listed both in models/index.md and methodology/index.md. owner dl625.
2026-06-24 — Added agent & MCP layer: mcp_server/ (FastMCP capability layer over the repo — list_documents/get_document/get_traceability/find_gaps/find_stale/references/search_wiki/validate read tools + propose_document PR-only write, wiki://schema & wiki://manual resources, wiki_repo.py, Dockerfile), agent/ (Google ADK skeleton — WikiRoot coordinator over WikiQA read-only + WikiMaintainer PR-only), and docs/architecture.md (architecture diagram, agent roles, don't-guess gates, Cloud Run / Vertex AI Agent Engine deployment).
