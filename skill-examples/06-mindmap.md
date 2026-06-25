name: mindmap
category: other
description: Generate an Obsidian-style mindmap (Mermaid) from the [[wikilink]] graph around a topic.

---

# Mindmap from Wikilink Graph

Generate an Obsidian-style mindmap for a topic, like the Obsidian graph view.

## Steps
1. Take a center note (slug or title) and a depth N (default 2).
2. Walk `[[wikilink]]` connections in the curated wiki out to depth N.
3. Emit a Mermaid `mindmap` (or `graph LR`) where nodes = note titles, edges = links.
   Color/group nodes by `type` (paper/concept/method/project).
4. Save to a `_mindmaps/<center-slug>.md` and commit, or return inline if the user just
   wants to view it. Exclude `scope:inbox` notes and user-annotation footnotes.
