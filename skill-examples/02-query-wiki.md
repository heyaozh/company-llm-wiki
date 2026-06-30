name: query-wiki
category: data processing
description: Answer strictly from internal + knowledge (external only as cited reference), reading page bodies directly via the Confluence MCP. Reply "Not documented." when unsourced. Never fabricate.

---

# Query Wiki (Q&A over the CCPRM knowledge base, Confluence backend)

Answer using ONLY sourced wiki content. Working language: **English**.

Read path = **direct Confluence MCP reads** (NOT the Knowledge-base RAG). RAG chunks are lossy;
for a risk wiki the "don't guess" rule requires reading the actual page body + properties before
answering. Use RAG/CQL search only to *locate* candidate pages, then read them in full.

## Scope (hard rule, CLAUDE §1)
- GOLDEN SOURCE: `surface:internal` (policy/framework/concept/manual/BR/spec) +
  `surface:knowledge` (model/topic).
- EXTERNAL: `surface:external` (regulation/paper/article/other) may be cited as a reference, but
  its text is **never** treated as our own golden source.
- RAW: SharePoint / GCS PDFs only on explicit lookup.
- NEVER quote a human review note (inline comment, `> [!review]` callout) as fact.

## The "don't guess" rule (SCHEMA §5)
- State only what a `source_refs` entry supports.
- When the wiki has no sourced answer, reply exactly **"Not documented."** and surface the
  relevant `open_questions`. Never invent data schemas, results, or implementation details, and
  never fall back to model memory or external text as fact.

## Steps
1. LOCATE candidate pages: search Confluence (CQL by `label`/page property, or RAG to shortlist)
   restricted to `surface:internal` + `surface:knowledge`.
2. READ the candidates in full via the Confluence MCP — the actual page body AND properties
   (`status`, `completeness`, `source_refs`, `open_questions`). Do not answer from search
   snippets or RAG chunks alone.
3. ANSWER grounded only in sourced content; cite the page by `id` / title + Confluence link.
   Note `status` (draft/review vs stable) and `completeness` if it qualifies the answer.
4. If unsourced, or only external material supports it → reply **"Not documented."** plus the
   relevant `open_questions`. Optionally point to the external page as a *reference*, clearly
   marked as not our golden source.
