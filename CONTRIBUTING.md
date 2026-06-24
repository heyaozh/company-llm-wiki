# Contributing

How to add and maintain documents in the CCPRM Model & Analytics wiki. All content is in
**English**. Read [`SCHEMA.md`](SCHEMA.md) first — it is the contract CI enforces.

---

## Add a new document

1. Pick the type and copy the matching template:
   - methodology → `methodology/_TEMPLATE.md` → `methodology/meth-<slug>.md`
   - business requirement → `business-requirements/_TEMPLATE.md` → `br-<slug>.md`
   - specification → `specifications/_TEMPLATE.md` → `spec-<slug>.md`
2. Set `id` to the filename stem (without `.md`).
3. Fill the front matter. Set `model:` to an existing model id (create the model page under
   `models/` first if needed).
4. Add the traceability link for the type (`derives_from` for BR, `implements` for spec).
5. Write the body following the section structure in `SCHEMA.md` §5.
6. **Do not guess.** Cite sources in `source_refs`; put every unknown in `open_questions`
   and set `completeness` accordingly (`theory_only` / `partial` / `complete`).
7. Add a one-line entry to [`log.md`](log.md) and link the document from [`index.md`](index.md).
8. Open a Pull Request. CI runs `tools/validate_wiki.py`; fix any reported errors.

## Update an existing document

- Make the edit, bump `version`, update `last_reviewed` and `review_year`.
- If you remove text that another document relies on, update the referring document too so no
  link dangles.

## Annual review (yearly change tracking)

Once per year the team reviews each model's chain:

1. For every reviewed document, update `last_reviewed`, `review_year`, and `status`.
2. Resolve or re-state `open_questions`; downgrade `completeness` if information is now known
   to be missing.
3. Commit the review, then tag it:
   ```bash
   git tag review-2026
   git push origin review-2026
   ```
4. Differences between years are then a plain diff:
   ```bash
   git diff review-2026 review-2027
   ```

## Reference integrity

`tools/validate_wiki.py` checks, on every push and PR:

- front matter completeness and controlled vocabulary,
- `id` matches filename,
- every `model` / `derives_from` / `implements` / `references` id exists (no dangling links),
- the traceability chain is unbroken (spec→BR, BR→methodology).

Run it locally before pushing:

```bash
python tools/validate_wiki.py
```
