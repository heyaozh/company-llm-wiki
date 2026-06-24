# ADK agent — CCPRM wiki reasoning layer

A [Google ADK](https://google.github.io/adk-docs/) agent that reasons over the wiki using the
MCP capability layer ([`../mcp_server/`](../mcp_server/)). See the full design in
[`../docs/architecture.md`](../docs/architecture.md).

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `WikiRoot` | gemini-2.5-flash | Coordinator — routes to the sub-agents. |
| `WikiQA` | gemini-2.5-flash | Grounded Q&A; cites doc ids; says "Not documented." when unsourced. |
| `WikiMaintainer` | gemini-2.5-pro | `/ingest`, `/lint`, `/reindex`; writes via PR only. |

## Run locally

```bash
pip install -r agent/requirements.txt
export GOOGLE_GENAI_USE_VERTEXAI=TRUE GOOGLE_CLOUD_PROJECT=<proj> GOOGLE_CLOUD_LOCATION=<region>
export WIKI_ROOT="$(pwd)"
adk web          # dev chat UI    (or: adk run agent)
```

The agent spawns the MCP server over stdio (see `agent.py`). For the deployed server, switch
`MCPToolset` to `SseConnectionParams` pointing at the Cloud Run URL.

## Deploy

- **Vertex AI Agent Engine** (managed sessions/scaling) — recommended for production.
- **Cloud Run**: `adk deploy cloud_run --project <proj> --region <region> agent`.

> ADK symbol names shift between versions; `agent.py` notes the affected imports. Pin a
> version and adjust if an import fails.
