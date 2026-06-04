# Parsing Unstructured Logs

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

| Pattern | Matches |
|---------|---------|
| `LD` | Any characters (lazy) |
| `INT` | Integer value |
| `IPADDR` | IP address |
| `TIMESTAMP` | Date/time |

> **Best Practice**: Use `parse` early in the pipeline so downstream filters and summaries can use the extracted fields.

<!-- LAB_QUESTION
type: multiple-choice
question: What is the DQL pattern `LD` used for in a parse command?
options:
  - Matching log dates
  - Matching any characters (lazy match)
  - Matching log levels
  - Matching line delimiters
correct: 1
hint: LD stands for 'Lazy Data' — it matches any sequence of characters, as few as possible.
explanation: '`LD` (Lazy Data) matches any characters with a lazy (non-greedy) strategy, stopping at the next matching pattern.'
-->
