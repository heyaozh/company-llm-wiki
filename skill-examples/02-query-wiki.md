name: query-wiki
category: data processing
description: Answer questions / RAG strictly from scope:wiki notes; never trust inbox or raw as fact.

---

# Query Wiki (RAG / Q&A)

Answer the user's question using ONLY curated wiki knowledge.

## Scope (hard rule)
- ALLOWED as fact: Memory entries tagged `scope:wiki` (mirror of the curated wiki),
  or the curated wiki tree in git.
- SUPPORTING (cite, don't treat as distilled fact): raw/external sources, only when asked
  to trace provenance.
- EXCLUDED: anything tagged `scope:inbox` / `scope:idea` (transient notes). Include them
  ONLY if the user explicitly says "search my ideas / inbox".
- NEVER quote a user annotation (`[^me-*]`, `[!me]`, `<!-- user-note -->`) as a fact.

## Steps
1. Retrieve from Memory filtered on `scope:wiki` (+ relevant `type:`/`topic:` tags).
2. Synthesize an answer grounded only in those notes. Cite note slugs.
3. If the wiki has no coverage, say so plainly — do NOT fall back to inbox or model memory.
4. Output Chinese-primary, English on technical terms.
