name: reindex-wiki
category: data processing
description: Rebuild index.md and the per-folder index.md files from front matter. Open a PR; never write main.

---

# Reindex Wiki

Rebuild the indices from document front matter.

## Steps
1. Scan all documents' front matter (id, type, title, status, parent, model, review_year).
2. Regenerate root `index.md` and each per-folder `index.md` (grouped by surface → type).
3. Append `YYYY-MM-DD — reindex` to `log.md`.
4. OPEN A PULL REQUEST with the changes. Never write `main`.
5. (Optional) Refresh the Memory cache tags from the rebuilt front matter; git stays
   authoritative — drop Memory entries with no backing document.
