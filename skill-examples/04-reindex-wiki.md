name: reindex-wiki
category: data processing
description: Rebuild the Confluence index page(s) from page properties + labels. Publish as a new version under review; never overwrite a stable index silently.

---

# Reindex Wiki (Confluence backend)

Rebuild the index from page properties — the Confluence equivalent of the old `index.md`.
Confluence's native **page tree** is already a live index; this skill produces the *flat,
grouped, queryable* views the tree alone doesn't give.

## Steps
1. SCAN all pages in the space via the Confluence MCP, reading properties
   (`id`, `type`, `title`, `status`, `parent`, `model`, `review_year`, `completeness`) + labels.
2. REGENERATE the index page(s), grouped by `surface` → `type`:
   - Prefer a **Page Properties Report** macro keyed on the `surface:*` / `type:*` labels so the
     index stays live without re-running this skill; fall back to a generated table if the macro
     is unavailable.
   - One index page per top-level surface (`internal` / `external` / `knowledge`), or a single
     index page with a section per surface.
3. PUBLISH as a new version of the index page (review gate applies — do not silently overwrite a
   stable index; flag `needs-review` if the structure changed materially).
4. LOG one row on the **Change log** page (`YYYY-MM-DD · reindex`).

Do not invent pages or properties; the index reflects only what exists. Never use `privileged`.
