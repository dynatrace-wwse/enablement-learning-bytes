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

## Regenerating from the app's seed data

This repo was extracted from `ui/app/training/data/demoTrainings.ts`:

```bash
cd ../dynatrace-app-enablements && node scripts/extract_learning_bytes.mjs
```
