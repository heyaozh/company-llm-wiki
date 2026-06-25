# Aether Skill Examples — CCPRM Model & Analytics Wiki

Copy-paste source for the wiki-maintenance skills in the Aether Orchestration Plane,
**tailored to this repo** (CCPRM Model & Analytics knowledge base). Read `SCHEMA.md` and
`CLAUDE.md` first — these skills only encode the workflow; those two files are the contract.

Each file holds the three GUI fields (**name / category / description**) followed by the
**markdown instruction** to paste into the skill body.

Architecture & hard rules assumed by every skill:

- **Working language is English.**
- **Git repo = source of truth.** internal/ + knowledge/ are the golden answer scope;
  external/ is cited, never treated as our own golden source.
- **All agent writes go through a Pull Request — never write `main`.** CI
  (`tools/validate_wiki.py`) gates it; a human merges.
- **Never guess** (SCHEMA §5). Unsourced → record in `open_questions`, set `completeness`
  honestly; an agent answering replies **"Not documented."**
- **Never delete/reword human review notes** (`> [!review]`, `<!-- review: … -->`); preserve
  verbatim, strike superseded body text instead.
- Raw source PDFs live in **SharePoint / GCS**, never copied into the repo.
- Memory (if used) is a tagged cache mirror; it is always reconstructable from git.

| File | name | category |
|------|------|----------|
| `01-ingest-source.md` | `ingest-source` | data processing |
| `02-query-wiki.md` | `query-wiki` | data processing |
| `03-lint-wiki.md` | `lint-wiki` | logging |
| `04-reindex-wiki.md` | `reindex-wiki` | data processing |
| `05-mindmap.md` *(optional)* | `mindmap` | other |
| `06-connect-source.md` *(optional)* | `connect-source` | api integration |
