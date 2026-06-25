name: promote-note
category: data processing
description: Rewrite a transient inbox/idea note into an atomic wiki note (only on explicit request).

---

# Promote Transient Note → Wiki

Only run on EXPLICIT user instruction (SCHEMA promotion workflow).

## Steps
1. Read the source transient note (or a Memory entry tagged `scope:inbox`).
2. REWRITE in your own words as an atomic wiki note using the matching SCHEMA template.
   Do NOT copy speculative text verbatim.
3. Set `source_refs` to the original idea path (provenance).
4. Link to ≥2 existing wiki notes.
5. Optionally back-link the idea note (`promoted_to: [[wiki/...]]`).
6. Commit to git, mirror to Memory (`scope:wiki`), log the action.
