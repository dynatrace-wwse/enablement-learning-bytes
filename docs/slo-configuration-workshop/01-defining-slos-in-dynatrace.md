# Defining SLOs in Dynatrace

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
  total = avg(dt.service.request.count),
  errors = avg(dt.service.request.failure_count)
}
| fieldsAdd sli = 100.0 - arrayAvg(errors) / arrayAvg(total) * 100
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
