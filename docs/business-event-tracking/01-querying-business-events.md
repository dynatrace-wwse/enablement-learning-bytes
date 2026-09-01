# Querying Business Events

Business events are queried with DQL using `fetch bizevents`.

## Load the demo dataset

The queries below are graded, so they need data. Press **Load demo data** to ingest a
small, fixed set of business events into *this* tenant. It is bounded (77 records),
idempotent, and every record carries `event.provider = "dynatrace.enablement.learningbytes"`
so it can never be confused with your production traffic.

Every record is also stamped with **your own** seed scope, and each query below filters
on it with `{{DT_SEED_SCOPE}}`. That is not decoration: on a shared tenant your classmates
are seeding the same event types into the same provider at the same moment. Without the
scope filter your "40 cart additions" would be everyone's cart additions, and the check
would pass whether or not you ever pressed the button.

<!-- LAB_SEED
dataset: shop-funnel
version: 1
buttonText: Load demo data
provider: dynatrace.enablement.learningbytes
spreadMinutes: 90
records:
  - event.type: com.shop.cart.add
    count: 40
    attributes:
      storefront: learning-bytes-demo
    cycle:
      productId: [SKU-1001, SKU-1002, SKU-1003, SKU-1004, SKU-1005]
      quantity: [1, 2, 1, 3, 1]
      price: [19.99, 49.50, 12.00, 149.00, 8.75]
  - event.type: com.shop.checkout.start
    count: 25
    attributes:
      storefront: learning-bytes-demo
    cycle:
      cartTotal: [39.98, 99.00, 24.00, 149.00, 17.50]
      itemCount: [2, 2, 2, 1, 2]
  - event.type: com.shop.purchase.complete
    count: 12
    attributes:
      storefront: learning-bytes-demo
    cycle:
      total: [25.00, 50.00, 75.00, 100.00, 125.00, 150.00, 75.00, 100.00, 125.00, 150.00, 125.00, 100.00]
      paymentMethod: [card, card, paypal, card, invoice, card, paypal, card, card, invoice, card, paypal]
-->

That dataset is deliberately a funnel that *leaks*: 40 cart additions become 25 checkouts
become 12 purchases. A 30% cart-to-purchase conversion is the kind of number a business
stakeholder actually asks you about, and it is the reason business events exist.

## Basic Query

```dql
fetch bizevents, from:now()-2h
| filter event.provider == "dynatrace.enablement.learningbytes"
| filter dt.enablement.seed.scope == "{{DT_SEED_SCOPE}}"
| filter event.type == "com.shop.purchase.complete"
| sort timestamp desc
| limit 20
```

> **Always scope by `event.provider`.** On a real tenant `fetch bizevents` is a firehose
> of every ingest source you have. Filtering on the provider is what makes a query
> reproducible — and what stops a demo query from quietly reading production revenue.
>
> `dt.enablement.seed.scope` narrows it one step further, to the records *you* seeded.
> The general lesson outlives this lab: a query you intend to be about one subject should
> say so in a filter, rather than relying on being the only person generating that data.

## Funnel Analysis

Track conversion through stages. Use `in()` rather than a chain of `or`s — it is shorter,
and it does not silently change meaning when someone adds a fourth stage:

```dql
fetch bizevents, from:now()-2h
| filter event.provider == "dynatrace.enablement.learningbytes"
| filter dt.enablement.seed.scope == "{{DT_SEED_SCOPE}}"
| filter in(event.type, {"com.shop.cart.add",
                         "com.shop.checkout.start",
                         "com.shop.purchase.complete"})
| summarize eventCount = count(), by:{event.type}
| sort eventCount desc
```

<!-- LAB_QUESTION
type: dql-verification
question: Run the funnel query. How many `com.shop.cart.add` events did the demo dataset produce?
buttonText: Run the funnel query
dql: |
  fetch bizevents, from:now()-2h
  | filter event.provider == "dynatrace.enablement.learningbytes"
  | filter dt.enablement.seed.scope == "{{DT_SEED_SCOPE}}"
  | filter event.type == "com.shop.cart.add"
  | summarize cartAdds = count()
expect:
  operator: gte
  field: cartAdds
  value: 40
hint: Load the demo data first — the button above this section.
explanation: The dataset ingests exactly 40 `com.shop.cart.add` records per run, into your
  own seed scope. The check uses `gte`, not `eq`, because reloading the demo data after part
  of it has aged out tops the set up rather than replacing it.
-->

## Revenue Calculation

`summarize` can compute several aggregates in one pass:

```dql
fetch bizevents, from:now()-2h
| filter event.provider == "dynatrace.enablement.learningbytes"
| filter dt.enablement.seed.scope == "{{DT_SEED_SCOPE}}"
| filter event.type == "com.shop.purchase.complete"
| summarize totalRevenue = sum(total),
            orderCount   = count(),
            avgOrder     = avg(total)
```

The 12 seeded orders sum to exactly **1200.00**, so `avgOrder` is 100.00.

<!-- LAB_QUESTION
type: dql-verification
question: Run the revenue query. Does the demo dataset report at least 1200.00 in completed revenue?
buttonText: Verify revenue
dql: |
  fetch bizevents, from:now()-2h
  | filter event.provider == "dynatrace.enablement.learningbytes"
  | filter dt.enablement.seed.scope == "{{DT_SEED_SCOPE}}"
  | filter event.type == "com.shop.purchase.complete"
  | summarize totalRevenue = sum(total)
expect:
  operator: gte
  field: totalRevenue
  value: 1200
hint: If this returns nothing, the demo data has not been loaded — or more than 2 hours
  have passed since you loaded it, and the `from:now()-2h` window has moved past it.
explanation: '`sum(total)` over the 12 seeded `com.shop.purchase.complete` records is 1200.00.
  Note the timeframe is part of the query: `from:now()-2h` is what makes this reproducible.'
-->

## Trending the Funnel

```dql
fetch bizevents, from:now()-2h
| filter event.provider == "dynatrace.enablement.learningbytes"
| filter dt.enablement.seed.scope == "{{DT_SEED_SCOPE}}"
| makeTimeseries count(), by:{event.type}, interval:10m
```

> **Tip**: `makeTimeseries` turns *event records* into a series. `timeseries` reads
> *metrics*. Business events are records, so after `fetch bizevents` you want
> `makeTimeseries`; reach for `timeseries` only once the data is a metric.

<!-- LAB_QUESTION
type: multiple-choice
question: Which DQL data source command fetches business events?
options:
  - fetch logs
  - fetch events
  - fetch bizevents
  - fetch metrics
correct: 2
explanation: '`fetch bizevents` is the DQL command to query business events stored in Grail.
  `fetch events` returns Davis and platform events — a different data object entirely.'
-->

<!-- LAB_QUESTION
type: multiple-choice
question: Your funnel query returns zero rows, but you know the events were ingested. Which is the LEAST likely explanation?
options:
  - The query timeframe does not cover when the events were ingested
  - The `event.provider` or `event.type` string does not match exactly
  - DQL returned an error that the UI did not display
  - The events landed in a different bucket than the one being queried
correct: 2
hint: Think about what DQL does when you filter on a value that matches nothing.
explanation: A DQL filter that matches nothing is not an error — the query succeeds and
  returns zero rows. That is precisely why "no results" is so often a timeframe, a typo,
  or a bucket problem rather than a missing-data problem.
-->
