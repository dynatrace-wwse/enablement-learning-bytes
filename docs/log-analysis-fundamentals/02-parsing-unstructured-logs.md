# Parsing Unstructured Logs

!!! warning "Reads your tenant's own logs — nothing is seeded"
    The `parse` example expects log lines shaped like `GET /api/users 200 45ms`. On a
    tenant whose logs look different — or which has no logs at all — `isNotNull(httpStatus)`
    filters everything out and you get zero rows. That is the pattern not matching, not an
    error.

Many logs contain useful data embedded in free-text messages. DQL's `parse` command extracts structured fields.

## Example: Parsing HTTP Status Codes

Given a log message like: `GET /api/users 200 45ms`

```dql
fetch logs
| parse content, "LD:method ' ' LD:path ' ' INT:httpStatus ' ' INT:duration 'ms'"
| filter isNotNull(httpStatus)
| summarize count(), by:{httpStatus}
```

## Key Parse Patterns

DQL's `parse` uses **DPL** — Dynatrace Pattern Language. These are the matchers you will
reach for first:

| Matcher | Full name | Matches |
|---------|-----------|---------|
| `LD` | `LDATA` — **line data** | Any characters *within a single line* |
| `DATA` | multiline data | Any characters, newlines included |
| `INT` | `INTEGER` | Integral numbers |
| `IPADDR` | — | IPv4 and IPv6 addresses |
| `TIMESTAMP` | `TIME` | Time and date — needs a format, e.g. `TIMESTAMP('yyyy-MM-dd')` |
| `SPACE` / `BLANK` | — | Whitespace |

`LD` is bounded by the *next* thing in the pattern, which is why
`LD:method ' ' LD:path` splits cleanly on the spaces: each `LD` stops as soon as the
following literal can match. You can bound it explicitly too — `LD{1,64}:path` refuses to
run away over a pathological line, which is worth doing on high-volume log pipelines.

> **Best Practice**: Use `parse` early in the pipeline so downstream filters and summaries can use the extracted fields.

<!-- LAB_QUESTION
type: multiple-choice
question: What is the DQL pattern `LD` used for in a parse command?
options:
  - Matching log dates
  - Matching any characters within a single line
  - Matching log levels
  - Matching line delimiters
correct: 1
hint: LD is short for LDATA. Think about the one thing it will not cross.
explanation: '`LD` is the abbreviation of `LDATA` — the *line data* matcher. It matches any
  character except a line break, and stops as soon as the next element of the pattern can
  match. Use `DATA` when you deliberately need to cross newlines.'
-->
