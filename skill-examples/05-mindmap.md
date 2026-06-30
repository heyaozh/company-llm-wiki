name: mindmap
category: other
description: Generate a graph of the model ↔ concept ↔ topic relationships around a document, as an embeddable Confluence HTML/Mermaid visualization (Obsidian-style graph view).

---

# Mindmap from the Document Graph (Confluence backend)

Visualize how documents connect, for a model or a topic. This is the core of the
graph/visualization agent — an Obsidian-style graph view over the wiki.

## Steps
1. Take a center document (`id`) and a depth N (default 2). For a whole-space graph, omit the
   center and walk all pages.
2. Read pages via the Confluence MCP and walk the relationship fields out to depth N:
   `parent`, `model`, `derives_from`, `implements`, `references`, plus in-body topic links.
3. Build a graph where nodes = pages (title/`id` + Confluence link) and edges = relationships.
   Group/color nodes by `surface` (internal / external / knowledge) and `type`.
4. RENDER one of:
   - a **Mermaid `graph LR`** (if the space allows the Mermaid macro), or
   - a self-contained **HTML graph** embedded via the HTML macro (e.g. a force-directed view);
   make nodes link back to their Confluence pages.
5. PUBLISH as a Confluence page (e.g. under the `knowledge` parent, id-less utility page), or
   return inline for a quick look. Publishing follows the review gate; label it `needs-review`
   if it replaces an existing graph page.

Exclude human review-note content from the graph. Read-only over the wiki; never use `privileged`.
