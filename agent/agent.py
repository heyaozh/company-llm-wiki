"""ADK agent for the CCPRM Model & Analytics wiki.

Reasoning layer on top of the MCP capability layer (mcp_server/). A root coordinator
routes to two sub-agents:
  - WikiQA          (consumer)  : grounded Q&A over the wiki; "Not documented." otherwise.
  - WikiMaintainer  (producer)  : /ingest, /lint, /reindex; all writes go through a PR.

The instructions encode the rules from CLAUDE.md (query scope + don't-guess). The tools
come from the MCP server via MCPToolset.

NOTE: ADK symbol names move between versions. This targets google-adk >= 1.0. If an import
fails, check `pip show google-adk` and the current docs; the connection-params class has
been named StdioServerParameters / StdioConnectionParams / SseServerParams /
SseConnectionParams across releases.
"""
from __future__ import annotations

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

# Local dev: talk to the MCP server over stdio.
# Cloud Run: switch to SSE (see the commented block below).
try:
    from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams as _Stdio
except ImportError:  # older ADK
    from mcp import StdioServerParameters as _Stdio  # type: ignore

WIKI_ROOT = os.environ.get("WIKI_ROOT", ".")

wiki_tools = MCPToolset(
    connection_params=_Stdio(
        command="python",
        args=["mcp_server/server.py"],
        env={"WIKI_ROOT": WIKI_ROOT, "MCP_TRANSPORT": "stdio"},
    )
)

# For the deployed MCP server, replace the block above with:
#   from google.adk.tools.mcp_tool.mcp_toolset import SseConnectionParams
#   wiki_tools = MCPToolset(connection_params=SseConnectionParams(
#       url="https://ccprm-wiki-mcp-...run.app/sse"))

GROUNDING = """You are the Q&A agent for the CCPRM Model & Analytics wiki.

HARD RULES (from CLAUDE.md / SCHEMA.md):
- Answer ONLY from the wiki, reached through the tools. Cite the doc id for every claim.
- Default scope is the curated wiki: internal/ (policy, framework, concept, manual,
  business_requirement, specification) and knowledge/ (model, topic); external/ docs are
  cited references. Raw source documents are out of scope for answering.
- If the wiki has no sourced answer, reply exactly: "Not documented." Then call
  find_gaps() or get_document() to surface the relevant open_questions.
- NEVER invent data schemas, numerical results, or implementation details. An explicit
  "Not documented." is always better than a guess.
- For coverage/freshness questions use list_documents, get_traceability, find_stale,
  find_gaps directly."""

MAINTAINER = """You maintain the CCPRM Model & Analytics wiki per CLAUDE.md.
- /ingest: distill a source methodology document into a methodology note AND the atomic,
  model-agnostic concept notes it rests on (one concept per file; merge, never duplicate).
- Record every unknown in open_questions; set completeness honestly; never guess.
- /lint: call validate() and report; do not auto-delete.
- /reindex: rebuild index.md from front matter.
- ALL writes go through propose_document (a Pull Request). Never bypass CI; never write
  to main. Link every new page to >= 2 existing pages."""


def _grounding_guard(callback_context, llm_response):
    """Optional after-model callback: where you can enforce that answers cite a doc id,
    else rewrite to "Not documented." Left as a stub to wire to your eval/guard policy."""
    return llm_response


wiki_qa = LlmAgent(
    name="WikiQA",
    model="gemini-2.5-flash",
    instruction=GROUNDING,
    tools=[wiki_tools],
    after_model_callback=_grounding_guard,
)

wiki_maintainer = LlmAgent(
    name="WikiMaintainer",
    model="gemini-2.5-pro",
    instruction=MAINTAINER,
    tools=[wiki_tools],
)

root_agent = LlmAgent(
    name="WikiRoot",
    model="gemini-2.5-flash",
    instruction=(
        "Route questions about model theory, requirements, specs, concepts, coverage, "
        "gaps, or freshness to WikiQA. Route ingest / lint / reindex / document edits to "
        "WikiMaintainer."
    ),
    sub_agents=[wiki_qa, wiki_maintainer],
)
