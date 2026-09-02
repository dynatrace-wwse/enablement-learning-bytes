# Defining SLOs in Dynatrace

!!! warning "Illustrative SLI expressions — nothing is configured or seeded"
    The metric expression and DQL below are worked examples of how an SLI is built. They
    read `dt.service.request.*`, which exists only where services are monitored, and this
    byte creates no SLO and writes no sample data. Read them for the shape of the
    calculation; run them on a tenant with real service traffic.

Dynatrace SLOs combine an SLI metric expression with a target and evaluation window.

## SLO Configuration Components

1. **Name & Description**: Clear, actionable naming (e.g., "Payment API Availability")
2. **SLI Definition**: A DQL metric expression or built-in metric
3. **Target**: The percentage target (e.g., 99.9%)
4. **Warning**: An early-warning threshold (e.g., 99.95%)
5. **Evaluation Window**: Rolling timeframe (7d, 14d, 30d)

## SLI via Metric Expression

```
(100) * (
  builtin:service.errors.server.successCount:splitBy()
  /
  builtin:service.requestCount.server:splitBy()
)
```

## SLI via DQL

```dql
timeseries {
  total  = sum(dt.service.request.count),
  failed = sum(dt.service.request.failure_count)
}, from:now()-30d
| fieldsAdd sli = 100.0 * (arraySum(total) - arraySum(failed)) / arraySum(total)
```

> **`sum()`, not `avg()`.** `dt.service.request.count` is a counter. Averaging it gives
> you "requests per interval", and a ratio of two averages is only equal to the ratio of
> the underlying totals when every bucket carries the same traffic — which is exactly
> what never happens. Averaging silently over-weights your quiet 3 a.m. buckets against
> your busy midday ones, so the SLI reads better than reality during an incident that
> starts at peak. Sum the numerator and denominator, then divide once.

Guard the empty window too — a service with no traffic divides by zero:

```dql
timeseries {
  total  = sum(dt.service.request.count),
  failed = sum(dt.service.request.failure_count)
}, from:now()-30d
| fieldsAdd reqs = arraySum(total), errs = arraySum(failed)
| fieldsAdd sli = if(reqs > 0, 100.0 * (reqs - errs) / reqs, else: 100.0)
```

## Choosing the Right Window

| Window | Best For |
|--------|----------|
| 7 days | New services, rapid iteration |
| 14 days | Services with weekly patterns |
| 30 days | Mature, stable services |

<!-- LAB_QUESTION
type: multiple-choice
question: What is the purpose of the 'Warning' threshold in an SLO configuration?
options:
  - To trigger immediate incident response
  - To provide early indication that the SLO might be breached if the trend continues
  - To automatically scale up infrastructure
  - To block deployments
correct: 1
explanation: The warning threshold is set above the SLO target to give teams advance notice. For example, a 99.95% warning on a 99.9% SLO triggers before the actual target is breached.
-->
