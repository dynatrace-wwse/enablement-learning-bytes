> **Scenario** — This training exists solely to test biz event ingestion.
>
> **Your goal:** Complete it, then verify a `com.dynatrace.enablement.training.completed` event appears in Grail.

# BizEvent Ingestion Validator

This training emits a `com.dynatrace.enablement.training.completed` biz event to local Grail when completed.

After finishing, run the following DQL to confirm ingestion:

```dql
fetch bizevents, from: now()-1h
| filter event.type == "com.dynatrace.enablement.training.completed"
| sort timestamp desc
| limit 5
```

Answer the question below and click **Next** to complete.

<!-- LAB_QUESTION
type: multiple-choice
question: Which DQL data source contains ingested biz events?
options:
  - fetch logs
  - fetch bizevents
  - fetch events
  - fetch metrics
correct: 1
explanation: '`fetch bizevents` is the Grail data source for business events ingested via the bizevents API.'
-->
