#!/usr/bin/env python3
"""GCP ingest pipeline.

Read a source PDF with Gemini (Vertex AI), draft SCHEMA-compliant wiki documents
(one concept + one model overview + N distilled topics), wire the cross-links,
validate, and open a Pull Request for human review.

Faithful by design: the prompt forbids guessing (unknowns -> open_questions) and
the output is a PR, never a direct write to main.

Usage:
    python ingest/ingest.py \
        --source gs://ccprm-model-sources/black76.pdf \
        --owner dl625 \
        --project my-gcp-project --location europe-west1

Requires: google-genai, pyyaml; git + `gh` for the PR; Vertex AI enabled.
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import subprocess
import sys

import yaml
from google import genai
from google.genai import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prompt import EXTRACTION_PROMPT
from schema_models import Ingest

REPO = pathlib.Path(__file__).resolve().parent.parent
DATE = datetime.date.today().isoformat()
YEAR = datetime.date.today().year


# ---------- Gemini extraction ----------
def read_pdf_part(src: str):
    if src.startswith(("gs://", "https://", "http://")):
        return types.Part.from_uri(file_uri=src, mime_type="application/pdf")
    data = pathlib.Path(src).read_bytes()
    return types.Part.from_bytes(data=data, mime_type="application/pdf")


def extract(src: str, project: str, location: str, gemini: str) -> Ingest:
    client = genai.Client(vertexai=True, project=project, location=location)
    resp = client.models.generate_content(
        model=gemini,
        contents=[read_pdf_part(src), EXTRACTION_PROMPT],
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=Ingest,
        ),
    )
    return resp.parsed  # an Ingest instance


# ---------- assemble SCHEMA-compliant files ----------
def _fm(d: dict) -> str:
    return "---\n" + yaml.safe_dump(d, sort_keys=False, allow_unicode=True) + "---\n"


def build_files(ing: Ingest, owner: str, source_ref: str) -> dict[str, str]:
    model_id = f"model-{ing.model.slug}"
    con_id = f"con-{ing.concept.slug}"
    topic_ids = [f"topic-{t.slug}" for t in ing.topics]
    files: dict[str, str] = {}

    # model overview
    files[f"knowledge/model/{model_id}.md"] = _fm({
        "id": model_id, "type": "model", "title": ing.model.title,
        "status": "draft", "owner": owner, "version": 1,
        "review_year": YEAR, "last_reviewed": DATE,
        "completeness": ing.model.completeness,
        "open_questions": ing.model.open_questions or [],
        "source_refs": [source_ref],
        "references": [con_id] + topic_ids,
        "tags": ing.model.tags,
    }) + (
        f"\n# {ing.model.title}\n\n## Overview\n{ing.model.overview}\n\n"
        f"## Documents (traceability)\n- **Concept:** "
        f"[{ing.concept.title}](../../internal/concept/{con_id}.md)\n\n"
        "## Distilled topics\n" +
        ("".join(f"- [{t.title}](../topic/{f'topic-{t.slug}'}.md)\n" for t in ing.topics) or "- _none_\n") +
        f"\n## Status & review\nDraft, last reviewed {DATE}. AI-drafted from source; pending human review.\n"
    )

    # concept
    files[f"internal/concept/{con_id}.md"] = _fm({
        "id": con_id, "type": "concept", "title": ing.concept.title,
        "parent": "", "concept_kind": ing.concept.concept_kind, "model": model_id,
        "status": "draft", "owner": owner, "version": 1,
        "review_year": YEAR, "last_reviewed": DATE,
        "completeness": ing.concept.completeness,
        "open_questions": ing.concept.open_questions or [],
        "source_refs": ing.concept.source_refs or [source_ref],
        "references": [model_id] + topic_ids,
        "tags": ing.concept.tags,
    }) + (
        f"\n# {ing.concept.title}\n\n"
        "> AI-drafted from the source document; verify against the source before sign-off.\n\n"
        f"## Summary\n{ing.concept.summary}\n\n"
        f"## Theory / content\n{ing.concept.theory_md}\n\n"
        f"## Inputs & data\n{ing.concept.inputs_data}\n\n"
        f"## Assumptions & limitations\n{ing.concept.assumptions}\n\n"
        f"## Relationships\n- **Model:** [{ing.model.title}](../../knowledge/model/{model_id}.md).\n"
    )

    # topics
    for t in ing.topics:
        tid = f"topic-{t.slug}"
        files[f"knowledge/topic/{tid}.md"] = _fm({
            "id": tid, "type": "topic", "title": t.title,
            "status": "draft", "owner": owner, "version": 1,
            "review_year": YEAR, "last_reviewed": DATE,
            "completeness": t.completeness, "open_questions": t.open_questions or [],
            "source_refs": [source_ref],
            "references": [model_id, con_id], "tags": t.tags,
        }) + (
            f"\n# {t.title}\n\n## Definition\n{t.definition_md}\n\n"
            f"## Why it matters\n{t.why_it_matters}\n\n"
            f"## Used by\n- [{ing.model.title}](../model/{model_id}.md)\n"
        )
    return files


# ---------- validate + open PR ----------
def open_pr(files: dict[str, str], branch: str, message: str) -> None:
    for rel, content in files.items():
        p = REPO / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    v = subprocess.run([sys.executable, str(REPO / "tools" / "validate_wiki.py")],
                       cwd=REPO, capture_output=True, text=True)
    print(v.stdout)
    if v.returncode != 0:
        print("Validation failed — files written but NOT pushed. Fix and re-run.")
        return
    subprocess.run(["git", "checkout", "-B", branch], cwd=REPO, check=True)
    subprocess.run(["git", "add", *files.keys()], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO, check=True)
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=REPO, check=True)
    subprocess.run(["gh", "pr", "create", "--fill", "--head", branch], cwd=REPO)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="gs:// URI or local path to the source PDF")
    ap.add_argument("--owner", required=True)
    ap.add_argument("--project", required=True, help="GCP project id")
    ap.add_argument("--location", default="europe-west1")
    ap.add_argument("--gemini", default="gemini-2.5-pro")
    ap.add_argument("--dry-run", action="store_true", help="write files + validate, no PR")
    args = ap.parse_args()

    ing = extract(args.source, args.project, args.location, args.gemini)
    files = build_files(ing, args.owner, source_ref=args.source)
    branch = f"ingest/{ing.model.slug}-{DATE}"
    msg = f"Ingest {ing.model.title} from {args.source} (AI draft, pending review)"
    if args.dry_run:
        for rel, content in files.items():
            (REPO / rel).parent.mkdir(parents=True, exist_ok=True)
            (REPO / rel).write_text(content, encoding="utf-8")
        print("Wrote", len(files), "file(s). Run tools/validate_wiki.py to check.")
        return 0
    open_pr(files, branch, msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
