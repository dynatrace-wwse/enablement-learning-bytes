# Problem Correlation & Root Cause

When multiple anomalies occur, Davis groups related symptoms into a single **Problem** and identifies the root cause.

## Problem Lifecycle

1. **Detection**: Individual anomalies detected on entities
2. **Correlation**: Davis groups related anomalies using topology (Smartscape)
3. **Root Cause Analysis**: Davis traces the dependency chain to find the origin
4. **Resolution**: Problem closes when all symptoms resolve

## Correlation Logic

Davis uses Smartscape topology to understand:
- Which services call which services
- Which services run on which hosts
- Which processes belong to which services

If `Service A` calls `Service B` and both show response time anomalies, Davis correlates them into one Problem and identifies which is the cause vs. the effect.

## Root Cause Types

| Root Cause | Example |
|------------|---------|
| **Deployment** | New version introduced a bug |
| **Resource saturation** | Disk full on database host |
| **Infrastructure** | Cloud provider availability zone issue |
| **External dependency** | Third-party API degradation |
| **Traffic spike** | Unexpected load increase |

<!-- LAB_QUESTION
type: multiple-choice
question: What technology does Davis use to correlate related anomalies into a single Problem?
options:
  - Log pattern matching
  - Smartscape topology (entity relationships and dependencies)
  - Alert rule grouping configured by administrators
  - Timestamp proximity (anomalies within 5 minutes of each other)
correct: 1
explanation: Davis uses Smartscape — Dynatrace's real-time topology map of all entity relationships and dependencies — to understand which anomalies are causally related.
-->

<!-- LAB_QUESTION
type: multiple-choice
question: Service A calls Service B. Both show increased response times. Service B also shows increased failure rate. Where is the likely root cause?
options:
  - Service A (the caller)
  - Service B (the dependency)
  - Both equally
  - Neither — it's a network issue
correct: 1
explanation: Service B shows both failure rate and response time anomalies. Service A's slowdown is a downstream effect of calling the degraded Service B. Root cause is at Service B.
-->
