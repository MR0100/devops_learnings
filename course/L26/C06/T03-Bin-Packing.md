# L26/C06/T03 — Cluster Bin-Packing

## Learning Objectives

- Efficient node usage
- Reduce node count

## Bin-Packing

Pack pods densely on nodes:
- Fewer nodes
- Lower cost

## Why

Idle nodes:
- 50% utilization typical
- Half capacity wasted

For: aim 70-80% utilization.

## Strategies

### Right-Size Nodes
Match node size to typical pod.

Big pods + small node: waste.
Small pods + big node: waste headroom.

### Mixed
Multiple node sizes.

### Karpenter
Auto-selects:
- For pending pods
- Pick cheapest fit

```yaml
requirements:
  - key: karpenter.k8s.aws/instance-cpu
    operator: In
    values: ["2", "4", "8"]
```

## Consolidation

Karpenter:
- Detects underutilized
- Migrates pods
- Removes node

```yaml
disruption:
  consolidationPolicy: WhenEmpty
  consolidateAfter: 30s
```

Or `WhenUnderutilized` (newer).

## Bin-Packing Algorithms

### First Fit
Put pod in first node that fits.

### Best Fit
Put in node with closest fit.

### Worst Fit
Put in node with most free.

K8s scheduler: customizable.

## Topology Spread

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: zone
  whenUnsatisfiable: DoNotSchedule
```

Spread for HA; tradeoff with packing.

## Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
```

Protects during consolidation.

## Spot Bin-Packing

Karpenter + spot:
- Dense + cheap
- Eviction tolerated

For: massive savings.

## Cluster Autoscaler

Older alternative:
- Scale ASGs
- Less flexible than Karpenter

For: Karpenter usually better on AWS.

## Best Practices

- Karpenter
- Consolidation aggressive
- Right-size pods first
- Mixed instance types
- Topology spread reasonable

## Common Mistakes

- One node size (overprovision)
- Cluster Autoscaler when Karpenter better
- No consolidation (idle nodes)
- Too tight topology (no packing)

## Metrics

```promql
# Node utilization
node:cpu:usage / node:cpu:capacity
node:memory:usage / node:memory:capacity
```

Target: 60-80%.

## Quick Refs

```yaml
# Karpenter
disruption:
  consolidationPolicy: WhenUnderutilized
  consolidateAfter: 30s

# PDB
kind: PodDisruptionBudget
spec:
  minAvailable: 2
```

## Interview Prep

**Mid**: "Bin-packing."

**Senior**: "Karpenter consolidation."

**Staff**: "K8s cost efficiency."

## Next Topic

→ Move to [L26/C07](../C07/README.md) or L27
