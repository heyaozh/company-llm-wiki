"""WikiRepo — read/query/maintain access to the CCPRM Model & Analytics wiki.

This is the capability layer the MCP server exposes as tools. It parses the
Markdown + YAML front matter under the wiki root, answers structured queries
(traceability, gaps, stale docs), does a lightweight keyword search, runs the
existing CI validator, and opens PRs for writes (never commits to main).

Dependencies: pyyaml. Git/GitHub CLI (`gh`) only needed for `open_pr`.
"""
from __future__ import annotations

import dataclasses
import datetime
import pathlib
import re
import subprocess
import sys

import yaml

DOC_DIRS = {
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


@dataclasses.dataclass
class Doc:
    id: str
    type: str
    path: pathlib.Path
    front: dict
    body: str

    @property
    def title(self) -> str:
        return self.front.get("title", self.id)


class WikiRepo:
    def __init__(self, root: str | pathlib.Path):
        self.root = pathlib.Path(root).resolve()
        self._docs: dict[str, Doc] = {}
        self.reload()

    # ---------- loading ----------
    def reload(self) -> None:
        self._docs = {}
        for folder in DOC_DIRS.values():
            d = self.root / folder
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.md")):
                if p.name == "index.md" or p.name.startswith("_"):
                    continue
                doc = self._parse(p)
                if doc:
                    self._docs[doc.id] = doc

    @staticmethod
    def _parse(path: pathlib.Path) -> Doc | None:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return None
        try:
            _, fm, body = text.split("---", 2)
            front = yaml.safe_load(fm) or {}
        except (ValueError, yaml.YAMLError):
            return None
        return Doc(
            id=front.get("id", path.stem),
            type=front.get("type", ""),
            path=path,
            front=front,
            body=body.strip(),
        )

    # ---------- structured queries ----------
    def list_documents(self, type: str = "", model: str = "", status: str = "") -> list[dict]:
        out = []
        for doc in self._docs.values():
            if type and doc.type != type:
                continue
            if model and doc.front.get("model") != model:
                continue
            if status and doc.front.get("status") != status:
                continue
            out.append(self._summary(doc))
        return sorted(out, key=lambda d: d["id"])

    def get_document(self, doc_id: str) -> dict:
        doc = self._docs.get(doc_id)
        if not doc:
            return {"error": f"document '{doc_id}' not found"}
        return {**doc.front, "id": doc.id, "type": doc.type,
                "path": str(doc.path.relative_to(self.root)), "body": doc.body}

    def traceability(self, model_id: str) -> dict:
        """concept -> business_requirement -> specification chain (plus manuals) for a model."""
        by_type = {t: [] for t in ("concept", "manual",
                                    "business_requirement", "specification")}
        for doc in self._docs.values():
            if doc.front.get("model") == model_id and doc.type in by_type:
                by_type[doc.type].append(self._summary(doc))
        model = self._docs.get(model_id)
        return {
            "model": self._summary(model) if model else {"id": model_id, "error": "model page not found"},
            **{k: sorted(v, key=lambda d: d["id"]) for k, v in by_type.items()},
        }

    def find_gaps(self) -> list[dict]:
        """Docs that are not complete or carry open_questions (the 'unknowns')."""
        out = []
        for doc in self._docs.values():
            completeness = doc.front.get("completeness")
            oq = doc.front.get("open_questions") or []
            if completeness != "complete" or oq:
                s = self._summary(doc)
                s["open_questions"] = oq
                out.append(s)
        return sorted(out, key=lambda d: d["id"])

    def find_stale(self, year: int | None = None) -> list[dict]:
        year = year or datetime.date.today().year
        out = [self._summary(d) for d in self._docs.values()
               if isinstance(d.front.get("review_year"), int) and d.front["review_year"] < year]
        return sorted(out, key=lambda d: d["id"])

    def references_of(self, doc_id: str) -> dict:
        doc = self._docs.get(doc_id)
        if not doc:
            return {"error": f"document '{doc_id}' not found"}
        outbound = []
        for field in ("model", "derives_from", "implements", "references"):
            v = doc.front.get(field)
            if not v:
                continue
            for ref in ([v] if isinstance(v, str) else v):
                outbound.append({"field": field, "id": ref, "exists": ref in self._docs})
        inbound = []
        for other in self._docs.values():
            if other.id == doc_id:
                continue
            for field in ("model", "derives_from", "implements", "references"):
                v = other.front.get(field)
                vals = [v] if isinstance(v, str) else (v or [])
                if doc_id in vals:
                    inbound.append({"id": other.id, "field": field})
        return {"id": doc_id, "outbound": outbound, "inbound": inbound}

    # ---------- lightweight search (swap for embeddings later) ----------
    def search(self, query: str, k: int = 6) -> list[dict]:
        """Keyword search over title + body. Placeholder for semantic search.

        Replace the scorer with Vertex AI embeddings + cosine when the corpus
        grows; the tool signature stays the same.
        """
        terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
        scored = []
        for doc in self._docs.values():
            title = doc.title.lower()
            body = doc.body.lower()
            score = sum(3 * title.count(t) + body.count(t) for t in terms)
            if score:
                scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        results = []
        for score, doc in scored[:k]:
            results.append({
                "doc_id": doc.id, "type": doc.type, "title": doc.title,
                "score": score, "snippet": self._snippet(doc.body, terms),
                "completeness": doc.front.get("completeness"),
            })
        return results

    # ---------- validation ----------
    def validate(self) -> dict:
        """Run the CI validator (tools/validate_wiki.py) and return its report."""
        script = self.root / "tools" / "validate_wiki.py"
        proc = subprocess.run([sys.executable, str(script)],
                              capture_output=True, text=True, cwd=self.root)
        return {"ok": proc.returncode == 0, "output": proc.stdout + proc.stderr}

    # ---------- writes (PR only, never commits to main) ----------
    def open_pr(self, rel_path: str, content: str, message: str,
                branch: str | None = None) -> dict:
        """Write a file on a new branch and open a PR. Requires git + `gh` auth.

        Intentionally never writes to main: CI (validate_wiki.py) gates the PR and
        a human reviews it. See CLAUDE.md §4 and docs/architecture.md.
        """
        branch = branch or f"agent/{pathlib.Path(rel_path).stem}-{datetime.date.today():%Y%m%d}"
        target = (self.root / rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        try:
            self._git("checkout", "-B", branch)
            self._git("add", rel_path)
            self._git("commit", "-m", message)
            self._git("push", "-u", "origin", branch)
            pr = subprocess.run(
                ["gh", "pr", "create", "--fill", "--head", branch],
                capture_output=True, text=True, cwd=self.root)
            url = pr.stdout.strip() or pr.stderr.strip()
            return {"ok": pr.returncode == 0, "branch": branch, "pr": url}
        except subprocess.CalledProcessError as exc:
            return {"ok": False, "error": str(exc), "branch": branch}

    def _git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True,
                       capture_output=True, text=True)

    # ---------- helpers ----------
    def _summary(self, doc: Doc) -> dict:
        return {
            "id": doc.id, "type": doc.type, "title": doc.title,
            "model": doc.front.get("model"), "status": doc.front.get("status"),
            "completeness": doc.front.get("completeness"),
            "review_year": doc.front.get("review_year"),
            "owner": doc.front.get("owner"),
        }

    @staticmethod
    def _snippet(body: str, terms: list[str], width: int = 240) -> str:
        low = body.lower()
        pos = next((low.find(t) for t in terms if low.find(t) >= 0), 0)
        start = max(0, pos - width // 2)
        return body[start:start + width].replace("\n", " ").strip()
