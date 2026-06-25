name: reindex-wiki
category: data processing
description: Rebuild the index map-of-content from every note's front matter; resync Memory tags.

---

# Reindex Wiki

Rebuild the index as a map-of-content from every wiki note's front matter, then resync Memory.

## Steps
1. Scan the curated wiki front matter (title, slug, type, domain, tags, updated).
2. Regenerate `index.md` grouped by type → domain. Commit via Git MCP.
3. Resync Memory: for each wiki note, upsert body + refresh tags from front matter.
   Git is authoritative — if Memory and git disagree, git wins; drop Memory entries
   that no longer have a git note.
4. Append `YYYY-MM-DD — reindex` to `log.md`.
