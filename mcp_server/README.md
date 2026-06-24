# MCP server — CCPRM wiki capability layer

A vendor-neutral [Model Context Protocol](https://modelcontextprotocol.io) server that exposes
the wiki as tools. It wraps [`wiki_repo.py`](wiki_repo.py) (parses the Markdown + front matter,
runs the validator). The same server works in your platform's **MCP slot**, in Claude Code, or
any MCP client.

## Tools

| Tool | Purpose |
|------|---------|
| `list_documents(type, model, status)` | Filtered front-matter summaries. |
| `get_document(doc_id)` | Full front matter + body. |
| `get_traceability(model_id)` | concept → BR → spec (+ manuals) chain. |
| `find_gaps()` | Docs not `complete` / with `open_questions` (the "unknowns"). |
| `find_stale(year)` | Docs whose `review_year` is older than `year`. |
| `references(doc_id)` | Inbound + outbound links. |
| `search_wiki(query, k)` | Keyword search (swap for embeddings later). |
| `validate()` | Run `tools/validate_wiki.py`. |
| `propose_document(...)` | Open a PR — **only registered when `MCP_READONLY` is unset**. |

Resources: `wiki://schema`, `wiki://manual`.

## Deploy to the platform's MCP slot (platform hosts the container)

The [`Dockerfile`](Dockerfile) builds a **self-contained** image: it bakes the wiki content in
(POC snapshot — rebuild to refresh), serves over HTTP, and is **read-only** (`MCP_READONLY=1`,
so the write tool is dropped). No git token needed.

```bash
# build from the REPO ROOT (context = repo root)
docker build -f mcp_server/Dockerfile -t ccprm-wiki-mcp .
```

Give that image (or this repo + Dockerfile path) to the MCP slot. Defaults baked in:

| Env | Value | Meaning |
|-----|-------|---------|
| `MCP_TRANSPORT` | `streamable-http` | HTTP transport. Set to `sse` if your platform expects the `/sse` endpoint instead. |
| `PORT` | `8080` | The platform usually injects its own `PORT`; the server honours it. |
| `MCP_READONLY` | `1` | Drops `propose_document` — the hosted server can only read. |
| `WIKI_ROOT` | `/app` | The baked-in wiki content. |

**Endpoint to register with the Agent:** the platform will show the MCP's URL after it boots.
For `streamable-http` the path is typically `/mcp`; for `sse` it is `/sse`. Use whichever your
platform asks for (match `MCP_TRANSPORT` to it).

> To refresh content after merging an ingest PR, rebuild the image (snapshot). Later you can
> switch to clone-on-start (set `WIKI_REPO_URL` + a read token) or a mounted volume + redeploy
> on merge.

## Run locally (stdio — Claude Code)

```bash
pip install -r mcp_server/requirements.txt
WIKI_ROOT="$(pwd)" python mcp_server/server.py
```
