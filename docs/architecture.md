# Agent & MCP Architecture — CCPRM Model & Analytics Wiki

How we put an LLM agent on top of this wiki using **Google ADK** (Agent Development Kit) for
reasoning and the **Model Context Protocol (MCP)** for the wiki's capability layer. The
guiding principle is the same one behind the repo itself: **format, not platform** — GitHub
stays the neutral source of truth, and a vendor-neutral MCP server keeps the wiki usable from
any cloud or client.

---

## 1. Layering: ADK vs MCP

They are not an either/or — they are two layers:

- **MCP server (capability layer).** Wraps the repo + the CI validator + retrieval and
  exposes them as tools/resources. Vendor-neutral. The *same* server is consumed by the GCP
  agent, by Claude Code locally, and by anything else that speaks MCP.
- **ADK agent (reasoning layer).** Gemini + the rules from [`../CLAUDE.md`](../CLAUDE.md),
  calling the MCP tools via `MCPToolset`.

> If we were GCP-only forever, native ADK function tools would be simpler. We choose MCP
> because we live on multiple surfaces (GCP, Databricks, local Claude): write the wiki tools
> once, consume them everywhere. MCP is the anti-lock-in seam.

---

## 2. Architecture diagram

```
                       ┌───────────────────────────────────────────┐
                       │  GitHub: company-llm-wiki                   │
                       │  (Markdown + YAML front matter)             │
                       │  SOURCE OF TRUTH — neutral, versioned       │
                       └───────────────────────────────────────────┘
                            ▲                         │ clone / pull (webhook)
              PR (gh API)   │                         ▼
                            │      ┌────────────────────────────────────────┐
                            │      │  MCP server (FastMCP, Python)            │
                            │      │  on Cloud Run  —  CAPABILITY LAYER       │
                            └──────┤  read:  list_documents · get_document   │
                                   │         get_traceability · find_gaps    │
                                   │         find_stale · references         │
                                   │         search_wiki · validate          │
                                   │  write: propose_document  → PR only      │
                                   │  resources: wiki://schema · wiki://manual│
                                   └────────────────────────────────────────┘
                                       ▲                         ▲
                            MCPToolset │ (SSE)            stdio   │
                                       │                         │
                  ┌────────────────────┴─────────┐     ┌─────────┴───────────┐
                  │  ADK agent (Vertex AI Agent   │     │  Claude Code (local) │
                  │  Engine / Cloud Run)          │     │  maintains the repo  │
                  │  ┌─────────────────────────┐  │     └─────────────────────┘
                  │  │ WikiRoot (coordinator)  │  │
                  │  │  ├─ WikiQA  (consumer)  │  │     CI: GitHub Actions runs
                  │  │  └─ WikiMaintainer (PR) │  │     validate_wiki.py on every PR
                  │  └─────────────────────────┘  │
                  └───────────────────────────────┘
                                       ▲
                                       │ chat / API
                              users · Slack · internal app
```

Data flow in one line: **GitHub → (clone) → MCP server → (MCPToolset) → ADK agent → users**;
and for writes: **agent → propose_document → PR → CI → human merge → GitHub**.

---

## 3. Agent roles

A `WikiRoot` coordinator routes to two sub-agents. The split mirrors the
producer/consumer separation in `CLAUDE.md`.

| Agent | Model | Type | Responsibilities | Tools |
|-------|-------|------|------------------|-------|
| **WikiRoot** | gemini-2.5-flash | coordinator | Classify the request and route it. | — |
| **WikiQA** | gemini-2.5-flash | consumer (read-only) | Grounded Q&A: model theory, requirements, specs, concepts; coverage/freshness questions. Cites doc ids. Says **"Not documented."** when unsourced. | `list_documents`, `get_document`, `get_traceability`, `find_gaps`, `find_stale`, `references`, `search_wiki` |
| **WikiMaintainer** | gemini-2.5-pro | producer (write via PR) | `/ingest` (distill a source into internal docs + knowledge model/topics), `/lint`, `/reindex`. Writes only through PRs. | all read tools + `validate`, `propose_document` |

Start with **WikiQA only** — it delivers most of the "library / tracking" value with zero
write risk. Enable WikiMaintainer once the read path is trusted.

---

## 4. MCP tool catalog

Implemented in [`../mcp_server/server.py`](../mcp_server/server.py) over
[`../mcp_server/wiki_repo.py`](../mcp_server/wiki_repo.py).

| Tool | Kind | What it returns |
|------|------|-----------------|
| `list_documents(type, model, status)` | structured | Filtered front-matter summaries. |
| `get_document(doc_id)` | structured | Full front matter + body. |
| `get_traceability(model_id)` | structured | concept → BR → spec (+ manuals) chain for a model. |
| `find_gaps()` | structured | Docs not `complete` / with `open_questions` — the **"what we don't know"** view. |
| `find_stale(year)` | structured | Docs whose `review_year` is older than `year`. |
| `references(doc_id)` | structured | Inbound + outbound links (traceability / orphan detection). |
| `search_wiki(query, k)` | semantic | Keyword search today; swap in embeddings without changing the signature. |
| `validate()` | structured | Runs `tools/validate_wiki.py` (schema + reference integrity). |
| `propose_document(rel_path, content, message)` | write | Opens a PR. **Never** commits to main. |

