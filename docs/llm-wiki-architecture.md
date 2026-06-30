# LLM-Wiki on Aether + Confluence — Architecture & Handoff

**Status:** design / planning. Written to hand off to a fresh conversation so it has full
context without re-deriving it. Working language: English.

---

## 0. What this is

A company **LLM-maintained wiki** for the **CCPRM (Central Clearing Counterparty Risk
Management) Model & Analytics** team. It mirrors internal company documents, tracks external
sources, and distills both into atomic, interconnected knowledge. The structural contract is
[`SCHEMA.md`](../SCHEMA.md); the operating manual is [`CLAUDE.md`](../CLAUDE.md).

> This is the **company** wiki. It is unrelated to the author's personal "second brain" vault
> (different domain, Chinese-primary, market-microstructure/RL). Do not mix the two.

This GitHub repo (`company-llm-wiki`) is currently used as an **intermediate staging platform**
to author the schema, skills, and instructions, then sync them into the company environment.

---

## 1. The platform: Aether Orchestration Plane

Internal company orchestration platform (built on GCP; we cannot access lower-level GCP
configuration). Relevant primitives:

- **Agents** — created with: identity (name, role, routing hint), model + temperature,
  attached **skills**, **tools**, **native integrations**, a **security profile**, and
  **custom instructions** (markdown, appended after a fixed governance prompt).
  - The fixed **governance prompt** (uneditable): *"You are a helpful AI assistant. Answer
    concisely and accurately. If you do not know something, say no."* — weak; our custom
    instructions deliberately override it (see [`skill-examples/agent-custom-instructions.md`](../skill-examples/agent-custom-instructions.md)).
- **Skills** — reusable, attached to agents; selected by the agent via their `description`.
  Each skill = name + category (`data processing` | `authentication` | `api integration` |
  `logging` | `other`) + description + markdown instruction.
