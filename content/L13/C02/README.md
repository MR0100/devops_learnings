# L13/C02 — Core Workload Resources

## Topics

- **T01 Pods (The Atomic Unit)** — The smallest deployable unit; 1+ containers sharing net/IPC/storage. Pod lifecycle (Pending → Running → Succeeded/Failed). Restart policies. Pod IP shared by all containers.
- **T02 ReplicaSets & Deployments** — RS ensures N pods running; Deployment manages RS rollouts. Update strategies (RollingUpdate, Recreate). maxSurge, maxUnavailable. Rollback via `kubectl rollout undo`.
- **T03 StatefulSets** — Stable network identity (web-0, web-1), stable storage (per-pod PVC), ordered deployment/scaling. Use for: databases, queues, anything needing stable identity.
- **T04 DaemonSets** — One pod per node. Use for: log collectors, monitoring agents, CNI plugins. Tolerations to schedule on tainted nodes.
- **T05 Jobs & CronJobs** — Run to completion. backoffLimit, completions, parallelism. CronJob is scheduled Job; concurrencyPolicy controls overlap.

## Key Decisions

| Use case | Resource |
|---|---|
| Stateless web service | Deployment |
| Stateful with stable identity (DB, Kafka) | StatefulSet |
| Per-node agent | DaemonSet |
| One-off task | Job |
| Scheduled task | CronJob |
| Tightly coupled with another container | Sidecar in same Pod |

## Common Pitfalls

- StatefulSet pods don't get rescheduled to other nodes automatically on node failure (until 1.27+ with PVC-aware behavior)
- Job retry counts include controller restarts (can multiply if pods crash on a bad state)
- CronJob startingDeadlineSeconds default is large; jobs can fire unexpectedly after API server outage

## Interview Themes

- "When would you use a StatefulSet vs Deployment?"
- "Walk me through a rolling update"
- "Why might a Deployment get stuck rolling?" (probes, image pull, resource pressure)
