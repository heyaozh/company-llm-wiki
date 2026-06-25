name: query-wiki
category: data processing
description: Answer strictly from internal + knowledge (external only as cited reference). Reply "Not documented." when unsourced. Never fabricate.

---

# Query Wiki (Q&A over CCPRM knowledge base)

Answer using ONLY sourced wiki content. Working language: **English**.

## Scope (hard rule, CLAUDE §1)
- GOLDEN SOURCE: `internal/` (policy/framework/concept/manual/BR/spec) + `knowledge/`
  (model/topic).
- EXTERNAL: `external/` (regulation/paper/article/other) may be cited as a reference, but its
  text is **never** treated as our own golden source.
- RAW: SharePoint / GCS PDFs only on explicit lookup.
- NEVER quote a human review note (`> [!review]`, `<!-- review: … -->`) as fact.

## The "don't guess" rule (SCHEMA §5)
- State only what a `source_refs` entry supports.
- When the wiki has no sourced answer, reply exactly **"Not documented."** and surface the
  relevant `open_questions`. Never invent data schemas, results, or implementation details.

## Steps
1. Retrieve from internal + knowledge (Memory `surface:internal|knowledge`, or the repo).
2. Answer grounded only in sourced content; cite document ids / relative links.
3. If unsourced → "Not documented." + the relevant `open_questions`. Do not fall back to
   model memory or external text as fact.
