name: lint-wiki
category: logging
description: Validate Confluence pages against SCHEMA agent-side (no CI). Run pre-publish on the page being ingested, or on demand across the space. Report only; never auto-delete.

---

# Lint Wiki (agent-side validation, Confluence backend)

Validate against `SCHEMA.md`. There is **no PR/CI gate** on Confluence — this skill IS the gate.
Run it (a) pre-publish inside `ingest-source` step 6 on the page about to be published, and
(b) on demand across the whole space as an audit. REPORT only — never auto-delete or auto-fix
silently. This ports the checks formerly in `tools/validate_wiki.py`.

## Failures (must be fixed before publishing)
Read each page's properties + labels + body via the Confluence MCP and check:
- missing required property (SCHEMA §2.1 common fields + the type-specific required field);
- `id` prefix does not match `type`, or `id` not in the right surface/page-tree position;
- value outside the controlled vocabulary (SCHEMA §3: `type`, `status`, `completeness`,
  `concept_kind`);
- `concept` without `concept_kind`; `specification` without `implements`;
  `business_requirement` without `derives_from`;
- any dangling reference — every id in `model`/`parent`/`derives_from`/`implements`/`references`
  must resolve to an existing page in the space.

## Warnings (CLAUDE §2)
- non-`complete` `completeness` with empty `open_questions`;
- stale `review_year` (overdue annual review);
- orphan `topic` pages (no inbound Confluence links);
- pages left at `status: review` with a `needs-review` label past their review window.

## Rules
- Do NOT count human review-note content (inline comments / `> [!review]` callouts) toward the
  ≥2-link rule, and never modify or remove them.
- Report only: a grouped list (one section per check) with page `id` + Confluence link + the
  specific violation. Do not edit pages. When run pre-publish, return pass/fail so `ingest-source`
  can block on failures.
