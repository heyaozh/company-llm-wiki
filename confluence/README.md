# Confluence deployment assets — CCPRM Model & Analytics Wiki

Everything needed to stand up the wiki on **Confluence + Aether**, in one place to copy from.
The wiki lives in **one Confluence space** with three top-level parent pages (`internal`,
`external`, `knowledge`) plus a **Wiki Contract** parent (SCHEMA + AGENT), an **Index** page, and
a **Change Log** page. Agents act via the Confluence + SharePoint MCPs under the **restricted**
security profile.

## What to copy where

| File | Copy into |
|------|-----------|
| [`SCHEMA.md`](SCHEMA.md) | **Wiki Contract → SCHEMA** page (the structural contract) |
| [`AGENT.md`](AGENT.md) | **Wiki Contract → AGENT** page (the operating manual) |
| [`INDEX.md`](INDEX.md) | the **Index** page (prefer a Page Properties Report macro; see the file) |
| [`LOG.md`](LOG.md) | the **Change Log** page (space-wide ledger of structural changes) |
| [`agent-custom-instructions.md`](agent-custom-instructions.md) | the agent's **custom instructions** field in Aether |
| [`skills/`](skills/) | one Aether **skill** per file (name / category / description + body) |

## Skills

| File | name | category |
|------|------|----------|
| [`skills/01-ingest-source.md`](skills/01-ingest-source.md) | `ingest-source` | data processing |
| [`skills/02-query-wiki.md`](skills/02-query-wiki.md) | `query-wiki` | data processing |
| [`skills/03-lint-wiki.md`](skills/03-lint-wiki.md) | `lint-wiki` | logging |
| [`skills/04-reindex-wiki.md`](skills/04-reindex-wiki.md) | `reindex-wiki` | data processing |
| [`skills/05-mindmap.md`](skills/05-mindmap.md) *(optional)* | `mindmap` | other |
| [`skills/06-connect-source.md`](skills/06-connect-source.md) *(optional)* | `connect-source` | api integration |

## Hard rules assumed by everything here

- **Working language: English.** Security profile: **restricted**, never `privileged`.
- **Read the Wiki Contract first.** Every skill and the custom instructions begin by reading the
  **SCHEMA** and **AGENT** pages via the Confluence MCP, then follow them verbatim.
- **No PR/CI.** Every write publishes as a **new Confluence version under review**
  (`status: review` + `needs-review`, notify owner) — never silently overwriting a `stable` page;
  a human flips to `stable`. The agent runs the `lint-wiki` checks itself before publishing.
- **Versioning = native Confluence version history** (each publish = a version, diffable). On
  re-ingest add a "Changes in this version" section; apply a `review-YYYY` label at annual review.
- **Read path for Q&A = direct Confluence MCP reads** (page body + properties), not RAG chunks.
- **Metadata mapping:** structured fields → page **properties**; `type`/`status`/`surface`/`tags`
  + `id` + `review-YYYY` → **labels**; hierarchy (`parent`, surface) → **page tree**;
  `references`/`model`/topic links → **Confluence page links** (SCHEMA §2.3).
- **Never guess** (SCHEMA §5): unsourced → `open_questions`, answer **"Not documented."**
- **Never delete/reword human review notes** (inline comments / `> [!review]` callouts).
- Raw source files stay in **SharePoint / GCS**, never pasted into Confluence — only the
  `source_refs` pointer.

> Markdown here is the **authoring** format only. Confluence stores ADF/XHTML and the round-trip
> is lossy — don't expect to read Markdown back out of Confluence unchanged.
