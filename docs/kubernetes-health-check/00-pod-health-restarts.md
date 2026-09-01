---
description: Assess your knowledge of monitoring Kubernetes clusters with Dynatrace. Covers pod health, resource utilization, and cluster events.
tags:
  - cloud-ops
  - kubernetes
  - infrastructure
difficulty: intermediate
duration: 10
---

> **Scenario** — A critical production cluster is showing degraded performance. Pods are restarting and resource limits are being hit. Your job is to identify and triage the issues.
>
> **Your goal:** Demonstrate your ability to diagnose Kubernetes cluster issues using Dynatrace observability data.

# Pod Health & Restarts

Monitoring pod health is essential for Kubernetes operations. Key metrics include:

- **Pod phase**: Running, Pending, Failed, Succeeded, Unknown
- **Restart count**: High restarts indicate crashlooping containers
- **Ready condition**: Whether all containers in the pod are ready to serve traffic

## Querying Restarts

Restarts are a **metric**, not an entity property, so this is a `timeseries` query — not
a `fetch`:

```dql
timeseries restarts = sum(dt.kubernetes.container.restarts),
           by:{k8s.cluster.name, k8s.namespace.name, k8s.workload.name},
           from:now()-6h
| fieldsAdd totalRestarts = arraySum(restarts)
| filter totalRestarts > 0
| sort totalRestarts desc
| limit 20
```

Two things an experienced operator reads into that query:

- **`dt.kubernetes.container.restarts` is measured per container, and there is no
  pod-level restart metric.** A pod with an app container and a sidecar reports two
  series. Summing to `k8s.workload.name`, as above, is how you get the number a human
  actually means when they say "this deployment is restarting".
- **It is a counter.** `sum()` over the window gives you restarts *in that window*.
  Do not read a single data point as "total restarts ever" — and be aware that a gap in
  the series (agent restart, node drain) can make a naive delta look like a spike.

To see which workloads are restarting *right now* rather than over the window, keep the
series and look at its shape instead of collapsing it:

```dql
timeseries restarts = sum(dt.kubernetes.container.restarts),
           by:{k8s.namespace.name, k8s.workload.name},
           from:now()-2h, interval:5m
```

## Common Causes of Pod Restarts

1. **OOMKilled** — Container exceeded memory limits
2. **CrashLoopBackOff** — Application crashes on startup repeatedly
3. **Liveness probe failure** — Health check endpoint not responding
4. **Image pull errors** — Container image not accessible

<!-- LAB_QUESTION
type: multiple-choice
question: A pod has restarted 47 times in the last hour. Which is the MOST likely cause?
options:
  - Scheduled maintenance window
  - CrashLoopBackOff due to application startup failure
  - Normal rolling update behavior
  - DNS resolution delay
correct: 1
explanation: 47 restarts/hour strongly indicates CrashLoopBackOff — the container starts, crashes, and Kubernetes keeps restarting it with exponential backoff.
-->

<!-- LAB_QUESTION
type: multiple-choice
question: What Kubernetes condition indicates a pod is ready to receive traffic?
options:
  - PodScheduled
  - Initialized
  - Ready
  - ContainersReady
correct: 2
hint: This is the top-level condition that gates Service endpoint inclusion.
explanation: The `Ready` condition aggregates all readiness checks. A pod only receives Service traffic when Ready=True.
-->
