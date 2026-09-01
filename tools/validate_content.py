#!/usr/bin/env python3
"""
Validate the Learning Bytes content repo before it can reach a tenant.

Why this exists
---------------
The Enablement app grades a `multiple-choice` question by exact index match, and a step
is not unlocked until every question on it is answered correctly. There is no skip. So a
single wrong `correct:` index is not a typo — it is a **permanent deadlock** for every
learner who reaches that step.

Worse, the importer's own validation *silently drops* a malformed question
(`import-lab.function.ts` → `extractQuestions` logs a warning and returns ""), so a broken
block does not fail the import. It just disappears. Neither failure mode is visible from
the outside, which is exactly why they need a gate here.

Checks
------
  structure  nav entries resolve to files; first page of each byte carries front matter
  titles     no emoji in any training title (nav) or page H1
  questions  YAML parses; required fields present; `correct` is an in-range int;
             options are 2..6 and mutually distinct; dql operators are ones the app
             implements
  seed       LAB_SEED blocks parse and are internally consistent
  coupling   every `dql-verification` threshold is *achievable against the seed data
             declared in the same byte* — this is what keeps queries and data in step

Exit code 0 = safe to import. Non-zero = would break a learner.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

QUESTION_RE = re.compile(r"<!--\s*LAB_QUESTION\s*\n(.*?)-->", re.DOTALL)
SEED_RE = re.compile(r"<!--\s*LAB_SEED\s*\n(.*?)-->", re.DOTALL)
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿⬀-⯿️←-⇿⌀-⏿]"
)

# Mirrors VALID_DQL_OPERATORS / VALID_SHELL_OPERATORS in api/import-lab.function.ts.
# Anything else is dropped by the importer without an error.
DQL_OPERATORS = {"gte", "eq", "gt", "contains", "not-empty"}
SHELL_OPERATORS = {"exit-zero", "contains", "not-empty", "gt"}
KNOWN_TYPES = {"multiple-choice", "dql-verification", "shell-verification", "instructor-code"}

errors: list[str] = []
warnings: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def warn(where: str, msg: str) -> None:
    warnings.append(f"{where}: {msg}")


def load_nav() -> list[tuple[str, list[tuple[str, str]]]]:
    cfg = yaml.safe_load((ROOT / "mkdocs.yaml").read_text())
    nav = cfg.get("nav") or []
    out = []
    for section in nav:
        if not isinstance(section, dict):
            err("mkdocs.yaml", f"top-level nav entry is not a section: {section!r}")
            continue
        title, pages = next(iter(section.items()))
        entries = []
        for page in pages or []:
            if isinstance(page, dict):
                entries.append(next(iter(page.items())))
            else:
                err("mkdocs.yaml", f"nav page under {title!r} is not a mapping: {page!r}")
        out.append((title, entries))
    return out


def check_titles(nav) -> None:
    for title, entries in nav:
        if EMOJI_RE.search(title):
            err("mkdocs.yaml", f"training title contains an emoji: {title!r}")
        for step_title, _path in entries:
            if EMOJI_RE.search(step_title):
                err("mkdocs.yaml", f"step title contains an emoji: {step_title!r}")


def check_page_h1(path: Path) -> None:
    for line in path.read_text().splitlines():
        if line.startswith("# "):
            if EMOJI_RE.search(line):
                err(str(path.relative_to(ROOT)), f"page heading contains an emoji: {line!r}")
            return


def parse_blocks(regex, text, path, label):
    out = []
    for i, body in enumerate(regex.findall(text)):
        try:
            parsed = yaml.safe_load(body)
        except yaml.YAMLError as e:
            err(f"{path}#{label}{i}", f"YAML does not parse — the importer drops it: {e}")
            continue
        if not isinstance(parsed, dict):
            err(f"{path}#{label}{i}", "block is not a YAML mapping")
            continue
        out.append((i, parsed))
    return out


def check_question(where: str, q: dict) -> None:
    qtype = q.get("type")
    if qtype not in KNOWN_TYPES:
        err(where, f"unknown question type {qtype!r} — the importer drops it silently")
        return
    if not isinstance(q.get("question"), str) or not q["question"].strip():
        err(where, "missing 'question' text")

    if qtype == "multiple-choice":
        opts = q.get("options")
        if not isinstance(opts, list):
            err(where, "'options' is missing or not a list")
            return
        if not 2 <= len(opts) <= 6:
            err(where, f"{len(opts)} options — the importer accepts 2..6 and drops the rest")
        if len(set(map(str, opts))) != len(opts):
            err(where, "duplicate options — two identical answers, one is marked wrong")
        correct = q.get("correct")
        # bool is a subclass of int in Python; the importer's typeof check rejects it.
        if isinstance(correct, bool) or not isinstance(correct, int):
            err(where, f"'correct' must be an integer index, got {correct!r} "
                       "— DEADLOCK: no option would ever be accepted")
        elif not 0 <= correct < len(opts):
            err(where, f"'correct' index {correct} is outside 0..{len(opts) - 1} "
                       "— DEADLOCK: no option would ever be accepted")

    elif qtype == "dql-verification":
        for field in ("dql", "buttonText"):
            if not isinstance(q.get(field), str) or not q[field].strip():
                err(where, f"dql-verification missing '{field}'")
        expect = q.get("expect")
        if not isinstance(expect, dict):
            err(where, "dql-verification missing 'expect'")
            return
        op = expect.get("operator")
        if op not in DQL_OPERATORS:
            err(where, f"expect.operator {op!r} is not implemented by the app "
                       f"(valid: {sorted(DQL_OPERATORS)})")
        if op != "not-empty" and expect.get("value") is None:
            err(where, f"expect.operator {op!r} needs a 'value'")
        field = expect.get("field")
        if field and isinstance(q.get("dql"), str) and field not in q["dql"]:
            err(where, f"expect.field {field!r} never appears in the DQL — "
                       "the app would read a non-existent column and always fail")

    elif qtype == "shell-verification":
        if not isinstance(q.get("command"), str):
            err(where, "shell-verification missing 'command'")
        op = (q.get("expect") or {}).get("operator")
        if op not in SHELL_OPERATORS:
            err(where, f"expect.operator {op!r} is not implemented (valid: {sorted(SHELL_OPERATORS)})")

    for forbidden in ("code", "secret", "algorithm", "salt"):
        if qtype == "instructor-code" and forbidden in q:
            err(where, f"instructor-code must not carry '{forbidden}' — it is stripped on import")


def seed_totals(seeds: list[dict]) -> dict[str, dict[str, float]]:
    """Aggregate declared seed data → {event.type: {"count": n, "sum:<attr>": total}}."""
    totals: dict[str, dict[str, float]] = {}
    for seed in seeds:
        for rec in seed.get("records") or []:
            etype = rec.get("event.type")
            count = rec.get("count")
            if not isinstance(etype, str) or not isinstance(count, int) or count < 1:
                continue
            bucket = totals.setdefault(etype, {"count": 0})
            bucket["count"] += count
            for attr, values in (rec.get("cycle") or {}).items():
                if not isinstance(values, list) or not values:
                    continue
                if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
                    continue
                # Values are cycled across `count` records, exactly as the seeder emits them.
                total = sum(values[i % len(values)] for i in range(count))
                bucket[f"sum:{attr}"] = bucket.get(f"sum:{attr}", 0) + total
    return totals


AGG_RE = re.compile(r"(\w+)\s*=\s*(count\(\)|sum\(([\w.]+)\))")
ETYPE_RE = re.compile(r'event\.type\s*==\s*"([^"]+)"')


SEED_SCOPE_FIELD = "dt.enablement.seed.scope"
SEED_SCOPE_VAR = "{{DT_SEED_SCOPE}}"
SEED_PROVIDER_PREFIX = "dynatrace.enablement."

FROM_RE = re.compile(r"from:\s*now\(\)\s*-\s*(\d+)\s*([smhd])")
_UNIT_MINUTES = {"s": 1 / 60, "m": 1, "h": 60, "d": 1440}


def check_seed_scope(where: str, q: dict) -> None:
    """A graded query over seeded data must read only THIS learner's records.

    Every learner on a tenant seeds the same event types into the same provider
    namespace. Without a scope filter, learner B's check passes on learner A's records
    and B never has to press the button at all — a silent false pass, and the same shape
    as the `endsWith(x, "")` trap the app's templateVars.ts documents.

    The scope is stamped server-side by seedLearningBytes from the caller's own identity;
    `{{DT_SEED_SCOPE}}` resolves to the same value in the browser.
    """
    dql = q.get("dql") or ""
    if SEED_SCOPE_FIELD not in dql:
        err(where, f"this byte seeds data, but the query does not filter on "
                   f"{SEED_SCOPE_FIELD} — it would read every learner's records and can "
                   f"pass on someone else's data")
        return
    if SEED_SCOPE_VAR not in dql:
        err(where, f"filters on {SEED_SCOPE_FIELD} but not against {SEED_SCOPE_VAR} — a "
                   f"hard-coded scope matches one person and nobody else")


def check_seed_window(where: str, q: dict, widest_spread: float) -> None:
    """The query's timeframe must cover the whole window the seed spreads records over.

    Records are backdated across `spreadMinutes`. A query with a shorter `from:` simply
    cannot see the older half of its own dataset, so a threshold that the arithmetic says
    is reachable is not reachable in practice — and it fails intermittently, which is
    worse than failing outright.
    """
    dql = q.get("dql") or ""
    m = FROM_RE.search(dql)
    if not m:
        warn(where, "no `from:now()-N` in the query — it will use the default timeframe, "
                    "which is not something this byte controls")
        return
    minutes = int(m.group(1)) * _UNIT_MINUTES[m.group(2)]
    if minutes < widest_spread:
        err(where, f"queries the last {minutes:g}m but the seed spreads records over "
                   f"{widest_spread:g}m — the older records are invisible to this query")


def check_seed_coupling(where: str, q: dict, totals: dict) -> None:
    """A dql-verification threshold must be reachable from the seed declared in the byte."""
    dql = q.get("dql") or ""
    expect = q.get("expect") or {}
    if expect.get("operator") not in {"gte", "gt", "eq"}:
        return
    etypes = ETYPE_RE.findall(dql)
    if len(etypes) != 1:
        return  # multi-type or unfiltered query — not mechanically checkable, leave it
    etype = etypes[0]
    if etype not in totals:
        warn(where, f"queries event.type {etype!r}, which no LAB_SEED in this byte produces "
                    "— the check depends on data this repo does not control")
        return
    field = expect.get("field")
    aggs = {name: (kind, attr) for name, kind, attr in AGG_RE.findall(dql)}
    if field not in aggs:
        return
    kind, attr = aggs[field]
    available = totals[etype]["count"] if kind == "count()" else totals[etype].get(f"sum:{attr}")
    if available is None:
        warn(where, f"cannot compute sum({attr}) from the seed declaration")
        return
    want = float(expect["value"])
    op = expect["operator"]
    if op == "eq":
        err(where, "an exact-equality threshold over seeded data is not stable: a learner "
                   "who reloads the demo data after part of it has aged out gets a top-up, "
                   "so the count inside the query window can exceed the declared total. "
                   "Use gte.")
        return
    ok = (available >= want) if op == "gte" else (available > want)
    if not ok:
        err(where, f"seed produces {field}={available:g} for {etype}, but the check requires "
                   f"{op} {want:g} — this question can never pass")


def main() -> int:
    nav = load_nav()
    check_titles(nav)

    for title, entries in nav:
        if not entries:
            err("mkdocs.yaml", f"training {title!r} has no pages")
            continue
        seeds_in_byte: list[dict] = []
        questions_in_byte: list[tuple[str, dict]] = []

        for idx, (step_title, rel) in enumerate(entries):
            path = DOCS / rel
            if not path.is_file():
                err("mkdocs.yaml", f"{title!r} → {step_title!r} points at missing file {rel}")
                continue
            rp = str(path.relative_to(ROOT))
            text = path.read_text()
            check_page_h1(path)

            if idx == 0 and not text.lstrip("﻿").startswith("---"):
                err(rp, f"first page of {title!r} has no front matter — the catalog card "
                        "will show no description, tags, difficulty or duration")

            for i, seed in parse_blocks(SEED_RE, text, rp, "seed"):
                w = f"{rp}#seed{i}"
                if not isinstance(seed.get("dataset"), str):
                    err(w, "LAB_SEED missing 'dataset'")
                provider = seed.get("provider")
                if not isinstance(provider, str):
                    err(w, "LAB_SEED missing 'provider' — seed data must be namespaced")
                elif not provider.startswith(SEED_PROVIDER_PREFIX):
                    err(w, f"provider {provider!r} is outside the reserved "
                           f"{SEED_PROVIDER_PREFIX!r} namespace. seedLearningBytes refuses "
                           "it at ingest, so this byte's button would fail for every learner")
                spread = seed.get("spreadMinutes", 60)
                if not isinstance(spread, int) or not 1 <= spread <= 1440:
                    err(w, f"spreadMinutes {spread!r} outside 1..1440")
                recs = seed.get("records")
                if not isinstance(recs, list) or not recs:
                    err(w, "LAB_SEED has no 'records'")
                    continue
                total = 0
                for r in recs:
                    if not isinstance(r.get("event.type"), str):
                        err(w, "a seed record has no 'event.type'")
                    n = r.get("count")
                    if not isinstance(n, int) or not 1 <= n <= 500:
                        err(w, f"seed record count {n!r} outside 1..500 — keep tenants uncluttered")
                    else:
                        total += n
                if total > 1000:
                    err(w, f"{total} records per seed run is too many for a shared tenant")
                seeds_in_byte.append(seed)

            for i, q in parse_blocks(QUESTION_RE, text, rp, "q"):
                w = f"{rp}#q{i}"
                check_question(w, q)
                questions_in_byte.append((w, q))

        totals = seed_totals(seeds_in_byte)
        widest_spread = max(
            (s.get("spreadMinutes", 60) for s in seeds_in_byte
             if isinstance(s.get("spreadMinutes", 60), int)),
            default=0,
        )
        graded_dql = 0
        for w, q in questions_in_byte:
            if q.get("type") != "dql-verification":
                continue
            graded_dql += 1
            check_seed_coupling(w, q, totals)
            if seeds_in_byte:
                check_seed_scope(w, q)
                check_seed_window(w, q, widest_spread)
        if seeds_in_byte and graded_dql == 0:
            warn(f"{title}", "declares a LAB_SEED but grades no dql-verification against it "
                             "— it writes records into every learner's tenant for nothing")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(nav)} trainings checked — {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
