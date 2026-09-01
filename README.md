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

### Two gates, and what each one cannot see

`validate_content.py` is **static**. It runs with no tenant and proves arithmetic and
structure: a threshold is reachable from the declared dataset, no `correct:` index is out
of range, every question parses.

What it can never see is the class of bug this content actually shipped with: DQL that is
valid and matches nothing. `filter event.kind == "KUBERNETES_EVENT"` parses, executes,
succeeds and returns zero rows forever, because Grail is schema-on-read and filtering on a
field that does not exist is not an error. Four such queries were live.

So a second gate runs nightly against a real tenant — `verifyLearningBytes` in the
Enablement app, invoked by Orbital's nightly scheduler. It seeds each byte's dataset under
a **fresh ephemeral scope**, waits for the records to be queryable, runs each graded query
and evaluates the result with the *same* `evaluateDqlResult` the browser grades with. A
fresh scope per run is what makes it a check rather than a ratchet: last night's data
cannot satisfy tonight's assertion.

It verifies only questions on a step that declares a seed. A DQL question with no seed
reads whatever telemetry the tenant happens to have, so its failure would mean "the tenant
is quiet tonight", not "the byte is broken" — and a nightly that cries wolf gets muted.

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

Rules that keep a shared tenant clean. Grail business events are **append-only** — there
is no update, no delete and no TTL you can set at ingest — so none of this can be cleaned
up afterwards. Every control is either *don't write* or *scope the write*:

| Rule | Why |
|---|---|
| Every record carries `event.provider` under `dynatrace.enablement.` | Lab queries filter on it, so seed data can never be mistaken for production traffic, and lab queries can never read production traffic. Enforced at ingest, not only here. |
| Every record carries `dt.enablement.seed.scope`, and every graded query filters on it with `{{DT_SEED_SCOPE}}` | Thirty learners on one tenant seed the same event types at the same moment. Without the scope, learner B's check passes on learner A's records and B never has to press the button — a silent false pass. |
| Pressing the button twice inside the window is a no-op | The app asks Grail whether this scope already holds this dataset. Volume is bounded at one dataset per learner per window, not one per click. |
| ≤ 500 records per record-spec, ≤ 1000 per run | Enforced by the validator *and* re-enforced at ingest. A byte is a demo, not a load test. |
| Thresholds use `gte`, never `eq` | Reloading after part of the data has aged out tops the set up rather than replacing it, so the count inside the window can exceed the declared total. |
| A query's `from:` must be at least as wide as the seed's `spreadMinutes` | Records are backdated across the window; a narrower query cannot see the older half of its own dataset, and fails intermittently. |

The scope is computed from the caller's own identity **server-side**, and a `scope` in the
request payload is ignored — a learner must not be able to choose one, or they could read
a classmate's. `{{DT_SEED_SCOPE}}` is deliberately *not* `{{DT_SESSION_ID}}`: the session
id carries a UTC date, so data seeded at 23:59 would be unqueryable at 00:01.

The one mechanism that ever *removes* seeded data is an OpenPipeline dynamic route on
`event.provider startsWith "dynatrace.enablement."` into a short-retention bucket. That is
a per-tenant admin action nobody can assume on a customer tenant, which is why the rules
above have to stand on their own.

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
