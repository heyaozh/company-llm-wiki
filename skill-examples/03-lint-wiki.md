name: lint-wiki
category: logging
description: Run tools/validate_wiki.py plus stale-review / completeness / orphan-topic checks. Report only; never auto-delete.

---

# Lint Wiki (report only)

Validate the repo against `SCHEMA.md`. REPORT only — never auto-delete or auto-fix silently.

## Steps
1. Run `python tools/validate_wiki.py` and report all failures, which include:
   - missing required field; `id` ≠ filename or wrong prefix/folder;
   - value outside the controlled vocabulary (SCHEMA §3);
   - `concept` without `concept_kind`; `specification` without `implements`;
     `business_requirement` without `derives_from`;
   - any dangling reference (`model`/`parent`/`derives_from`/`implements`/`references`).
2. Additional warnings (CLAUDE §2):
   - non-`complete` `completeness` with empty `open_questions`;
   - stale `review_year` (overdue annual review);
   - orphan `topic` pages (no inbound links).
3. Do NOT count `[!review]` content toward the link rule.

## Output
A grouped report (one section per check) with document ids and the specific violation.
Do not modify files.
