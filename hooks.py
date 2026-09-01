"""
mkdocs hook — render <!-- LAB_QUESTION --> blocks as visible quiz cards during
`mkdocs serve` / `mkdocs build`.

The SAME comment block is consumed by the Enablement App importer
(api/import-lab.function.ts → extractQuestions) where it becomes a graded,
interactive question. This hook is preview-only: it shows authors what learners
will see. Register in mkdocs.yaml with:

    hooks:
      - hooks.py
"""

import html
import re

import yaml

LAB_QUESTION_RE = re.compile(r"<!--\s*LAB_QUESTION\s*\n(.*?)-->", re.DOTALL)
LAB_SEED_RE = re.compile(r"<!--\s*LAB_SEED\s*\n(.*?)-->", re.DOTALL)

_CSS = """
<style>
.lab-quiz{border:1px solid #d0d7de;border-left:4px solid #6c6cff;border-radius:8px;
  padding:14px 16px;margin:18px 0;background:#fafbff}
.lab-quiz .lab-quiz-tag{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.04em;
  text-transform:uppercase;color:#6c6cff;margin-bottom:6px}
.lab-quiz .lab-quiz-q{font-weight:600;margin:0 0 10px}
.lab-quiz ul.lab-opts{list-style:none;padding:0;margin:0 0 8px}
.lab-quiz ul.lab-opts li{padding:6px 10px;margin:4px 0;border:1px solid #e2e6ea;border-radius:6px;background:#fff}
.lab-quiz ul.lab-opts li.correct{border-color:#2da44e;background:#eaf6ec;font-weight:600}
.lab-quiz ul.lab-opts li.correct::after{content:" ✓";color:#2da44e}
.lab-quiz details{margin-top:6px}
.lab-quiz details summary{cursor:pointer;color:#6c6cff;font-weight:600}
.lab-quiz code.lab-cmd{display:block;padding:8px 10px;background:#0d1117;color:#e6edf3;border-radius:6px;
  white-space:pre-wrap;margin:6px 0}
.lab-quiz .lab-badge{display:inline-block;font-size:12px;color:#57606a;background:#eef1f4;
  border-radius:12px;padding:2px 10px;margin-top:6px}
.lab-seed{border:1px solid #d0d7de;border-left:4px solid #2da44e;border-radius:8px;
  padding:14px 16px;margin:18px 0;background:#f6fbf7}
.lab-seed .lab-seed-tag{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.04em;
  text-transform:uppercase;color:#2da44e;margin-bottom:6px}
.lab-seed table{border-collapse:collapse;margin:8px 0;font-size:14px}
.lab-seed th,.lab-seed td{border:1px solid #e2e6ea;padding:4px 10px;text-align:left}
.lab-seed .lab-seed-note{font-size:13px;color:#57606a;margin-top:6px}
</style>
"""

_TYPE_TAG = {
    "multiple-choice": "Knowledge check",
    "dql-verification": "DQL validation",
    "shell-verification": "Command validation",
    "instructor-code": "Instructor unlock",
}


def _esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def _render_card(yaml_body: str) -> str:
    try:
        q = yaml.safe_load(yaml_body)
    except yaml.YAMLError:
        return "<!-- LAB_QUESTION (unparseable; left as-is in preview) -->"
    if not isinstance(q, dict) or not q.get("type") or not q.get("question"):
        return ""

    qtype = q["type"]
    tag = _TYPE_TAG.get(qtype, "Question")
    out = ['<div class="lab-quiz">']
    out.append(f'<span class="lab-quiz-tag">{_esc(tag)}</span>')
    out.append(f'<p class="lab-quiz-q">{_esc(q["question"])}</p>')

    if qtype == "multiple-choice":
        options = q.get("options") or []
        correct = q.get("correct")
        out.append('<ul class="lab-opts">')
        for i, opt in enumerate(options):
            cls = ' class="correct"' if i == correct else ""
            out.append(f"<li{cls}>{_esc(opt)}</li>")
        out.append("</ul>")
        if q.get("explanation"):
            out.append(f"<details><summary>Explanation</summary><p>{_esc(q['explanation'])}</p></details>")
    elif qtype in ("dql-verification", "shell-verification"):
        snippet = q.get("dql") or q.get("command") or ""
        if snippet:
            out.append(f'<code class="lab-cmd">{_esc(snippet)}</code>')
        out.append('<span class="lab-badge">Validated live in the Enablement app</span>')
        if q.get("explanation"):
            out.append(f"<details><summary>Explanation</summary><p>{_esc(q['explanation'])}</p></details>")
    elif qtype == "instructor-code":
        out.append('<span class="lab-badge">Unlock code provided by your instructor</span>')
        if q.get("hint"):
            out.append(f"<details><summary>Hint</summary><p>{_esc(q['hint'])}</p></details>")

    out.append("</div>")
    return "".join(out)


def _render_seed(yaml_body: str) -> str:
    """Preview a LAB_SEED block: the dataset the app ingests before the graded queries run.

    Authors need to see the exact record counts here, because the DQL thresholds in the
    same file are asserted against them (tools/validate_content.py enforces the match).
    """
    try:
        seed = yaml.safe_load(yaml_body)
    except yaml.YAMLError:
        return "<!-- LAB_SEED (unparseable; left as-is in preview) -->"
    if not isinstance(seed, dict) or not seed.get("records"):
        return ""

    out = ['<div class="lab-seed">']
    out.append('<span class="lab-seed-tag">Demo dataset</span>')
    out.append(
        f'<p class="lab-quiz-q">{_esc(seed.get("buttonText") or "Load demo data")} '
        f'&rarr; <code>{_esc(seed.get("dataset"))}</code> v{_esc(seed.get("version", 1))}</p>'
    )
    out.append("<table><tr><th>event.type</th><th>records</th><th>attributes</th></tr>")
    total = 0
    for rec in seed["records"]:
        count = rec.get("count", 0)
        total += count if isinstance(count, int) else 0
        attrs = sorted(set(list((rec.get("attributes") or {}).keys()) + list((rec.get("cycle") or {}).keys())))
        out.append(
            f"<tr><td><code>{_esc(rec.get('event.type'))}</code></td>"
            f"<td>{_esc(count)}</td><td>{_esc(', '.join(attrs))}</td></tr>"
        )
    out.append("</table>")
    out.append(
        f'<p class="lab-seed-note">{total} records per run, all tagged '
        f'<code>event.provider = "{_esc(seed.get("provider"))}"</code>, timestamps spread over '
        f'the last {_esc(seed.get("spreadMinutes", 60))} minutes. Ingested into the learner\'s own '
        f'tenant by the Enablement app.</p>'
    )
    out.append(
        '<p class="lab-seed-note">Each record also carries '
        f'<code>dt.enablement.seed.scope</code>, set from the learner\'s own identity. '
        'Every graded query in this byte must filter on it with '
        '<code>{{DT_SEED_SCOPE}}</code> — otherwise a learner\'s check passes on a '
        'classmate\'s records. <code>tools/validate_content.py</code> enforces that.</p>'
    )
    out.append("</div>")
    return "".join(out)


def on_page_markdown(markdown: str, **kwargs) -> str:
    if "LAB_QUESTION" not in markdown and "LAB_SEED" not in markdown:
        return markdown
    rendered = LAB_SEED_RE.sub(lambda m: _render_seed(m.group(1)), markdown)
    rendered = LAB_QUESTION_RE.sub(lambda m: _render_card(m.group(1)), rendered)
    return _CSS + rendered
