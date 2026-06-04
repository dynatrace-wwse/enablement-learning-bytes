> **Scenario** — Multiple alerts are firing across your environment. Davis AI has identified the root cause and grouped related symptoms. You need to interpret the findings.
>
> **Your goal:** Demonstrate understanding of Davis AI's anomaly detection, problem correlation, and root cause analysis.

# Davis AI Anomaly Detection

Davis AI uses machine learning to establish baselines and detect deviations — no manual threshold configuration required.

## How Davis Detects Anomalies

1. **Baseline learning**: Davis continuously learns normal patterns (seasonality, trends)
2. **Multi-dimensional analysis**: Considers multiple signals simultaneously
3. **Contextual evaluation**: Accounts for deployments, config changes, load variations
4. **Automatic sensitivity**: Adapts detection sensitivity per entity and metric

## Types of Anomalies

| Type | Description | Example |
|------|-------------|---------|
| **Response time** | Latency exceeds learned baseline | P95 jumped from 200ms to 2s |
| **Failure rate** | Error ratio exceeds normal | Error rate went from 0.1% to 5% |
| **Load** | Traffic pattern deviates | Request count dropped 80% |
| **Resource** | CPU, memory, disk anomaly | CPU saturated at 98% for 10 min |
| **Availability** | Process/host unreachable | Service instance crashed |

## Key Principle

> Davis doesn't alert on every metric crossing a static threshold. It alerts when behavior **significantly deviates** from the learned baseline in a way that's likely to impact users.

<!-- LAB_QUESTION
type: multiple-choice
question: How does Davis AI determine what is 'abnormal' behavior for a service?
options:
  - It uses static thresholds defined by the administrator
  - It compares against industry benchmarks
  - It continuously learns baseline patterns and detects significant deviations
  - It only reacts to user-reported incidents
correct: 2
explanation: Davis uses machine learning to continuously establish baselines per entity and metric, then detects statistically significant deviations.
-->
