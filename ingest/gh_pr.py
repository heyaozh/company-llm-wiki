"""Open a GitHub Pull Request with one or more files via the REST API (no git/gh CLI).

Designed for locked-down containers (e.g. Cloud Run) that can reach GitHub with a token.
Supports GitHub Enterprise via GITHUB_API_URL and corporate TLS via GITHUB_CA_BUNDLE.

Env:
  GITHUB_TOKEN     PAT / app token with repo write access      (required)
  GITHUB_REPO      "org/repo"                                   (required)
  GITHUB_API_URL   default https://api.github.com
                   GitHub Enterprise: https://<host>/api/v3
  GITHUB_BASE      base branch, default "main"
  GITHUB_CA_BUNDLE optional path to the corporate root CA .pem
"""
from __future__ import annotations

import base64
import os

import httpx


def _client() -> httpx.Client:
    ca = os.environ.get("GITHUB_CA_BUNDLE")
    return httpx.Client(
        base_url=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
        headers={
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        verify=ca if ca else True,
        timeout=30.0,
    )


def open_pr(files: dict[str, str], branch: str, title: str, body: str = "") -> str:
    """Create `branch` off the base, commit each file in `files` (path -> content),
    open a PR, and return its URL. Creates or updates files (handles existing ones)."""
    repo = os.environ["GITHUB_REPO"]
    base = os.environ.get("GITHUB_BASE", "main")
    with _client() as c:
        # 1) base branch head sha
        r = c.get(f"/repos/{repo}/git/ref/heads/{base}")
        r.raise_for_status()
        base_sha = r.json()["object"]["sha"]

        # 2) create the new branch (422 = already exists, fine)
        r = c.post(f"/repos/{repo}/git/refs",
                   json={"ref": f"refs/heads/{branch}", "sha": base_sha})
        if r.status_code not in (201, 422):
            r.raise_for_status()

        # 3) write each file (Contents API; include sha if updating an existing file)
        for path, content in files.items():
            cur = c.get(f"/repos/{repo}/contents/{path}", params={"ref": branch})
            payload = {
                "message": title,
                "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
                "branch": branch,
            }
            if cur.status_code == 200:
                payload["sha"] = cur.json()["sha"]
            r = c.put(f"/repos/{repo}/contents/{path}", json=payload)
            r.raise_for_status()

        # 4) open the PR
        r = c.post(f"/repos/{repo}/pulls",
                   json={"title": title, "head": branch, "base": base, "body": body})
        r.raise_for_status()
        return r.json()["html_url"]
