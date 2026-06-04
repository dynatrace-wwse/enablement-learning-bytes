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


def on_page_markdown(markdown: str, **kwargs) -> str:
    if "LAB_QUESTION" not in markdown:
        return markdown
    rendered = LAB_QUESTION_RE.sub(lambda m: _render_card(m.group(1)), markdown)
    return _CSS + rendered
