"""MCP server exposing the CCPRM Model & Analytics wiki as tools + resources.

Vendor-neutral: the same server is consumed by the GCP/ADK agent (via MCPToolset),
by Claude Code locally, or by any MCP client. It wraps `WikiRepo` (see wiki_repo.py).

Run:
    WIKI_ROOT=/path/to/company-llm-wiki python mcp_server/server.py            # stdio (local/Claude)
    WIKI_ROOT=/path/to/company-llm-wiki MCP_TRANSPORT=sse python mcp_server/server.py   # SSE (Cloud Run)
"""
from __future__ import annotations

import os
import pathlib

from mcp.server.fastmcp import FastMCP

from wiki_repo import WikiRepo

WIKI_ROOT = os.environ.get("WIKI_ROOT", str(pathlib.Path(__file__).resolve().parent.parent))
repo = WikiRepo(WIKI_ROOT)

mcp = FastMCP("ccprm-wiki")


# ---- read / query tools (consumer) ----
@mcp.tool()
def list_documents(type: str = "", model: str = "", status: str = "") -> list[dict]:
    """List wiki documents, optionally filtered by type / model / status.

    type is one of: policy, framework, concept, manual, business_requirement,
    specification, regulation, paper, article, other, model, topic.
    Returns front-matter summaries only (id, title, status, completeness, ...).
    """
    return repo.list_documents(type=type, model=model, status=status)


@mcp.tool()
def get_document(doc_id: str) -> dict:
    """Return the full front matter and Markdown body of a document by id."""
    return repo.get_document(doc_id)


@mcp.tool()
def get_traceability(model_id: str) -> dict:
    """Return the methodology -> business_requirement -> specification chain (plus
    concepts) for a given model id."""
    return repo.traceability(model_id)


@mcp.tool()
def find_gaps() -> list[dict]:
    """List documents that are not 'complete' or that carry open_questions. This is
    the canonical 'what we do not yet know' view — use it instead of guessing."""
    return repo.find_gaps()


@mcp.tool()
def find_stale(year: int = 0) -> list[dict]:
    """List documents whose review_year is older than `year` (default: current year)."""
    return repo.find_stale(year or None)


@mcp.tool()
def references(doc_id: str) -> dict:
    """Return outbound and inbound links for a document (for traceability / orphans)."""
    return repo.references_of(doc_id)


@mcp.tool()
def search_wiki(query: str, k: int = 6) -> list[dict]:
    """Search the wiki for a query. Returns [{doc_id, title, score, snippet}].
    Keyword-based today; swap in embeddings without changing this signature."""
    return repo.search(query, k)


@mcp.tool()
def validate() -> dict:
    """Run the CI validator (front matter, controlled vocab, reference integrity,
    traceability chain). Returns {ok, output}."""
    return repo.validate()


# ---- write tool (producer) — PR only, never main ----
@mcp.tool()
def propose_document(rel_path: str, content: str, message: str) -> dict:
    """Write a document on a new branch and open a Pull Request. NEVER commits to
    main: CI gates the PR and a human reviews it. Requires git + `gh` auth.

    rel_path example: 'internal/concept/con-initial-margin.md'
    """
    return repo.open_pr(rel_path, content, message)


# ---- resources (browsable context) ----
@mcp.resource("wiki://schema")
def schema() -> str:
    """The document contract (SCHEMA.md)."""
    return (pathlib.Path(WIKI_ROOT) / "SCHEMA.md").read_text(encoding="utf-8")


@mcp.resource("wiki://manual")
def manual() -> str:
    """The agent operating manual (CLAUDE.md)."""
    return (pathlib.Path(WIKI_ROOT) / "CLAUDE.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)
