# Ingest pipeline (GCP / Vertex AI)

Reads a source PDF with **Gemini on Vertex AI**, drafts SCHEMA-compliant documents
(one `concept` + one `model` overview + N `topic`s), wires the cross-links, validates, and
**opens a Pull Request** for human review. See the design in
[`../docs/architecture.md`](../docs/architecture.md).

It is a deterministic pipeline, not a free-roaming agent: Gemini extracts *content* as
structured JSON ([`schema_models.py`](schema_models.py)); [`ingest.py`](ingest.py) assembles
the files and links. Faithful by design — the prompt forbids guessing (unknowns go to
`open_questions`), and nothing reaches `main` without a reviewed PR.

## One-time GCP setup

```bash
gcloud services enable aiplatform.googleapis.com
gcloud storage buckets create gs://ccprm-model-sources --location europe-west1   # holds source PDFs
gcloud projects add-iam-policy-binding <PROJECT> \
  --member="user:<you>@<firm>" --role="roles/aiplatform.user"
gh auth login        # needed for the PR step
```

## Run

```bash
pip install -r ingest/requirements.txt
# upload a source PDF
gcloud storage cp "black76 option pricing model.pdf" gs://ccprm-model-sources/black76.pdf

# dry run first (writes files + validates, NO push) — review the drafts
python ingest/ingest.py --source gs://ccprm-model-sources/black76.pdf \
  --owner dl625 --project <PROJECT> --location europe-west1 --dry-run

# when happy, open the PR
python ingest/ingest.py --source gs://ccprm-model-sources/black76.pdf \
  --owner dl625 --project <PROJECT> --location europe-west1
```

The PR runs CI (`tools/validate_wiki.py`). **You review the diff against the source PDF and
merge** — the pipeline never merges for you.

## Re-ingest / annual update

Point it at the updated PDF again. It writes the same ids (so links stay), the PR shows a
line-by-line diff, you review and merge, then bump `version`/`review_year` and tag
`review-YYYY`. That diff *is* your yearly change record.

## Deploy options

- **Cloud Run job** (batch): containerise this folder; pass `--source` per run, trigger from
  Eventarc when a PDF lands in the bucket.
- **Wrap as an ADK tool**: expose `extract()` + `open_pr()` to the `WikiMaintainer` agent in
  [`../agent/`](../agent/) so it can ingest conversationally. The pipeline here is the
  trustworthy core either way.

> SDK note: uses the unified `google-genai` SDK with the Vertex backend
> (`genai.Client(vertexai=True, …)`). Pin a version; symbol names can shift.
