#!/usr/bin/env python3
"""Validate the CCPRM Model & Analytics wiki against SCHEMA.md.

Checks (errors fail the build):
  - required front-matter fields present; `id` equals the filename stem
  - controlled-vocabulary values for type / status / completeness
  - every referenced id (model / derives_from / implements / references) exists
  - traceability chain is unbroken (specification->BR, BR->methodology)

Warnings (do not fail):
  - completeness != complete with empty open_questions
  - review_year older than the current year (stale)

Usage:  python tools/validate_wiki.py
Requires: pyyaml
"""
from __future__ import annotations

import datetime
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

TYPE_DIRS = {
    "methodology": "methodology",
    "business_requirement": "business-requirements",
    "specification": "specifications",
    "model": "models",
}
ID_PREFIX = {
    "methodology": "meth-",
    "business_requirement": "br-",
    "specification": "spec-",
    "model": "model-",
}
STATUS = {"draft", "review", "stable", "deprecated"}
COMPLETENESS = {"complete", "partial", "theory_only"}
COMMON_REQUIRED = [
    "id", "type", "title", "status", "owner", "version",
    "review_year", "last_reviewed", "completeness", "open_questions", "source_refs",
]

errors: list[str] = []
warnings: list[str] = []


def load(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{path}: missing YAML front matter")
        return None
    try:
        _, fm, _ = text.split("---", 2)
    except ValueError:
        errors.append(f"{path}: malformed front matter (need opening and closing '---')")
        return None
    try:
        data = yaml.safe_load(fm) or {}
    except yaml.YAMLError as exc:
        errors.append(f"{path}: YAML parse error: {exc}")
        return None
    return data


def doc_files():
    for folder in TYPE_DIRS.values():
        d = ROOT / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name == "index.md" or p.name.startswith("_"):
                continue
            yield p


def main() -> int:
    docs = {}  # id -> (path, front matter)
    for path in doc_files():
        fm = load(path)
        if fm is None:
            continue
        stem = path.stem
        doc_id = fm.get("id")
        if doc_id != stem:
            errors.append(f"{path}: id '{doc_id}' must equal filename stem '{stem}'")
        for field in COMMON_REQUIRED:
            if field not in fm:
                errors.append(f"{path}: missing required field '{field}'")
        dtype = fm.get("type")
        if dtype not in TYPE_DIRS:
            errors.append(f"{path}: invalid type '{dtype}'")
        else:
            if path.parent.name != TYPE_DIRS[dtype]:
                errors.append(f"{path}: type '{dtype}' must live in '{TYPE_DIRS[dtype]}/'")
            if isinstance(doc_id, str) and not doc_id.startswith(ID_PREFIX[dtype]):
                errors.append(f"{path}: id should start with '{ID_PREFIX[dtype]}'")
        if fm.get("status") not in STATUS:
            errors.append(f"{path}: invalid status '{fm.get('status')}'")
        if fm.get("completeness") not in COMPLETENESS:
            errors.append(f"{path}: invalid completeness '{fm.get('completeness')}'")
        docs[stem] = (path, fm)

    ids = set(docs)
    this_year = datetime.date.today().year

    def check_refs(path, fm, field):
        vals = fm.get(field) or []
        if isinstance(vals, str):
            vals = [vals]
        for ref in vals:
            if ref not in ids:
                errors.append(f"{path}: {field} -> '{ref}' does not exist (dangling reference)")

    for stem, (path, fm) in docs.items():
        dtype = fm.get("type")
        # model linkage (every non-model doc must point at an existing model page)
        if dtype != "model":
            model = fm.get("model")
            if not model:
                errors.append(f"{path}: missing 'model'")
            elif model not in ids:
                errors.append(f"{path}: model -> '{model}' does not exist")
        check_refs(path, fm, "references")
        if dtype == "business_requirement":
            if not fm.get("derives_from"):
                errors.append(f"{path}: business_requirement must set 'derives_from' (broken chain)")
            check_refs(path, fm, "derives_from")
        if dtype == "specification":
            if not fm.get("implements"):
                errors.append(f"{path}: specification must set 'implements' (broken chain)")
            check_refs(path, fm, "implements")

        # warnings
        if fm.get("completeness") in {"partial", "theory_only"} and not fm.get("open_questions"):
            warnings.append(f"{path}: completeness '{fm.get('completeness')}' but no open_questions listed")
        ry = fm.get("review_year")
        if isinstance(ry, int) and ry < this_year:
            warnings.append(f"{path}: review_year {ry} is older than {this_year} (stale — needs review)")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\nChecked {len(docs)} document(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
