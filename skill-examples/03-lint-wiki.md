name: lint-wiki
category: logging
description: Report-only QA pass — orphans, stale strategies, invalid enums, Other w/o data_note, orphaned user notes.

---

# Lint Wiki (report only)

Run the SCHEMA lint checks over the curated wiki tree (git). REPORT only — never auto-delete.

## Checks
- Orphan pages: no inbound `[[...]]` links from other notes.
- Stale strategies/signals: `updated` older than 6 months → "needs review".
- Invalid enums: `data_used`/`data_required`/`data_category` not in the SCHEMA vocabulary;
  `asset_class` not in the allowed list.
- `Other` without `data_note`: any data list contains `Other` but `data_note` empty.
- Orphaned user notes: a `[^me-*]` definition with no matching reference in the body.

## Output
A grouped report (one section per check) with file slugs and the specific violation.
Do NOT count `[!me]`/`[^me-*]` content toward the link rule. Do not modify files.
