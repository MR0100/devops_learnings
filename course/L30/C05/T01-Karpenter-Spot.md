# L30/C05/T01 — Karpenter + Spot

## Learning Objectives

- Build spot-heavy platform
- Save cost

## Architecture

```
K8s Cluster
├─ Critical pods: on-demand
├─ Stateless web: spot (Karpenter)
├─ Batch / CI: spot heavy
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
    consolidationPolicy: WhenUnderutilized
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

## Quick Refs

```yaml
NodePool:
  requirements: spot + diverse
  disruption: WhenUnderutilized

Pod:
  tolerations: spot
  nodeSelector: spot
```

## Next Topic

→ [T02 — Graceful Spot Interruption Handling](T02-Spot-Interruption.md)
