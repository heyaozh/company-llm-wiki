"""Wiki tools — read-only Q&A over the CCPRM Model & Analytics knowledge wiki.

DROP-IN for the FastMCP template repo (the platform's "create MCP" template):
  1. copy this file       -> src/tools/wiki_tools.py
  2. copy wiki_repo.py    -> src/tools/wiki_repo.py
  3. in src/server.py add :  import src.tools.wiki_tools   # noqa: F401, E402
  4. add "pyyaml>=6.0" to pyproject dependencies; reinstall (pip install -e .)
  5. vendor wiki content into ./wiki  (internal/ external/ knowledge/), or set WIKI_ROOT

Registration happens on import (the @mcp.tool decorators run), matching the template's
example_tools.py. These are the 7 read-only Q&A tools (no write/validate tools).
"""
import os
import pathlib

from src.mcp import mcp
from src.tools.wiki_repo import WikiRepo

# Default to the repo root (this file is <repo>/src/tools/wiki_tools.py → parents[2] = repo
# root), so the server reads internal/ external/ knowledge/ that live at the repo root in a
# single-repo setup. Override with WIKI_ROOT (e.g. set it to "wiki" if you vendor a snapshot).
_DEFAULT_ROOT = pathlib.Path(__file__).resolve().parents[2]
repo = WikiRepo(os.environ.get("WIKI_ROOT", str(_DEFAULT_ROOT)))


@mcp.tool
def list_documents(type: str = "", model: str = "", status: str = "") -> list[dict]:
    """List wiki documents, optionally filtered by type / model / status. type is one of:
    policy, framework, concept, manual, business_requirement, specification, regulation,
    paper, article, other, model, topic. Returns front-matter summaries."""
    return repo.list_documents(type=type, model=model, status=status)


@mcp.tool
def get_document(doc_id: str) -> dict:
    """Return the full front matter and Markdown body of a document by id."""
    return repo.get_document(doc_id)


@mcp.tool
def get_traceability(model_id: str) -> dict:
    """Return the concept -> business_requirement -> specification chain (plus manuals)
    for a given model id."""
    return repo.traceability(model_id)


@mcp.tool
def find_gaps() -> list[dict]:
    """List documents that are not 'complete' or that carry open_questions — the canonical
    'what we do not yet know' view. Use it instead of guessing."""
    return repo.find_gaps()


@mcp.tool
def find_stale(year: int = 0) -> list[dict]:
    """List documents whose review_year is older than `year` (default: current year)."""
    return repo.find_stale(year or None)


@mcp.tool
def references(doc_id: str) -> dict:
    """Return outbound and inbound links for a document (traceability / orphans)."""
    return repo.references_of(doc_id)


@mcp.tool
def search_wiki(query: str, k: int = 6) -> list[dict]:
    """Search the wiki for a query. Returns [{doc_id, title, score, snippet}]."""
    return repo.search(query, k)
