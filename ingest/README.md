# Ingest pipeline (company gateway)

Distils a source PDF into SCHEMA-compliant documents (one `concept` + one `model` overview +
N `topic`s), wires the cross-links, validates, and **opens a Pull Request** for human review.
See the design in [`../docs/architecture.md`](../docs/architecture.md).

Deterministic by design: the PDF text is extracted locally, Gemini (via the company gateway)
returns **structured JSON** ([`schema_models.py`](schema_models.py)), and
[`ingest.py`](ingest.py) assembles the files and links. The prompt forbids guessing (unknowns
→ `open_questions`), and nothing reaches `main` without a reviewed PR.

## Model access — company OpenAI-compatible gateway

Set these (the key is a secret — use your shell/secret store, never the repo):

```bash
export GATEWAY_BASE_URL=https://company.com/api
export GATEWAY_API_KEY=...            # your internal key
export GATEWAY_CA_BUNDLE=/path/corp-root-ca.pem   # optional but preferred (proper TLS)
```

If `GATEWAY_CA_BUNDLE` is unset, TLS verification is disabled (the quick unblock you already
used with `verify=False`). Point it at your corporate root CA when you can.

## Run

```bash
pip install -r ingest/requirements.txt

# dry run first: drafts files + validates, NO push — review the drafts vs the PDF
python ingest/ingest.py --source "black76 option pricing model.pdf" --owner dl625 --dry-run

# happy? open the PR (CI re-validates; you review the diff and merge)
python ingest/ingest.py --source "black76 option pricing model.pdf" --owner dl625
```

- `--model` defaults to `gemini-2.5-pro`; pass whatever id your gateway exposes (e.g. the
  `gemini-2.5-flash` you tested).
- Scanned PDFs have no extractable text — OCR them first.

## Re-ingest / annual update

Point it at the updated PDF again. Same ids → links stay; the PR shows a line-by-line diff;
review, merge, bump `version`/`review_year`, tag `review-YYYY`. That diff is your yearly record.

## Where this runs on your platform

This is a plain Python job — run it wherever your internal platform gives you a Python runtime
(it does not need the "create Agent" slot). The interactive **Agent** and **MCP** slots are a
separate track (see `../docs/architecture.md`).
