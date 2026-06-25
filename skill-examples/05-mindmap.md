name: mindmap
category: other
description: Generate a Mermaid mindmap of the model ↔ concept ↔ topic graph around a document.

---

# Mindmap from the Document Graph

Visualize how documents connect, for a model or a topic.

## Steps
1. Take a center document (id) and a depth N (default 2).
2. Walk the relationship fields out to depth N: `parent`, `model`, `derives_from`,
   `implements`, `references`.
3. Emit a Mermaid `graph LR` where nodes = document titles/ids, edges = relationships.
   Group/color nodes by surface (internal / external / knowledge) and `type`.
4. Return inline, or save to `assets/_mindmaps/<id>.md` and open a PR if it should be kept.
   Exclude human review-note content.