Most "track the library" needs are **structured queries**, not retrieval — no vector store
required to get started.

---

## 5. The "don't guess" guarantee (three gates)

Requirement: we have the theory but not all downstream detail; the agent must not fabricate.

1. **Tool-bounded answers.** WikiQA has no free-form knowledge tool — only wiki tools — and
   every answer must cite a doc id.
2. **Grounding guard.** An ADK `after_model_callback` (stub in `agent/agent.py`) enforces
   "cite a doc id, else respond 'Not documented.' and surface `open_questions`."
3. **Writes are PRs.** `propose_document` opens a branch + PR; GitHub Actions runs
   `validate_wiki.py` (dangling refs / broken chain / missing fields fail the build); a human
   reviews and merges. The agent never writes `main`. Human-in-the-loop is the PR.

---

## 6. Retrieval strategy

- **Now:** structured front-matter queries + keyword `search_wiki`. Dependency-free; the
  corpus is small.
- **Later (when the corpus grows):** replace the scorer in `WikiRepo.search` with **Vertex AI
  embeddings** (`text-embedding-005`) + cosine; if it grows large, move the index to **Vertex
  AI Vector Search**. The MCP tool signature stays identical, so nothing downstream changes.

---

## 6b. Ingest pipeline ([`../ingest/`](../ingest/))

The producer path is a **deterministic pipeline**, not a free-roaming agent:

```
local PDF ──▶ extract text (pypdf) ──▶ Gemini via company gateway (OpenAI-compatible)
                                              │  structured JSON (schema_models.Ingest)
                                              ▼
              concept + model + topics ──▶ validate_wiki.py ──▶ PR ──▶ human review ──▶ merge
```

Model access is the firm's **OpenAI-compatible gateway** (`base_url` + key, corporate TLS) via
[`../ingest/gateway.py`](../ingest/gateway.py) — not the public Google API. Why a pipeline and
not a chat agent: Gemini does only *content extraction* (faithful to the source, unknowns
forced into `open_questions`); Python owns the front matter, ids, cross-links, and validation.
The result is a reviewable PR — never a direct write to `main`. It runs as a plain Python job
on the internal platform (no "create Agent" slot needed). The same `extract()` / `open_pr()`
functions can later be wrapped as tools for an interactive agent.

## 7. Deployment (GCP)

| Component | Target | Notes |
|-----------|--------|-------|
| MCP server | **Cloud Run** | Container in `mcp_server/Dockerfile`; clones the wiki on start, `git pull` on webhook; stateless, scales horizontally. |
| ADK agent | **Vertex AI Agent Engine** (recommended) or Cloud Run | Agent Engine manages sessions/scaling; Cloud Run via `adk deploy cloud_run`. |
| Secrets | **Secret Manager** | GitHub token (write path only), API keys. Read-only deploys need no token. |
| Identity | Service accounts | Least-privilege between Cloud Run ↔ Vertex ↔ GitHub. |
| Embeddings (later) | Vertex AI Embeddings / Vector Search | Only when keyword search is outgrown. |

Indicative commands:

```bash
# MCP server → Cloud Run
gcloud run deploy ccprm-wiki-mcp --source mcp_server \
  --set-env-vars MCP_TRANSPORT=sse,WIKI_REPO_URL=https://github.com/heyaozh/company-llm-wiki.git \
  --region europe-west1 --no-allow-unauthenticated

# ADK agent → Cloud Run (or use Vertex AI Agent Engine)
adk deploy cloud_run --project <proj> --region europe-west1 agent
```

---

## 8. Build order (de-risked)

1. **Local, read-only.** Run the MCP server over `stdio`; verify the tools from Claude Code.
   (Possible today — no GCP needed.)
2. **ADK locally.** `adk web` with `WikiQA` over the stdio MCP server.
3. **Service.** Move the MCP server to SSE on Cloud Run; point the agent at its URL.
4. **Managed agent.** Deploy the agent to Vertex AI Agent Engine.
5. **Enable writes.** Turn on `WikiMaintainer` / `propose_document` last, behind PR + CI.

---

## 9. How this fits the wider stack

- **GitHub is the neutral source of truth.** GCP/ADK reasons over it; Databricks Genie or a
  Databricks job can read the *same* repo (or the MCP server) independently. Neither cloud
  owns the knowledge.
- **MCP is the portability seam.** One capability layer, many reasoning layers (ADK/Gemini,
  Claude, future tools). If we ever move off ADK, the wiki and its tools are untouched.
