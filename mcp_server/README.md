# MCP server — CCPRM wiki capability layer

A vendor-neutral [Model Context Protocol](https://modelcontextprotocol.io) server that
exposes this wiki as tools and resources. The **same** server is consumed by the GCP/ADK
agent (via `MCPToolset`), by Claude Code locally, or by any MCP client — this is what keeps
the wiki portable across clouds (see [`../docs/architecture.md`](../docs/architecture.md)).

It wraps [`wiki_repo.py`](wiki_repo.py), which parses the Markdown + YAML front matter,
answers structured queries, runs the CI validator, and opens PRs for writes.

## Tools

| Tool | Role | Purpose |
|------|------|---------|
| `list_documents(type, model, status)` | read | Filtered front-matter summaries. |
| `get_document(doc_id)` | read | Full front matter + body. |
| `get_traceability(model_id)` | read | methodology → BR → spec (+ concepts) chain. |
| `find_gaps()` | read | Docs not `complete` / with `open_questions` (the "unknowns"). |
| `find_stale(year)` | read | Docs whose `review_year` is older than `year`. |
| `references(doc_id)` | read | Inbound + outbound links (traceability / orphans). |
| `search_wiki(query, k)` | read | Keyword search (swap for embeddings later). |
| `validate()` | read | Run `tools/validate_wiki.py`. |
| `propose_document(rel_path, content, message)` | write | Open a PR — **never** commits to main. |

Resources: `wiki://schema` (SCHEMA.md), `wiki://manual` (CLAUDE.md).

## Run locally (stdio — works with Claude Code)

```bash
pip install -r mcp_server/requirements.txt
WIKI_ROOT="$(pwd)" python mcp_server/server.py
```

Register it with Claude Code (`.mcp.json` or `claude mcp add`) pointing at that command.

## Run as a service (SSE — for the GCP agent)

```bash
WIKI_ROOT="$(pwd)" MCP_TRANSPORT=sse python mcp_server/server.py
```

## Deploy to Cloud Run

```bash
gcloud run deploy ccprm-wiki-mcp \
  --source . \
  --set-env-vars MCP_TRANSPORT=sse,WIKI_REPO_URL=https://github.com/heyaozh/company-llm-wiki.git \
  --region europe-west1 --no-allow-unauthenticated
```

Put the GitHub token in Secret Manager and mount it; the write path (`propose_document`)
needs `git` + `gh` auth. Read-only deployments can omit the token entirely.
