# L30/C05/T01 — Karpenter + Spot

## Learning Objectives

- Build spot-heavy platform
- Save cost

## Why Karpenter + Spot

This capstone proves the single highest-leverage FinOps move in Kubernetes:
running stateless workloads on **Spot** for 60–80% off on-demand, with
**Karpenter** making it operationally sane. The project demonstrates you can chase
real cost savings *without* tanking reliability — the trade-off every cost
conversation comes down to.

### Karpenter over Cluster Autoscaler (the interview classic)

- **Groupless, just-in-time provisioning** — Karpenter looks at *pending pods*
  and launches the cheapest instance that fits, rather than scaling fixed node
  groups (ASGs). No pre-defining a grid of instance types per AZ.
- **Better bin-packing and consolidation** — it actively consolidates
  underused nodes, so you don't pay for fragmentation.
- **Native diversification** — one NodePool can span many instance
  types/families/AZs, which is exactly what makes Spot reliable (see below).

Trade-off: Karpenter provisions nodes directly (more IAM/permissions surface)
and its consolidation can re-arrange pods in ways you must design for (PDBs,
graceful shutdown — C05/T02).

### Why Spot Reliability Comes From Diversification

Spot capacity is reclaimed per instance pool (type × AZ). If you run one
instance type, an interruption hits *all* your nodes at once. Spreading across
many types, families, and AZs means an interruption in one pool is a small,
absorbable fraction of capacity — the `capacity-optimized` allocation strategy
then prefers pools least likely to be interrupted. Diversification is the
reliability lever; everything else (PDBs, drain) is damage control.

## Architecture

```
K8s Cluster
├─ Critical pods: on-demand   (control planes, stateful — never interrupt)
├─ Stateless web: spot (Karpenter)
├─ Batch / CI: spot heavy     (interruption-tolerant by nature)
└─ Stateful: on-demand
```

## Karpenter NodePools

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general
spec:
  template:
    metadata:
      labels:
        workload-type: general
    spec:
      taints:
        - key: spot
          effect: NoSchedule
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: [spot, on-demand]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [c, m]
        - key: kubernetes.io/arch
          operator: In
          values: [amd64, arm64]
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
```

## Multiple Types

Diversification:
```yaml
requirements:
  - key: karpenter.k8s.aws/instance-family
    operator: In
    values: [c5, c6, c7, m5, m6, m7]
```

For: lower eviction.

## Spot Tolerations

```yaml
spec:
  tolerations:
    - key: spot
      operator: Exists
      effect: NoSchedule
  nodeSelector:
    karpenter.sh/capacity-type: spot
```

For: opt-in pods.

## Cost

For 100 nodes:
- All on-demand: $30k/mo
- 80% spot: $10-12k/mo
- 60% savings

## Best Practices

- Diverse instance types
- Spot for stateless
- On-demand for stateful
- Consolidation aggressive
- ARM where compatible

## Common Mistakes

- One instance type (high eviction)
- Stateful on spot
- No tolerations (pods don't schedule)

## Acceptance Criteria

- A NodePool spanning multiple instance types/families and all AZs, with
  spot + on-demand capacity types
- Karpenter provisions a node for a pending pod in ~1 minute and consolidates
  when nodes go underused
- Stateless workloads land on Spot; stateful/critical stay on-demand (via
  taints/affinity)
- A documented before/after cost number (on-demand-only vs. spot-heavy)

## Quick Refs

```yaml
NodePool:
  requirements: spot + on-demand, diverse types/families/AZs
  disruption: WhenEmptyOrUnderutilized

Pod:
  tolerations: spot
  nodeSelector: spot
```
```
Karpenter vs CAS: groupless JIT provisioning + consolidation + diversification
Spot reliability = diversification (many pools), capacity-optimized strategy
```

## Interview Prep

**Junior**: "What's the difference between Spot and on-demand instances?" —
On-demand instances are guaranteed but full price. Spot instances are spare AWS
capacity at 60–90% off, but AWS can reclaim them with a 2-minute warning. You run
interruption-tolerant, stateless workloads on Spot to save money.

**Mid**: "Why Karpenter over Cluster Autoscaler?" — Cluster Autoscaler scales
predefined node groups (ASGs), so you have to define a grid of instance types per
AZ up front. Karpenter is groupless — it looks at the actual pending pods and
launches the cheapest instance that fits them, just in time. It also consolidates
underused nodes and natively diversifies across many instance types, which both
saves money and makes Spot more reliable. It's faster and produces tighter
bin-packing.

**Senior**: "How do you make a Spot-heavy platform reliable?" — Reliability on
Spot comes mostly from diversification: Spot capacity is reclaimed per pool
(instance type × AZ), so if you run one type, one interruption takes everything.
Spreading across many instance types, families, and AZs means any single
interruption is a small, recoverable fraction, and the capacity-optimized
strategy steers toward pools least likely to be reclaimed. On top of that you
keep stateful and critical components on-demand, use PDBs so too many pods can't
drain at once, and make apps handle SIGTERM gracefully (C05/T02). The 80/20 is
diversification; the rest is graceful handling of the interruptions that still
happen.

**Staff**: "Leadership wants to put everything on Spot to cut cost. Where do you
push back?" — I'd frame it as reliability-per-dollar, not max savings. Spot is
the right default for stateless, interruption-tolerant, horizontally-scalable
workloads — that's where you capture ~70% savings at a tiny reliability cost
(99.95% → ~99.93% in our numbers). But some things must stay on-demand: stateful
systems where an interruption risks data or long recovery (databases),
singleton/control-plane components (Istio control plane, Vault) where losing the
instance is an outage not a reschedule, and anything with a hard latency SLA that
can't absorb cold-start churn. So the answer isn't "everything on Spot," it's a
*portfolio*: aggressive Spot for the stateless majority, on-demand (or Savings
Plans/Reserved) for the critical core, and a fallback to on-demand when Spot is
unavailable. Putting truly everything on Spot trades a known small bill for a
tail-risk outage — which costs far more than it saves the day a whole family gets
reclaimed.

## Next Topic

→ [T02 — Graceful Spot Interruption Handling](T02-Spot-Interruption.md)
