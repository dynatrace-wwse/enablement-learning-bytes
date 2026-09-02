---
description: Learn to query, filter, and analyze log data using DQL. Covers basic log exploration, filtering by severity, and extracting patterns from unstructured logs.
tags:
  - observability
  - logs
  - dql
  - beginner
difficulty: beginner
duration: 8
---

> **Scenario** — Your team has deployed a new microservice and users are reporting intermittent errors. You need to investigate the logs to find the root cause.
>
> **Your goal:** Use DQL to explore logs, identify error patterns, and pinpoint the failing component.

# Introduction to DQL Log Queries

!!! warning "These queries read your tenant's own logs — this byte seeds no sample data"
    The DQL here is real and copy-pasteable, but `fetch logs` reads whatever log data
    *your* tenant already holds. On a tenant with no log ingest configured every query
    below returns **zero rows** — and that is the correct answer, not a fault.

    Nothing is written to your tenant by this byte. If you want rows to look at, run these
    against a tenant that has log ingest enabled, or narrow them to a service you know
    is reporting.

Dynatrace Query Language (DQL) is the primary way to explore observability data stored in Grail.

## Basic Log Query

The simplest log query fetches recent log entries:

```dql
fetch logs
| limit 10
```

This returns the 10 most recent log records. Each record contains fields like:
- `timestamp` — when the log was written
- `content` — the log message
- `status` — severity level (INFO, WARN, ERROR, etc.)
- `dt.entity.host` — the host that produced the log

## Filtering Logs

You can narrow results using `filter`:

```dql
fetch logs
| filter status == "ERROR"
| limit 20
```

> **Tip**: Always specify a time range in production queries to avoid scanning too much data.

<!-- LAB_QUESTION
type: multiple-choice
question: Which DQL command is used to narrow log results to only error-level entries?
options:
  - summarize
  - filter
  - sort
  - parse
correct: 1
explanation: The `filter` command restricts results to rows matching a condition, like `filter status == "ERROR"`.
-->
