name: connect-source
category: api integration
description: (Optional) Locate a source in SharePoint / GCS and return its reference for ingest. Never copies raw files into Confluence.

---

# Connect Source (locate raw source for ingest)

**FIRST, read the Wiki Contract.** Read the **SCHEMA** and **AGENT** pages via the **Confluence
MCP**. Working language: **English**.

Resolve where a raw source lives so `ingest-source` can read it. Raw files stay in
SharePoint / GCS — never copied into Confluence (only the `source_refs` pointer is).

## Steps
1. Resolve the source: SharePoint MCP path, GCS object, Knowledge-base file id, or URL.
2. Confirm it is readable as a full document (not just RAG chunks) — ingest needs the complete file.
3. Return a stable reference string suitable for the `source_refs` property (path / object id /
   URL) and hand off to `ingest-source`.

Do not distill or publish any wiki page here — this skill only locates the source. Security
profile: **restricted**; never `privileged`.
