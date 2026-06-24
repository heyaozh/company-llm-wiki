"""Extraction prompt for the ingest pipeline. Encodes the SCHEMA / CLAUDE.md rules."""

EXTRACTION_PROMPT = """You are distilling ONE source document for the CCPRM Model & Analytics
knowledge wiki. The source document's text is provided in the user message. Produce JSON
matching the provided schema.

ABSOLUTE RULES (do not violate):
1. DO NOT GUESS. State only what the source document actually contains. If something is not in
   the document (data sources, products covered, numerical results, IT/implementation details,
   firm-specific conventions), DO NOT invent it — instead add a clear entry to `open_questions`
   describing exactly what is missing. An explicit gap is required; a fabricated fact is forbidden.
2. Set `completeness`:
   - "theory_only"  -> only the theory/methodology is in the source; downstream unknown.
   - "partial"      -> some downstream detail present, gaps remain (list them).
   - "complete"     -> fully documented; open_questions may be empty.
   If unsure, choose the LOWER completeness and list the gaps.
3. Write in ENGLISH. Use LaTeX ($$...$$) for equations, transcribed faithfully from the source.

WHAT TO PRODUCE:
- model: a short overview of the model the document describes (what it is, what it is used for).
- concept: the methodology/pricing/risk write-up — summary, theory (key definitions and
  equations from the source), inputs & data (only if stated), assumptions/limitations.
  Choose concept_kind: methodology | pricing | risk based on the document's nature.
- topics: the atomic, MODEL-AGNOSTIC primitives the document rests on (e.g. a pricing
  principle, a distributional assumption, a numerical scheme). One idea per topic. Prefer
  well-known reusable concepts that other models would also use. 1-4 topics is typical; use [] if none.

Slugs must be kebab-case without any prefix (the pipeline adds prefixes). Keep titles concise.
""" + r"""

CRITICAL JSON OUTPUT RULES (the response is parsed by a machine):
- Output ONLY the JSON object — no markdown, no ```json fences, no text before or after it.
- The JSON must be strictly valid. Inside string values you MUST escape every backslash as TWO
  backslashes. Write all LaTeX with doubled backslashes, e.g. \\frac, \\sigma, \\sqrt, \\theta,
  \\sqrt{T}, and escape real newlines as \n. A single unescaped backslash breaks parsing.
"""
