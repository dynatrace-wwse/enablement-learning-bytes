# Cluster Events & Alerts

!!! warning "Reads live Kubernetes events — this byte seeds no sample data"
    `event.provider == "KUBERNETES_EVENT"` selects events the Dynatrace Operator ingests
    from a real cluster. That provider value is reserved by the ingest path, so nothing can
    be seeded to imitate it.

    The queries below are the real ones and return **zero rows** on a tenant with no
    monitored cluster. Note that this is itself the lesson of this page: a filter matching
    nothing is not an error.

Kubernetes events provide a running log of cluster-level activities. They're essential for troubleshooting.

## Important Event Types

- **Normal**: Routine operations (pod scheduled, image pulled, container started)
- **Warning**: Issues requiring attention (failed scheduling, probe failures, evictions)

## Querying Events in Dynatrace

Kubernetes events are selected by **`event.provider`**, not `event.kind`:

```dql
fetch events, from:now()-24h
| filter event.provider == "KUBERNETES_EVENT"
| fields timestamp,
         k8s.cluster.name,
         dt.kubernetes.event.reason,
         dt.kubernetes.event.involved_object.kind,
         dt.kubernetes.event.involved_object.name,
         dt.kubernetes.event.message
| sort timestamp desc
| limit 50
```

> **Why not `event.kind`?** `event.kind` describes the *Dynatrace* event family
> (`DAVIS_EVENT`, `DAVIS_PROBLEM`, `SECURITY_EVENT`, …). There is no `KUBERNETES_EVENT`
> kind, so `filter event.kind == "KUBERNETES_EVENT"` returns zero rows and no error.
> `event.provider` is what identifies the ingest source.

Kubernetes' own `Normal` / `Warning` classification arrives as **`status`** — `INFO` for
Normal, `WARN` for Warning. It is *not* `event.type`: on an ingested Kubernetes event
`event.type` is `CUSTOM_INFO` and `event.kind` is `DAVIS_EVENT`, for every one of them.

```dql
fetch events, from:now()-24h
| filter event.provider == "KUBERNETES_EVENT"
| filter status == "WARN"
| fields timestamp, k8s.namespace.name, dt.kubernetes.event.reason, dt.kubernetes.event.message
| sort timestamp desc
| limit 50
```

When you meet an unfamiliar event source, resist guessing the field names — one `limit 1`
settles it, and the answer is often not what the vendor's own examples imply:

```dql
fetch events, from:now()-24h
| filter event.provider == "KUBERNETES_EVENT"
| limit 1
```

In practice you rarely want "all Warnings" anyway; you want a specific failure mode,
and `dt.kubernetes.event.reason` is the precise, stable way to ask for it:

```dql
fetch events, from:now()-24h
| filter event.provider == "KUBERNETES_EVENT"
| filter in(dt.kubernetes.event.reason,
            {"OOMKilling", "BackOff", "FailedScheduling", "Unhealthy", "Evicted"})
| summarize occurrences = count(),
            by:{dt.kubernetes.event.reason, dt.kubernetes.event.involved_object.name}
| sort occurrences desc
| limit 25
```

> **Retention note**: Kubernetes only keeps events for about an hour by default
> (`--event-ttl`). Dynatrace ingesting them into Grail is what makes a post-incident
> query like the one above possible at all — the cluster itself has already forgotten.

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
