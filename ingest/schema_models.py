"""Structured-output schema for the ingest pipeline.

Gemini returns JSON matching `Ingest`; Python (ingest.py) turns it into
SCHEMA-compliant Markdown files and wires the cross-links. Keeping the LLM
focused on *content extraction* (faithful to the PDF, with explicit gaps) and
leaving structure/linking to code is what makes the output reliable.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Completeness = Literal["complete", "partial", "theory_only"]


class Topic(BaseModel):
    slug: str = Field(description="kebab-case, no prefix, e.g. 'risk-neutral-valuation'")
    title: str
    definition_md: str = Field(description="Atomic definition; LaTeX allowed ($$...$$).")
    why_it_matters: str
    completeness: Completeness
    open_questions: list[str] = Field(description="Every unknown. Empty only if truly complete.")
    tags: list[str]


class Concept(BaseModel):
    slug: str = Field(description="kebab-case, no prefix")
    title: str
    concept_kind: Literal["methodology", "pricing", "risk"]
    summary: str
    theory_md: str = Field(description="Theory/content from the PDF; LaTeX allowed.")
    inputs_data: str = Field(description="Inputs & data ONLY if stated in the source; else note the gap.")
    assumptions: str
    completeness: Completeness
    open_questions: list[str]
    source_refs: list[str] = Field(description="What the source is (filename/URI/citation).")
    tags: list[str]


class ModelOverview(BaseModel):
    slug: str = Field(description="kebab-case, no prefix, e.g. 'black76'")
    title: str
    overview: str
    completeness: Completeness
    open_questions: list[str]
    tags: list[str]


class Ingest(BaseModel):
    """One source document -> one model overview + one concept + N distilled topics."""
    model: ModelOverview
    concept: Concept
    topics: list[Topic]
