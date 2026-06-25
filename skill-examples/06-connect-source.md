name: connect-source
category: api integration
description: (Optional) Locate a source in SharePoint / GCS and return its reference for ingest. Never copies raw files into the repo.

---

# Connect Source (locate raw source for ingest)

Resolve where a raw source lives so `ingest-source` can read it. This repo never stores raw
files — they stay in SharePoint / GCS.

## Steps
1. Resolve the source: SharePoint MCP path, GCS object, Knowledge base file id, or URL.
2. Confirm it is readable as a full document (not just RAG chunks).
3. Return a stable reference string suitable for `source_refs` (path / object id / URL) and
   hand off to `ingest-source`.

Do not distill or write any wiki document here — this skill only locates the source.
