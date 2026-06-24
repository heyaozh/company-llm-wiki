"""Drop-in wiki tools for a FastMCP server template.

Copy this file AND `wiki_repo.py` into the template's `src/tools/` folder, then in the
template's `src/server.py` (after the FastMCP instance `mcp` is created) add:

    from tools.wiki_tools import register_wiki_tools
    register_wiki_tools(mcp)

Vendor the wiki content (internal/, external/, knowledge/, SCHEMA.md, CLAUDE.md) into a
folder and point WIKI_ROOT at it (default: ./wiki). Add `pyyaml` to the template deps.

These are the 7 read-only Q&A tools (no write/validate tools — the hosted server only reads).
"""
from __future__ import annotations

import os

try:
    from .wiki_repo import WikiRepo          # package layout (src/tools/ is a package)
except ImportError:                          # flat layout
    from wiki_repo import WikiRepo


def register_wiki_tools(mcp, wiki_root: str | None = None):
    """Register the wiki read tools on a FastMCP instance. Returns the WikiRepo."""
    repo = WikiRepo(wiki_root or os.environ.get("WIKI_ROOT", "wiki"))

    @mcp.tool()
    def list_documents(type: str = "", model: str = "", status: str = "") -> list[dict]:
        """List wiki documents, optionally filtered by type / model / status. type is one of:
        policy, framework, concept, manual, business_requirement, specification, regulation,
        paper, article, other, model, topic. Returns front-matter summaries."""
        return repo.list_documents(type=type, model=model, status=status)

    @mcp.tool()
    def get_document(doc_id: str) -> dict:
        """Return the full front matter and Markdown body of a document by id."""
        return repo.get_document(doc_id)

    @mcp.tool()
    def get_traceability(model_id: str) -> dict:
        """Return the concept -> business_requirement -> specification chain (plus manuals)
        for a given model id."""
        return repo.traceability(model_id)

    @mcp.tool()
    def find_gaps() -> list[dict]:
        """List documents that are not 'complete' or that carry open_questions — the
        canonical 'what we do not yet know' view. Use it instead of guessing."""
        return repo.find_gaps()

    @mcp.tool()
    def find_stale(year: int = 0) -> list[dict]:
        """List documents whose review_year is older than `year` (default: current year)."""
        return repo.find_stale(year or None)

    @mcp.tool()
    def references(doc_id: str) -> dict:
        """Return outbound and inbound links for a document (traceability / orphans)."""
        return repo.references_of(doc_id)

    @mcp.tool()
    def search_wiki(query: str, k: int = 6) -> list[dict]:
        """Search the wiki for a query. Returns [{doc_id, title, score, snippet}]."""
        return repo.search(query, k)

    return repo
