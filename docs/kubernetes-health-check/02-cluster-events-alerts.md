# Cluster Events & Alerts

Kubernetes events provide a running log of cluster-level activities. They're essential for troubleshooting.

## Important Event Types

- **Normal**: Routine operations (pod scheduled, image pulled, container started)
- **Warning**: Issues requiring attention (failed scheduling, probe failures, evictions)

## Querying Events in Dynatrace

```dql
fetch events
| filter event.kind == "KUBERNETES_EVENT"
| filter event.type == "Warning"
| sort timestamp desc
| limit 50
```

## Setting Up Alerts

Configure Davis anomaly detection for:
- Pod restart rate exceeding threshold
- Node not ready conditions
- Persistent volume claim pending
- Resource quota exhaustion

<!-- LAB_QUESTION
type: multiple-choice
question: Which Kubernetes event type indicates an issue that may require investigation?
options:
  - Normal
  - Warning
  - Critical
  - Debug
correct: 1
explanation: 'Kubernetes has two event types: Normal (routine operations) and Warning (potential issues). There is no Critical or Debug event type in Kubernetes.'
-->

<!-- LAB_QUESTION
type: multiple-choice
question: You see a 'FailedScheduling' event for a pod. What is the most likely cause?
options:
  - The pod's container image doesn't exist
  - The pod's liveness probe is failing
  - The cluster lacks sufficient resources to place the pod
  - The pod's service account is missing
correct: 2
explanation: FailedScheduling means the scheduler cannot find a node with enough available CPU/memory (or matching affinity/tolerations) to run the pod.
-->
