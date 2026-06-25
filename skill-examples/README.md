# Aether Skill Examples — LLM-Wiki

Copy-paste source for the LLM-Wiki skills in the Aether Orchestration Plane.

Each file holds the three GUI fields (**name / category / description**) followed by the
**markdown instruction** to paste into the skill body.

Architecture assumed by every skill:

- **Git MCP repo = source of truth.** The full wiki tree + `SCHEMA.md` live in git.
- **Memory = tagged cache** (a mirror of the curated wiki), used for fast retrieval.
- **Knowledge base / SharePoint MCP / uploaded PDFs = raw source intake.**
- Every skill loads `SCHEMA.md` and follows it verbatim.
- Git is written **before** Memory; Memory must always be reconstructable from git.

| File | name | category |
|------|------|----------|
| `01-ingest-source.md` | `ingest-source` | data processing |
| `02-query-wiki.md` | `query-wiki` | data processing |
| `03-lint-wiki.md` | `lint-wiki` | logging |
| `04-reindex-wiki.md` | `reindex-wiki` | data processing |
| `05-promote-note.md` | `promote-note` | data processing |
| `06-mindmap.md` | `mindmap` | other |
| `07-connect-source.md` *(optional)* | `connect-source` | api integration |
