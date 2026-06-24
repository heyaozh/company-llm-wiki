# Agent — CCPRM wiki Q&A

A read-only Q&A agent over the wiki, using the MCP server ([`../mcp_server/`](../mcp_server/))
for tools. See the design in [`../docs/architecture.md`](../docs/architecture.md).

There are two ways to run an agent, depending on your platform's **Agent slot**:

---

## A. UI-form Agent slot (no code) — recommended for this platform

Your platform's "create Agent" slot is a form (instruction + model + attach tools/MCP). You do
**not** need `agent.py`. Configure it like this:

**1. Model:** pick `gemini-2.5-flash` (or `-pro`). The platform handles auth — no key.

**2. Tools / MCP:** attach the **`ccprm-wiki`** MCP you registered in the MCP slot. Enable its
read tools (`search_wiki`, `get_document`, `get_traceability`, `find_gaps`, `find_stale`,
`list_documents`, `references`).

**3. Instruction (paste this):**

```text
You are the Q&A assistant for the CCPRM Model & Analytics knowledge wiki.

- Answer ONLY using the wiki tools provided. Always cite the document id(s) you used.
- To find content, use search_wiki; for a specific doc use get_document; for how a model's
  documents connect use get_traceability; for what is unknown use find_gaps; for coverage use
  list_documents; for freshness use find_stale.
- If the wiki has no sourced answer, reply exactly "Not documented." and call find_gaps to show
  the relevant open questions. NEVER invent formulas, data, results, or implementation details.
- Scope: internal/ (policy, framework, concept, manual, business_requirement, specification)
  and knowledge/ (model, topic). external/ documents are cited references only.
```

**4. Try these questions** (good for the demo):
- "What is the Black-76 model used for?"  → grounded answer + cited id
- "Which models use risk-neutral valuation?"  → uses references / traceability
- "What is not documented about the CRR model?"  → uses find_gaps
- "List all pricing concepts."  → uses list_documents(type=concept)
- "What is the margin add-on formula?"  → should answer "Not documented." (nothing fabricated)

---

## B. Code-based Agent slot (ADK) — alternative

If instead your platform takes ADK Python, [`agent.py`](agent.py) is a starting skeleton
(WikiRoot → WikiQA + WikiMaintainer) that connects to the MCP via `MCPToolset`. For the
read-only POC, keep only `WikiQA` and point `MCPToolset` at the hosted MCP's URL. The model is
configured by the platform.
