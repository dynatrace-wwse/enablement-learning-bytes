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

## Querying Pod Restarts

```dql
fetch dt.entity.cloud_application
| fields entity.name, lifetime
| filterOut isNull(entity.name)
| sort entity.name asc
| limit 10
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
