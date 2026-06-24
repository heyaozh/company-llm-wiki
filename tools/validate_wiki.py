#!/usr/bin/env python3
"""Validate the CCPRM Model & Analytics wiki against SCHEMA.md.

Surfaces:
  internal/   policy, framework, concept, manual, business-requirements, specifications
  external/   regulation, paper, article, other
  knowledge/  model, topic   (our distilled layer)

Errors (fail the build):
  - required front-matter field missing; `id` != filename stem; id prefix / folder mismatch
  - value outside controlled vocabulary (type / status / completeness / concept_kind)
  - any referenced id (model / parent / derives_from / implements / references) does not exist
  - concept without concept_kind; specification without implements; BR without derives_from

Warnings (do not fail):
  - completeness != complete with empty open_questions
  - review_year older than the current year (stale)

Usage:  python tools/validate_wiki.py        Requires: pyyaml
"""
from __future__ import annotations

import datetime
import pathlib
import sys

import yaml

# type -> folder (relative to repo root)
TYPE_DIRS = {
    "policy": "internal/policy",
    "framework": "internal/framework",
    "concept": "internal/concept",
    "manual": "internal/manual",
    "business_requirement": "internal/business-requirements",
    "specification": "internal/specifications",
    "regulation": "external/regulation",
    "paper": "external/paper",
    "article": "external/article",
    "other": "external/other",
    "model": "knowledge/model",
    "topic": "knowledge/topic",
}
ID_PREFIX = {
    "policy": "pol-", "framework": "fwk-", "concept": "con-", "manual": "man-",
    "business_requirement": "br-", "specification": "spec-",
    "regulation": "reg-", "paper": "paper-", "article": "art-", "other": "other-",
    "model": "model-", "topic": "topic-",
}
STATUS = {"draft", "review", "stable", "deprecated"}
COMPLETENESS = {"complete", "partial", "theory_only"}
CONCEPT_KIND = {"methodology", "pricing", "risk"}
COMMON_REQUIRED = [
    "id", "type", "title", "status", "owner", "version",
    "review_year", "last_reviewed", "completeness", "open_questions", "source_refs",
]
REF_FIELDS = ("model", "parent", "derives_from", "implements", "references")

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []
warnings: list[str] = []


def load(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{path}: missing YAML front matter")
        return None
    try:
        _, fm, _ = text.split("---", 2)
        return yaml.safe_load(fm) or {}
    except (ValueError, yaml.YAMLError) as exc:
        errors.append(f"{path}: front matter error: {exc}")
        return None


def doc_files():
    for folder in TYPE_DIRS.values():
        d = ROOT / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name == "index.md" or p.name.startswith("_"):
                continue
            yield p


def as_list(v):
    if not v:
        return []
    return [v] if isinstance(v, str) else list(v)


def main() -> int:
    docs = {}
    for path in doc_files():
        fm = load(path)
        if fm is None:
            continue
        stem = path.stem
        if fm.get("id") != stem:
            errors.append(f"{path}: id '{fm.get('id')}' must equal filename stem '{stem}'")
        for field in COMMON_REQUIRED:
            if field not in fm:
                errors.append(f"{path}: missing required field '{field}'")
        dtype = fm.get("type")
        if dtype not in TYPE_DIRS:
            errors.append(f"{path}: invalid type '{dtype}'")
        else:
            if path.parent != (ROOT / TYPE_DIRS[dtype]):
                errors.append(f"{path}: type '{dtype}' must live in '{TYPE_DIRS[dtype]}/'")
            if isinstance(fm.get("id"), str) and not fm["id"].startswith(ID_PREFIX[dtype]):
                errors.append(f"{path}: id should start with '{ID_PREFIX[dtype]}'")
        if fm.get("status") not in STATUS:
            errors.append(f"{path}: invalid status '{fm.get('status')}'")
        if fm.get("completeness") not in COMPLETENESS:
            errors.append(f"{path}: invalid completeness '{fm.get('completeness')}'")
        if dtype == "concept" and fm.get("concept_kind") not in CONCEPT_KIND:
            errors.append(f"{path}: concept requires concept_kind in {sorted(CONCEPT_KIND)}")
        if dtype == "business_requirement" and not fm.get("derives_from"):
            errors.append(f"{path}: business_requirement must set 'derives_from'")
        if dtype == "specification" and not fm.get("implements"):
            errors.append(f"{path}: specification must set 'implements'")
        docs[stem] = (path, fm)

    ids = set(docs)
    this_year = datetime.date.today().year

    for stem, (path, fm) in docs.items():
        for field in REF_FIELDS:
            for ref in as_list(fm.get(field)):
                if ref and ref not in ids:
                    errors.append(f"{path}: {field} -> '{ref}' does not exist (dangling reference)")
        if fm.get("completeness") in {"partial", "theory_only"} and not fm.get("open_questions"):
            warnings.append(f"{path}: completeness '{fm.get('completeness')}' but no open_questions")
        ry = fm.get("review_year")
        if isinstance(ry, int) and ry < this_year:
            warnings.append(f"{path}: review_year {ry} older than {this_year} (stale)")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\nChecked {len(docs)} document(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
