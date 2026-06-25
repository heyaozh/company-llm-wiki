#!/usr/bin/env python3
"""Turn an agent ingestion dump into a PR on the wiki repo.

Workflow:
  1. In the agent UI, upload document(s) and ask to ingest. The agent prints the wiki
     Markdown files, each wrapped in  <<<FILE: path>>> ... <<<END>>>  delimiters.
  2. Copy the agent's WHOLE reply into a text file, e.g. dump.txt.
  3. Run locally (where you have git/gh access to the wiki repo):
        python tools/apply_ingest.py --dump dump.txt --repo /path/to/wiki-repo

Parses the dump, writes the files into the repo, runs the validator, and opens a PR
(git branch + push + `gh pr create`). No cloud token needed — it uses your own git access.
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import subprocess
import sys

BLOCK = re.compile(r"<<<FILE:\s*(?P<path>[^>\n]+?)\s*>>>\s*\n(?P<body>.*?)\n?<<<END>>>", re.DOTALL)


def parse(dump: str) -> dict[str, str]:
    return {m.group("path").strip(): m.group("body").strip() + "\n" for m in BLOCK.finditer(dump)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True, help="text file containing the agent's delimited output")
    ap.add_argument("--repo", required=True, help="path to your local clone of the wiki repo")
    ap.add_argument("--branch", default="")
    ap.add_argument("--no-pr", action="store_true", help="commit+push but skip `gh pr create`")
    args = ap.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    files = parse(pathlib.Path(args.dump).read_text(encoding="utf-8"))
    if not files:
        print("No <<<FILE: ...>>> blocks found — check the agent output / delimiters.")
        return 1
    print(f"Found {len(files)} file(s):")
    for p in files:
        print("  -", p)

    for rel, content in files.items():
        t = repo / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(content, encoding="utf-8")

    validator = repo / "tools" / "validate_wiki.py"
    if validator.exists():
        v = subprocess.run([sys.executable, str(validator)], cwd=repo, capture_output=True, text=True)
        print(v.stdout)
        if v.returncode != 0:
            print("Validation FAILED — files written but NOT committed. Fix and re-run.")
            return 1

    branch = args.branch or f"ingest/{datetime.datetime.now():%Y%m%d-%H%M%S}"
    subprocess.run(["git", "checkout", "-B", branch], cwd=repo, check=True)
    subprocess.run(["git", "add", *files.keys()], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Ingest documents (agent-drafted, pending review)"], cwd=repo, check=True)
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=repo, check=True)
    if not args.no_pr:
        if subprocess.run(["gh", "pr", "create", "--fill", "--head", branch], cwd=repo).returncode != 0:
            print(f"Branch pushed. Open the PR from '{branch}' in the web UI.")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
