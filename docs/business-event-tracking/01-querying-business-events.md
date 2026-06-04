# Querying Business Events

Business events are queried with DQL using `fetch bizevents`.

## Basic Query

```dql
fetch bizevents
| filter event.type == "com.shop.purchase.complete"
| sort timestamp desc
| limit 20
```

## Funnel Analysis

Track conversion through stages:

```dql
fetch bizevents
| filter event.type == "com.shop.cart.add" or event.type == "com.shop.checkout.start" or event.type == "com.shop.purchase.complete"
| summarize eventCount = count(), by:{event.type}
```

## Revenue Calculation

```dql
fetch bizevents
| filter event.type == "com.shop.purchase.complete"
| summarize totalRevenue = sum(total), orderCount = count()
```

> **Tip**: Use `makeTimeseries` with business events to spot trends in conversion rates over time.

<!-- LAB_QUESTION
type: multiple-choice
question: Which DQL data source command fetches business events?
options:
  - fetch logs
  - fetch events
  - fetch bizevents
  - fetch metrics
correct: 2
explanation: '`fetch bizevents` is the DQL command to query business events stored in Grail.'
-->
