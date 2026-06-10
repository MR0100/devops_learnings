# L13/C07/T02 — QoS Classes

## Learning Objectives

- Understand QoS implications
- Pick QoS per workload

## QoS Classes

Three classes; assigned automatically based on resources:

### Guaranteed
- Every container has CPU+memory requests AND limits
- requests == limits

```yaml
resources:
  requests:
    cpu: "1"
    memory: "1Gi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

### Burstable
- At least one container has requests OR limits
- Not Guaranteed
- Most common

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    memory: "256Mi"
```

### BestEffort
- No requests, no limits anywhere

```yaml
# No resources block
```

## Eviction Priority

When node under pressure (memory, disk):

1. **BestEffort**: evicted first
2. **Burstable**: next; sorted by usage above request
3. **Guaranteed**: last

For production: avoid BestEffort.

## OOM Score

For OOM-killer ranking:
- BestEffort: 1000 (most likely killed)
- Burstable: 2-999 (proportional to usage)
- Guaranteed: -997 (least likely)

Linux OOM-killer kills highest score.

## When Guaranteed

- Latency-sensitive (DBs, caches)
- Critical workloads
- CPU Manager static policy (pinned CPUs)
- Avoid throttling / eviction

Cost: must commit to specific size.

## When Burstable

- Most workloads
- Apps with variable usage
- Cost-efficient (don't pay for max constantly)

Default sensible choice.

## When BestEffort

- Truly disposable (preemptible workloads)
- Test environments
- Demos

NEVER production critical.

## Identify QoS

```bash
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'
# Guaranteed | Burstable | BestEffort
```

Or describe.

## Per-Container

QoS calculated per pod from all containers:
- If ALL containers have requests=limits for CPU and memory → Guaranteed
- If ANY container has requests/limits → Burstable
- Else BestEffort

Sidecar without resources → pod is Burstable even if app is fully specified.

## Implications

### Scheduling
Higher QoS doesn't get priority. Just request/limit math.

### Eviction
Higher QoS protected.

### Throttling
QoS doesn't affect throttling directly. CPU limit does.

### Preemption
PriorityClass affects preemption, not QoS.

## CPU Manager Integration

Static CPU pinning requires:
- Guaranteed QoS
- Integer CPU requests
- Node configured with `--cpu-manager-policy=static`

Pod gets dedicated cores; no shared scheduling.

For: HFT, low-latency.

## Combining With Priority

- Guaranteed + system-cluster-critical = highest protection
- BestEffort + low priority = most likely evicted

Mix as needed.

## Mixed Pod

Container A: Guaranteed.
Container B: no resources.

→ Pod is Burstable (lowest tier wins).

For uniformity: set on all containers.

## ResourceQuota Interaction

ResourceQuota counts requests + limits.

BestEffort pods don't count against `requests.cpu` etc. But count against `pods` quota.

## LimitRange

```yaml
spec:
  limits:
  - default:
      cpu: 500m
      memory: 256Mi
    defaultRequest:
      cpu: 200m
      memory: 128Mi
    type: Container
```

Pods without explicit resources get defaults; become Burstable.

For: prevent BestEffort.

## Anti-Patterns

- Critical app as BestEffort
- Java app as Guaranteed without -Xmx tied to limit
- Mixed Guaranteed + non-resource in pod (whole pod Burstable)

## Examples

### Tier-0 DB
```yaml
resources:
  requests:
    cpu: "4"
    memory: "16Gi"
  limits:
    cpu: "4"
    memory: "16Gi"
```
Guaranteed. Protected from eviction. CPU manager static.

### Stateless API
```yaml
resources:
  requests:
    cpu: "200m"
    memory: "256Mi"
  limits:
    memory: "512Mi"
```
Burstable. Bursts CPU when available. Capped memory.

### Batch Job
```yaml
resources:
  requests:
    cpu: "1"
    memory: "1Gi"
```
Burstable. Can use spare resources.

### Dev / Test
```yaml
# No resources
```
BestEffort. Acceptable for non-critical.

## Eviction Triggers

kubelet evicts when:
- memory.available < threshold
- nodefs.available < threshold
- imagefs.available < threshold
- pid.available < threshold

Soft eviction: grace period.
Hard eviction: immediate.

## Default Thresholds

```
memory.available: 100Mi
nodefs.available: 10%
nodefs.inodesFree: 5%
imagefs.available: 15%
```

Configurable via kubelet.

## Pod Eviction Process

1. kubelet picks victim (BestEffort first, then Burstable by usage above request)
2. Sends SIGTERM
3. terminationGracePeriodSeconds countdown
4. SIGKILL
5. Pod removed from node
6. ReplicaSet (if any) creates replacement on another node

## Node Pressure → Pod Status

```bash
kubectl get pods | grep Evicted
```

Pod has status `Evicted` with reason in events.

## Best Practices

- Guaranteed for tier-0
- Burstable for most apps
- BestEffort only for truly disposable
- LimitRange enforces minimum config
- ResourceQuota per namespace
- Monitor evictions

## Monitoring

```bash
# Evicted pods
kubectl get pods -A | grep Evicted

# Node conditions
kubectl describe node | grep -A 5 Conditions
```

Alert on evictions; tune resources / capacity.

## Cleanup

```bash
# Delete evicted
kubectl get pods -A | grep Evicted | awk '{print $2 " -n " $1}' | xargs -L1 kubectl delete pod
```

For: clean up after pressure event.

## Workload Categories

| Workload | QoS |
|---|---|
| Critical DB | Guaranteed |
| API gateway | Guaranteed |
| Web app | Burstable |
| Worker | Burstable |
| Batch | Burstable / BestEffort |
| Dev | BestEffort |

## QoS vs Priority

Separate concepts:
- QoS: eviction order (resource pressure)
- Priority: scheduling order (also preemption)

Combine for full protection.

## Recommendations

For new app:
1. Start Burstable with conservative requests
2. Monitor; right-size
3. If critical: switch to Guaranteed
4. If batch / disposable: BestEffort

## Quick Refs

```bash
# QoS of pod
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'

# All pods QoS
kubectl get pods -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass

# Evictions
kubectl get events --field-selector reason=Evicted -A
```

## Interview Prep

**Junior**: "QoS classes."

**Mid**: "Pick QoS for DB."

**Senior**: "Eviction order."

**Staff**: "Resource + QoS strategy."

## Next Topic

→ [T03 — Node Selectors, Affinity, Anti-Affinity](T03-Affinity.md)
