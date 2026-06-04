# Counting and Aggregating Logs

Once you know how to filter, the next step is summarizing patterns.

## Counting by Status

```dql
fetch logs
| summarize logCount = count(), by:{status}
| sort logCount desc
```

This groups logs by severity level and counts each group.

## Counting Over Time

Use `makeTimeseries` to see how log volume changes:

```dql
fetch logs
| makeTimeseries count(), by:{status}, interval:5m
```

This creates a time series with 5-minute buckets, split by log status.

## Finding Top Error Sources by Namespace

```dql
fetch logs
| filter status == "ERROR"
| summarize errorCount = count(), by:{k8s.namespace.name}
| sort errorCount desc
| limit 5
```

<!-- LAB_QUESTION
type: multiple-choice
question: What DQL command groups records and computes aggregate values like count()?
options:
  - filter
  - parse
  - summarize
  - fields
correct: 2
explanation: '`summarize` groups records by specified fields and computes aggregations like count(), avg(), sum().'
-->

<!-- LAB_QUESTION
type: multiple-choice
question: Which DQL function creates a time-bucketed series from log data?
options:
  - makeTimeseries
  - timechart
  - bucket
  - timeframe
correct: 0
explanation: '`makeTimeseries` creates time-bucketed series, useful for visualizing trends over time.'
-->
