# Learning Bytes — Dynatrace Enablement content

Short, self-paced labs & quizzes for the **Dynatrace Enablement App**. Each top-level
section in `mkdocs.yaml` `nav` is imported as a separate Learning Byte. Pure content —
no live environment — so the app renders it as **self-paced** (a repo is treated as
Hands-On only when it ships a `.devcontainer/devcontainer.json`).

## Author & preview locally

```bash
pip install -r requirements.txt
mkdocs serve        # http://127.0.0.1:8000 — quizzes render as cards via hooks.py
```

## Structure

```
mkdocs.yaml          # nav: one top-level section per Learning Byte (→ one training each)
docs/<byte>/NN-<step>.md
hooks.py             # renders <!-- LAB_QUESTION --> blocks in the mkdocs preview
```

`nav` must have **only section entries** at the top level — that tells the app
importer to treat each section as its own training (`buildTrainingGroups` in
`api/import-lab.function.ts`).

## Quiz format

```markdown
<!-- LAB_QUESTION
type: multiple-choice
question: Which DQL command filters records by a condition?
options:
  - filter
  - summarize
correct: 0
explanation: `filter` keeps rows matching a predicate.
-->
```

Also supported: `dql-verification`, `shell-verification`, `instructor-code`.
**Never** author `code`, `secret`, `algorithm`, or `salt` under `instructor-code`.

### `correct:` is load-bearing

The app grades a multiple-choice question by **exact index match**, and a step does not
unlock until every question on it is answered correctly. There is no skip button. A
`correct:` index that points at the wrong option — or at nothing — is therefore a
**permanent deadlock** for every learner who reaches that step, not a typo.

A malformed block fails the other way: the importer logs a warning and **drops it**, so
the question silently disappears from the training. Neither failure is visible after the
fact. `tools/validate_content.py` gates both, and CI runs it on every PR.

```bash
python3 tools/validate_content.py     # exit 0 = safe to import
```

## Seed data — `<!-- LAB_SEED -->`

A `dql-verification` question is only meaningful if the tenant holds data the query can
find. Rather than assume a tenant has the right traffic, a byte **declares the dataset it
needs**, inline, in the same file as the queries that read it:

```markdown
<!-- LAB_SEED
dataset: shop-funnel
version: 1
buttonText: Load demo data
provider: dynatrace.enablement.learningbytes
spreadMinutes: 90
records:
  - event.type: com.shop.purchase.complete
    count: 12
    attributes: { storefront: learning-bytes-demo }
    cycle:
      total: [25.00, 50.00, 75.00, 100.00, 125.00, 150.00, 75.00, 100.00, 125.00, 150.00, 125.00, 100.00]
-->
```

The app renders this as a button. Pressing it ingests the records as business events into
**the learner's own tenant**, through the app's existing AppEngine ingest identity — no new
credential, no per-tenant setup. `cycle` values are applied round-robin across `count`
records, and timestamps are spread backwards over `spreadMinutes`, so the data is already
"historical" the moment it lands and a `from:now()-2h` query finds it.

Rules that keep a shared tenant clean:

| Rule | Why |
|---|---|
| Every record carries `event.provider` | Lab queries filter on it, so seed data can never be mistaken for production traffic, and lab queries can never read production traffic. |
| ≤ 500 records per record-spec, ≤ 1000 per run | Enforced by the validator. A byte is a demo, not a load test. |
| Thresholds use `gte`, never `eq` | Loading the data twice must not break the check. |

**The validator enforces that the queries and the data agree.** It aggregates each byte's
`LAB_SEED` declarations, extracts the aggregation and `event.type` from each
`dql-verification`, and fails the build when a threshold is unreachable — e.g. *"seed
produces totalRevenue=1200 but the check requires gte 5000 — this question can never
pass"*. That coupling is the point: the data and the query it must satisfy live in one
commit and are checked together.

## Provenance — do NOT "regenerate" this repo

This repo was originally extracted from `ui/app/training/data/demoTrainings.ts` in the
Enablement app, via `scripts/extract_learning_bytes.mjs`.

**That direction is now reversed and the extraction script must not be re-run.**
`DEMO_TRAININGS` in the app is an empty array — Learning Bytes are no longer hardcoded
there; they are imported at runtime from *this* repo through the content-source registry.
Re-running the extractor would regenerate the content from an empty source and delete
everything here.

This repo is the source of truth. The app is a consumer.
