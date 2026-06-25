name: connect-source
category: api integration
description: (Optional) Pull a source from SharePoint MCP / Knowledge base / URL into the raw/ layer before ingest.

---

# Connect Source → Raw Layer

Fetch an external source into the raw/external layer before ingest. Use when the source
lives in SharePoint or the Knowledge base and you want capture decoupled from distillation.

## Steps
1. Resolve the source: SharePoint MCP path, Knowledge base file id, or URL.
2. PDFs/papers → keep binary in Knowledge base/Zotero (never git). Record the citekey.
3. Blog/HTML/docx → convert to markdown, save under the right `external/<bucket>/`.
4. Commit the raw markdown + return the raw path so `ingest-source` can pick it up.

Do not distill here — this skill only lands the raw asset.
