# OpenPipeline Processing

OpenPipeline lets you transform and enrich business events before they're stored.

## Pipeline Capabilities

- **Parsing**: Extract structured fields from raw event data
- **Enrichment**: Add context (e.g., customer segment, region)
- **Filtering**: Drop irrelevant events to save storage
- **Routing**: Send events to different buckets based on rules

## Example Pipeline Rule

A processing rule might:
1. Parse the `paymentMethod` field
2. Enrich with `customerTier` from a lookup table
3. Drop test transactions (where `email` contains `@test.com`)

## Configuration

OpenPipeline has its own app. Open **OpenPipeline** from the Dynatrace launcher and pick
the **Business events** data source (in older builds the same configuration sits under
Settings → Process and contextualize → OpenPipeline).

- Each data source has an ordered set of **pipelines**; a **dynamic route** decides which
  pipeline an incoming record enters, and records that match no route take the default.
- Inside a pipeline you add **processors** — parse, add fields, filter — and Dynatrace
  lets you **test them against a sample record before you activate**. Use that. A
  processing rule is applied at ingest, and ingest is not replayable.

## Bucket assignment — the operationally important part

A pipeline can also **assign a bucket**, and a bucket carries its own retention. This is
how you stop business events from becoming an unbounded cost:

- Send high-value, low-volume events (purchases, signups) to a long-retention bucket.
- Send high-volume, low-value events (every cart interaction) to a short one.
- Send synthetic, test, and demo traffic to a short-retention bucket so it ages out by
  itself instead of being curated by hand.

Which bucket a record actually landed in is readable as `dt.system.bucket`, so you can
confirm your routing did what you intended rather than assuming it:

```dql
fetch bizevents, from:now()-24h
| summarize records = count(), by:{dt.system.bucket}
| sort records desc
```

Unrouted business events land in `default_bizevents`. If you built a routing rule and this
query still shows everything in `default_bizevents`, the rule did not match — check the
matcher before you check the processor.

> **Best Practice**: Keep pipelines simple. Prefer doing complex transformations at query time (DQL) rather than at ingestion time.

<!-- LAB_QUESTION
type: multiple-choice
question: What is the primary purpose of OpenPipeline for business events?
options:
  - Sending alerts when events match conditions
  - Transforming and enriching events before storage
  - Visualizing events in dashboards
  - Backing up events to external storage
correct: 1
explanation: OpenPipeline processes events at ingestion time — parsing, enriching, filtering, and routing before they're stored in Grail.
-->
