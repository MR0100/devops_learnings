# L13/C07/T06 — Priority & Preemption

## Learning Objectives

- Use PriorityClasses
- Manage preemption

## PriorityClass

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "Critical services"
preemptionPolicy: PreemptLowerPriority
```

`value`: integer; higher = more important.

## Pod Usage

```yaml
spec:
  priorityClassName: high-priority
```

Pod gets that priority.

## Effects

### Scheduling Order
Higher-priority pending pods scheduled first.

### Preemption
If can't fit anywhere, scheduler may EVICT lower-priority pods to make room.

## Built-In Priority Classes

K8s reserves:
- `system-cluster-critical`: value 2000000000
- `system-node-critical`: value 2000001000

For: control plane components, critical DaemonSets.

Cannot use these for user workloads.

## Default Priority

Without priorityClassName: priority 0.

Can set global default:
```yaml
metadata:
  name: low-default
value: 100
globalDefault: true
```

All pods without explicit priorityClassName get 100.

## Preemption

When high-priority pod pending:
1. Scheduler tries normal scheduling
2. If no fit: identify lower-priority pods to evict
3. Evict (graceful)
4. Schedule high-priority pod

## Preemption Policy

```yaml
preemptionPolicy: PreemptLowerPriority   # default
# Or:
preemptionPolicy: Never
```

`Never`: pod waits without preempting. Useful for batch (don't disrupt prod).

## What Gets Preempted

Scheduler picks victims to minimize disruption:
- Lower priority
- Smaller resource footprint preferred
- PDB respected (can pause)

Multiple victims possible if needed for fit.

## PDB Interaction

If PDB would be violated by preemption, scheduler may not preempt.

For: critical apps with PDB protected.

## tolerationSeconds (Preempted Pods)

Preempted pod gets terminationGracePeriodSeconds for cleanup.

App must handle SIGTERM.

## Patterns

### Critical Services
```yaml
metadata:
  name: critical
value: 100000
```

Tier-0 apps; preempt lower-tier.

### Standard
```yaml
metadata:
  name: standard
value: 1000
globalDefault: true
```

Most apps.

### Best-Effort
```yaml
metadata:
  name: best-effort
value: 10
preemptionPolicy: Never
```

Batch / dev; won't preempt; gets evicted first when pressure.

## When to Use Priority

### High Priority Reasons
- Customer-facing critical
- Compliance-required
- Tier-0 SLA

### Low Priority Reasons
- Background batch
- Dev / experiments
- Non-critical

### Avoid
- Priority for everything (defeats purpose)
- Constantly preempting (churn)

## ResourceQuota

Per namespace can limit priority class usage:
```yaml
spec:
  hard:
    requests.cpu: "10"
  scopes: ["PriorityClass"]
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values: ["high-priority"]
```

Namespace can use high-priority only up to 10 CPU.

## DaemonSets

System DaemonSets use `system-node-critical`:
- CNI agents
- CSI agents
- Monitoring agents

For: ensure scheduling under pressure.

## Preempt-Lower vs Eviction

Different mechanisms:
- **Preemption**: scheduler-driven; for new pods
- **Eviction**: kubelet-driven; for resource pressure

Combined: priority affects both.

## Real-World

### Multi-Tier Cluster
- system-node-critical: kube-system + node-critical DaemonSets
- system-cluster-critical: kube-system + scheduler
- platform-critical: 100000 (your monitoring, logging)
- production: 10000
- staging: 1000
- batch: 100
- best-effort: 10 (preemptionPolicy: Never)

Layered.

### Capacity Planning
With priorities: provision capacity for normal load.
Critical bursts preempt lower.

Without priorities: provision for peak; expensive.

## Common Mistakes

- Everything high priority (defeats)
- No PDB on important pods (preempted unexpectedly)
- system-* on user pods (not allowed)
- Priority without resource requests (scheduler can't decide)

## Best Practices

- Tiers: critical/standard/batch
- PDB for important
- preemptionPolicy: Never for batch
- ResourceQuota per priority class
- Document priority values
- Test preemption in staging

## Cluster Autoscaler Behavior

When pending high-priority pod can't fit:
- Cluster Autoscaler / Karpenter adds node
- Pod scheduled on new node
- No preemption needed

Preemption + autoscale interact:
- Autoscale takes minutes
- Preemption: seconds
- Karpenter: optimize for both

## Pod Disruption Cost

Cost of preemption:
- Connection drops
- In-flight requests lost
- Restart time

For minimal impact:
- Graceful shutdown
- Health checks for re-balancing
- Idempotent ops

## Inspection

```bash
# Priority of pod
kubectl get pod my-pod -o jsonpath='{.spec.priority}'

# PriorityClasses
kubectl get priorityclass

# Preemption events
kubectl get events --field-selector reason=Preempted
```

## Anti-Patterns

- Constantly preempting (use more capacity instead)
- Critical workload at low priority
- Priority without budget management

## Auto-Scaling Strategy

```
High priority pods + Burstable QoS + Karpenter = good combo
- Burst: Karpenter scales
- Pressure: preempt batch first
- Critical: protected
```

## Quick Refs

```yaml
# Create PC
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high
value: 1000
preemptionPolicy: PreemptLowerPriority

# Use
spec:
  priorityClassName: high
```

```bash
# List
kubectl get priorityclass

# Pod priority
kubectl describe pod my-pod | grep Priority
```

## Interview Prep

**Mid**: "What's PriorityClass."

**Senior**: "Preemption flow."

**Staff**: "Priority strategy for shared cluster."

## Next Topic

→ [T07 — Custom Schedulers](T07-Custom-Schedulers.md)
