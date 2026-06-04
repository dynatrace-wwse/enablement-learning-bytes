# Resource Limits & Requests

Proper resource configuration prevents noisy-neighbor problems and ensures fair scheduling.

## Key Concepts

| Setting | Purpose |
|---------|---------|
| **requests.cpu** | Minimum CPU guaranteed to the container |
| **requests.memory** | Minimum memory guaranteed |
| **limits.cpu** | Maximum CPU the container can use |
| **limits.memory** | Maximum memory — exceeding this triggers OOMKill |

## Best Practices

- Set **requests** based on typical usage (P50)
- Set **limits** based on peak usage (P99) + 20% headroom
- Use **LimitRanges** to enforce defaults across namespaces
- Monitor with `dt.kubernetes.container.cpu_usage` and `dt.kubernetes.container.memory_usage`

## Warning Signs

- CPU throttling: `limits.cpu` too low → increased latency
- OOMKilled: `limits.memory` too low → pod restarts
- Pending pods: cluster has insufficient allocatable resources

<!-- LAB_QUESTION
type: multiple-choice
question: What happens when a container exceeds its memory limit?
options:
  - CPU is throttled
  - The container is OOMKilled and the pod restarts
  - The limit is automatically increased
  - Traffic is redirected to other pods
correct: 1
explanation: When a container exceeds its memory limit, the Linux OOM killer terminates it. Kubernetes then restarts the container based on the pod's restartPolicy.
-->
