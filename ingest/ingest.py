#!/usr/bin/env python3
"""Ingest pipeline (company OpenAI-compatible gateway).

Extract a source PDF's text locally, ask Gemini (via the company gateway) to
distill it into SCHEMA-compliant documents (one concept + one model overview +
N topics) as structured JSON, assemble + cross-link the files, validate, and
open a Pull Request for human review.

Faithful by design: the prompt forbids guessing (unknowns -> open_questions) and
the output is a PR, never a direct write to main.

Usage:
    export GATEWAY_BASE_URL=https://company.com/api
    export GATEWAY_API_KEY=...           # never commit
    python ingest/ingest.py --source "black76 option pricing model.pdf" --owner dl625 --dry-run

Requires: openai, httpx, pypdf, pydantic, pyyaml; git + `gh` for the PR.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

import yaml
from pypdf import PdfReader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gateway import chat_client
from prompt import EXTRACTION_PROMPT
from schema_models import Ingest

REPO = pathlib.Path(__file__).resolve().parent.parent
DATE = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
MAX_CHARS = 200_000  # guard against overflowing the context; chunk huge docs later


# ---------- extraction ----------
def pdf_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n\n".join((page.extract_text() or "") for page in reader.pages)


def extract(src: str, model: str) -> Ingest:
    text = pdf_text(src)
    if not text.strip():
        raise SystemExit("No extractable text (scanned PDF?). OCR is needed before ingest.")
    client = chat_client()
    system = (EXTRACTION_PROMPT
              + "\n\nReturn ONLY a JSON object matching this JSON schema:\n"
              + json.dumps(Ingest.model_json_schema()))
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "SOURCE DOCUMENT (text extracted from PDF):\n\n" + text[:MAX_CHARS]},
        ],
    )
    return Ingest.model_validate_json(resp.choices[0].message.content)


# ---------- assemble SCHEMA-compliant files ----------
def _fm(d: dict) -> str:
    return "---\n" + yaml.safe_dump(d, sort_keys=False, allow_unicode=True) + "---\n"


def build_files(ing: Ingest, owner: str, source_ref: str) -> dict[str, str]:
    model_id = f"model-{ing.model.slug}"
    con_id = f"con-{ing.concept.slug}"
    topic_ids = [f"topic-{t.slug}" for t in ing.topics]
    files: dict[str, str] = {}

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
        "## Distilled topics\n"
        + ("".join(f"- [{t.title}](../topic/topic-{t.slug}.md)\n" for t in ing.topics) or "- _none_\n")
        + f"\n## Status & review\nDraft, last reviewed {DATE}. AI-drafted from source; pending human review.\n"
    )

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


# ---------- validate + PR ----------
def write_and_validate(files: dict[str, str]) -> bool:
    for rel, content in files.items():
        p = REPO / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    v = subprocess.run([sys.executable, str(REPO / "tools" / "validate_wiki.py")],
                       cwd=REPO, capture_output=True, text=True)
    print(v.stdout)
    return v.returncode == 0


def open_pr(files: dict[str, str], branch: str, message: str) -> None:
    if not write_and_validate(files):
        print("Validation failed — files written but NOT pushed. Review and fix.")
        return
    subprocess.run(["git", "checkout", "-B", branch], cwd=REPO, check=True)
    subprocess.run(["git", "add", *files.keys()], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO, check=True)
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=REPO, check=True)
    subprocess.run(["gh", "pr", "create", "--fill", "--head", branch], cwd=REPO)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="local path to the source PDF")
    ap.add_argument("--owner", required=True)
    ap.add_argument("--model", default="gemini-2.5-pro", help="model id as named on your gateway")
    ap.add_argument("--dry-run", action="store_true", help="write files + validate, no PR")
    args = ap.parse_args()

    ing = extract(args.source, args.model)
    source_ref = f"{pathlib.Path(args.source).name} (local source; replace with SharePoint link)"
    files = build_files(ing, args.owner, source_ref)
    if args.dry_run:
        write_and_validate(files)
        print(f"Wrote {len(files)} file(s). Review them, then re-run without --dry-run to open a PR.")
        return 0
    branch = f"ingest/{ing.model.slug}-{DATE}"
    open_pr(files, branch, f"Ingest {ing.model.title} from {source_ref} (AI draft, pending review)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
