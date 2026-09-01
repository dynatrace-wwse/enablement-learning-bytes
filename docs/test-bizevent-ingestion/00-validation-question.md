---
description: A five-minute self-check that this tenant can ingest a business event and read it back with DQL, and that you can tell a local write apart from one routed to the central tenant. Retakeable.
tags:
  - test
  - bizevents
  - dql
difficulty: beginner
duration: 5
---

> **Scenario** — You have just installed or upgraded the Enablement app on a tenant and
> want to confirm the telemetry path works end to end before a cohort arrives.
>
> **Your goal:** Ingest a business event into this tenant, read it back with DQL, and
> know which tenant your own completion events are being written to.

# BizEvent Ingestion Validator

This byte checks two different things, and it is worth being precise about which is which.

## 1. Can this tenant ingest and query a business event?

Press the button. It ingests a handful of marker events into **this** tenant, through the
same business-events ingest path the app uses for its own telemetry.

<!-- LAB_SEED
dataset: ingest-probe
version: 1
buttonText: Ingest a probe event
provider: dynatrace.enablement.learningbytes
spreadMinutes: 5
records:
  - event.type: com.dynatrace.enablement.seed.ingest.probe
    count: 5
    attributes:
      probe: bizevent-ingestion-validator
-->

Now read it back:

```dql
fetch bizevents, from:now()-1h
| filter event.provider == "dynatrace.enablement.learningbytes"
| filter event.type == "com.dynatrace.enablement.seed.ingest.probe"
| sort timestamp desc
| limit 10
```

<!-- LAB_QUESTION
type: dql-verification
question: Confirm the probe events reached this tenant's Grail.
buttonText: Verify ingestion
dql: |
  fetch bizevents, from:now()-1h
  | filter event.provider == "dynatrace.enablement.learningbytes"
  | filter event.type == "com.dynatrace.enablement.seed.ingest.probe"
  | summarize probes = count()
expect:
  operator: gte
  field: probes
  value: 1
hint: Press "Ingest a probe event" above first. Ingestion is not instantaneous — if the
  count is 0, wait a few seconds and verify again.
explanation: The probe is written with the app's own AppEngine identity via the business
  events ingest API, so a passing check proves this tenant accepts and indexes bizevents.
-->

## 2. Where do *your* completion events go?

This is the part that surprises people, and the reason this byte used to give a confusing
answer.

When you finish a training, the app emits
`com.dynatrace.enablement.training.completed`. Where that lands depends on configuration:

| Tenant configuration | Where training events are written |
|---|---|
| **remote-grail configured** (the normal case — the app points at a central tenant) | The **central** tenant only |
| **remote-grail not configured** (e.g. the app installed *on* the central tenant) | This tenant, locally |

Exactly one write happens either way — that is deliberate, so a learner is never counted
twice. The consequence for you: on a tenant with remote-grail configured, this query is
**supposed** to return nothing, and that is not a fault:

```dql
fetch bizevents, from:now()-1h
| filter event.type == "com.dynatrace.enablement.training.completed"
| sort timestamp desc
| limit 5
```

> **The lesson generalises.** "The query returned no rows" and "the data was never
> written" are different statements. Before you go hunting for a broken producer, confirm
> you are querying the tenant the producer actually writes to.

<!-- LAB_QUESTION
type: multiple-choice
question: Which DQL data source contains ingested business events?
options:
  - fetch logs
  - fetch bizevents
  - fetch events
  - fetch metrics
correct: 1
explanation: '`fetch bizevents` is the Grail data object for business events ingested via
  the business events API.'
-->

<!-- LAB_QUESTION
type: multiple-choice
question: You complete a training on a tenant that has remote-grail configured, then query this tenant for `com.dynatrace.enablement.training.completed` and get zero rows. What has happened?
options:
  - The completion event failed to send and should be retried
  - The event was routed to the central tenant, which is the configured behaviour
  - Business events take 24 hours to become queryable
  - The training must be completed twice before an event is emitted
correct: 1
hint: Re-read the routing table above. How many writes happen per completion?
explanation: With remote-grail configured, training events are written to the central
  tenant only — exactly one write per event, so learners are never double-counted. A local
  query correctly returns nothing.
-->
