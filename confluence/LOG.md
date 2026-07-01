# Change Log

One row per **structural change** to the wiki (page created, updated to a new version, moved,
deprecated, reindexed, or a vocabulary change). Append-only; newest at the top. This is metadata,
not a document — do not distill or answer questions from it.

Every write from the `ingest-source` / `reindex-wiki` skills adds a row here (AGENT §4, §6).
Native Confluence page-version history is the per-page detail; this page is the space-wide ledger.

Columns:
- **Date** — `YYYY-MM-DD`.
- **id** — the page `id` affected (or `—` for space-wide actions like reindex).
- **Action** — `create` · `update` · `move` · `deprecate` · `reindex` · `vocab-change`.
- **Version** — the new page `version` after this change (or `—`).
- **Note** — one line: what changed and why (for `update`, mirror the page's "Changes in this
  version" summary).

| Date | id | Action | Version | Note |
|------|----|--------|---------|------|
| 2026-07-01 | — | reindex | — | Seed the Change Log and Index pages. |
