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

OpenPipeline is configured via Settings:
- Navigate to **Settings → OpenPipeline → Business Events**
- Add processing rules with matchers and processors
- Test with sample events before activating

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