- **Tools** — built-in, incl. **Knowledge base search** (the platform's built-in **RAG**).
- **Native integrations** — DevOps Jira, GitHub Enterprise, Microsoft Teams, **SharePoint
  (MCP)**, internal **Confluence (MCP)**, etc.
- **Security profiles** — `sandbox` (read-only) · `restricted` (read+write) ·
  `privileged` (read+write+destructive). **Use `restricted`** for wiki agents — never
  `privileged` (protects the "never delete review notes / never destroy history" rules).
- **Knowledge base** = built-in RAG store. **It does not store readable source files** — it
  chunks + embeds for retrieval. Ingest needs the *full* document, so ingest reads from
  SharePoint/GCS or an uploaded file, **not** from the Knowledge base.
- **Memory** = markdown store with **tags**, editable in the GUI, **not versioned**. Usable as
  a tagged cache, but never the source of truth.

---

## 2. The decision: where does the wiki actually live?

Three options were considered. Current direction: **Confluence as the wiki backend.**

| Backend | Pros | Cons |
|---|---|---|
| GitHub repo (this one) | Real hierarchy, diffable history, CI (`validate_wiki.py`), PR gating | Company GitHub App install friction; not where the team reads docs |
| Aether Memory | Tags, fast, native to platform | Flat, **not versioned** → can't protect review notes / annual-review diffs |
| **Confluence (chosen)** | Team already uses it; page/sub-page tree = hierarchy; **native page version history**; internal MCP exists; built-in links | **Not markdown-native** (see §3); no PR/CI gate |

**Why Confluence fits the hardest requirement:** the wiki needs **versioning + annual review
diffs** ("if I ingest an existing file, mark what changed"). Confluence keeps a **full version
history per page** natively and can diff any two versions — this satisfies the review/diff
requirement far better than Memory, and without git plumbing.

---

## 3. Confluence reality check (important corrections)

The assumption "Confluence pages are markdown-native" is **only partly true** — design around this:

- Confluence does **not** store pages as markdown. Storage is **Atlassian Document Format
  (ADF)** / legacy XHTML "storage format". The editor and API can **accept markdown input and
  convert**, but round-tripping markdown ⇄ Confluence is lossy. Treat markdown as the *authoring*
  format and Confluence as the *rendered* store.
- **Page / sub-page tree** maps cleanly to our hierarchy (internal → policy/framework/concept/
  manual; the surfaces internal/external/knowledge as top-level spaces or parent pages).
- **YAML front matter has no native home.** Map it onto Confluence primitives:
  - structured metadata (`id`, `type`, `status`, `owner`, `version`, `completeness`,
    `concept_kind`, `parent`, `model`, …) → **page properties** (Page Properties macro) and/or
    **labels**.
  - `tags` → Confluence **labels**.
  - relationships (`parent`/`model`/`references`/`derives_from`/`implements`) → page-tree
    parentage + **internal page links**.
- **Versioning** → Confluence native page **version history** (every publish = a new version;
  diffable). Use this instead of git for the annual-review diff. Optionally tag/label a yearly
  snapshot (`review-YYYY`).
- **No PR/CI gate** on Confluence. Replace the GitHub "PR + `validate_wiki.py`" gate with an
  **agent-side validation step before publishing** (the agent runs the schema checks itself and
  publishes as a **draft / new version for human review**, never silently overwriting a stable
  page).
- **`source_refs` / raw files** stay in **SharePoint / GCS**, never pasted into Confluence.

---

## 4. The wiki contract (already authored in this repo)

- [`SCHEMA.md`](../SCHEMA.md) — surfaces (internal/external/knowledge), 12 `type`s with folder +
  id-prefix, front matter (common + type-specific), controlled vocabulary, the **"don't guess"
  rule** (unsourced → record in `open_questions`, answer **"Not documented."**), lint rules.
- [`CLAUDE.md`](../CLAUDE.md) — operating manual: query scope, the 3 workflows
  (`/ingest`, `/lint`, `/reindex`), **human review notes are sacred** (`> [!review]` /
  `<!-- review: … -->`), ingest pipeline, **all writes via PR / review — never `main`**.
- These two files are the source of truth for the agents' behavior regardless of backend. For a
  Confluence backend, only the *write/validate/version* mechanics change (§3), not the contract.

---

## 5. Target agents & skills

### Agents (start with one or two)

1. **Wiki Keeper (ingest + Q&A)** — one agent can do both to start.
   - **Ingest:** read a file via the **SharePoint MCP** → distill into an internal doc +
     knowledge layer (model + topics) per SCHEMA → **publish to Confluence** via the internal
     Confluence MCP, mapping front matter → page properties/labels and hierarchy → page tree.
   - **Versioning:** if the source already has a page, create a **new Confluence version** and
     **surface the diff / mark changed sections** (supports the annual review).
   - **Q&A:** answer from internal + knowledge; external only as citation; **"Not documented."**
     when unsourced. (Split into a separate read-only agent later if desired.)
2. **(Later, out of current scope)** separate agents for **general RAG** (Knowledge base
   search) and **web search**. Not part of the LLM-wiki architecture for now.
3. **Graph / Visualization agent** — build the link graph between documents and visualize it,
   like the Obsidian graph view. Options:
   - generate a **Mermaid / HTML graph** of `parent`/`model`/`references`/topic links and embed
     it as a Confluence page (HTML macro), or
   - lean on Confluence's native page tree + link maps where possible.

### Skills (templates already in [`skill-examples/`](../skill-examples/), GitHub-flavored)

| Skill | Category | Purpose | Confluence adaptation needed |
|---|---|---|---|
| `ingest-source` | data processing | source → internal doc + model + topics | publish to Confluence (page tree + page properties), version + diff on update |
| `query-wiki` | data processing | answer from internal+knowledge; "Not documented." | read via Confluence MCP / Knowledge base |
| `lint-wiki` | logging | schema validation + stale review / orphan topics | replace `validate_wiki.py` (CI) with agent-side checks pre-publish |
| `reindex-wiki` | data processing | rebuild indices | Confluence page-tree / index page |
| `mindmap` | other | model↔concept↔topic graph | the visualization agent's core |
| `connect-source` | api integration | locate a SharePoint/GCS source for ingest | SharePoint MCP resolution |
| `agent-custom-instructions.md` | — | the custom-instructions block to paste into the agent | English; overrides governance prompt |

> The current skill templates assume a **GitHub** backend (PR + `validate_wiki.py`). For
> Confluence, the **read/distill/honesty/linking logic is unchanged**; only the
> **write/validate/version** steps need re-pointing (publish-as-new-version + agent-side
> validation instead of PR+CI). This is the main work for the next conversation.

---

## 6. Open questions for the next conversation

**Resolved (2026-06-30), now baked into `skill-examples/`:**
- **#2 Front-matter mapping** — decided: structured fields → **page properties**;
  `type`/`status`/`surface`/`tags` + `id` + `review-YYYY` → **labels**; hierarchy
  (`parent`, surface) → **page tree**; `references`/`model`/topic links → **Confluence page
  links**. (See `ingest-source` "Front-matter mapping".)
- **#3 Validation without CI** — decided: ported into the `lint-wiki` skill, run **agent-side
  pre-publish** (and on-demand audit). No CI.
- **#4 Space/tree layout** — decided: **one space**, three top-level parent pages
  (internal/external/knowledge); hierarchy below each via the page tree.
- **#5 Diff presentation** — decided: rely on Confluence native version diff **plus** an
  agent-emitted "Changes in this version" section (the section is authoritative if the MCP can't
  diff).
- **#6 Read path for Q&A** — decided: **direct Confluence MCP reads** (search only to locate;
  read full body+properties before answering). Not RAG.

**Still open:**
1. **Confluence MCP capabilities** — confirm the internal Confluence MCP supports: create/update
   page, set page properties/labels, read version history, and **produce a version diff**. The
   skills are written to degrade gracefully if native diff is missing (the change-summary section
   covers it), but verify the create/update/properties/labels primitives exist as assumed.

---

## 7. Quick-start for the new conversation

> Read `docs/llm-wiki-architecture.md`, `SCHEMA.md`, and `CLAUDE.md` in this repo. We are moving
> the CCPRM Company Wiki onto **Confluence** (internal Confluence + internal MCP) on the Aether
> Orchestration Plane. Help me: (1) adapt the `skill-examples/` skills from a GitHub backend to
> a Confluence backend (publish as new page version, agent-side validation, front matter →
> page properties/labels, hierarchy → page tree); (2) design the ingest agent that pulls from
> the SharePoint MCP, distills per SCHEMA, publishes to Confluence, and on re-ingest creates a
> new version marking what changed (for the annual review); (3) design a Q&A behavior with the
> "Not documented." rule; (4) design a graph/visualization agent (Obsidian-style) or a Confluence
> HTML visualization. Out of scope for now: general RAG and web-search agents.
