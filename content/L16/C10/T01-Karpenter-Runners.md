# L16/C10/T01 — Karpenter-Backed Runners

## Learning Objectives

- Auto-scale CI runners
- Use spot for cost

## Why

Self-hosted runners:
- Cost
- Custom hardware
- Network access

Static pool: idle cost.
Auto-scale: pay for use.

## Karpenter

K8s node autoscaler:
- Just-in-time nodes
- Spot/on-demand mix
- Multiple instance types

## Setup

```bash
# Install Karpenter
helm install karpenter oci://public.ecr.aws/karpenter/karpenter \
  --namespace karpenter \
  --create-namespace \
  --set settings.clusterName=my-cluster \
  --set settings.interruptionQueue=my-cluster
```

## NodePool

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: ci-runners
spec:
  template:
    metadata:
      labels:
        workload: ci
    spec:
      taints:
        - key: ci
          effect: NoSchedule
      requirements:
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [c, m]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [spot, on-demand]
      nodeClassRef:
        name: ci-class
```

For: CI-dedicated nodes.

## Runner Pods with Tolerations

```yaml
spec:
  tolerations:
    - key: ci
      effect: NoSchedule
  nodeSelector:
    workload: ci
```

For: only schedule on CI nodes.

## Scaling Logic

```
Pending CI pod → Karpenter detects
→ Provisions cheapest matching instance
→ Pod scheduled
→ Job runs
→ Pod terminates
→ Node idle X seconds
→ Karpenter deprovisions
```

For: per-job nodes.

## Cost Optimization

### Spot
70-90% off on-demand.

Risk: 2-min eviction.

Mitigate:
- Idempotent jobs
- Retry on eviction

### Right-Size
Match instance to job:
- Small job: t3.medium
- Big build: c6i.4xlarge

## Disruption

```yaml
spec:
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 30s
    expireAfter: 24h
```

For: scale down idle.

## ARC + Karpenter

```
GitHub queue → ARC scales runners → Karpenter provisions nodes
```

End-to-end auto-scale.

## Image Caching

Pre-pull images on nodes:
- Faster job starts
- Lower image registry pulls

## Spot Interruption Handling

GitHub Actions: job retried.
Karpenter: detects 2-min warning; drains.

For: minimize interruption impact.

## Cost Comparison

Static (10 instances always):
- ~$300-1000/mo

Auto-scaled with spot:
- ~$50-200/mo (depends usage)

For high usage: significant savings.

## Multi-Arch

```yaml
requirements:
- key: kubernetes.io/arch
  operator: In
  values: [amd64, arm64]
```

ARM cheaper for compatible workloads.

## GPU

```yaml
requirements:
- key: node.kubernetes.io/instance-type
  operator: In
  values: [p3.2xlarge, g4dn.xlarge]
```

For: ML CI.

## Best Practices

- Spot for CI (idempotent)
- Right-size by job
- Consolidation aggressive
- Image pre-pull
- Multiple NodePools per workload type
- Monitor cost + queue time

## Common Mistakes

- On-demand only (cost)
- Wrong taints (no isolation)
- No consolidation (waste)
- Stale runners (registration)

## Monitoring

Metrics:
- Queue time
- Job duration
- Node lifetime
- Cost per CI minute

For: optimize.

## Quick Refs

```yaml
# Karpenter
NodePool:
  requirements: [...]
  disruption:
    consolidationPolicy: WhenEmpty

# Runner pods
tolerations: [...]
nodeSelector: { ... }
```

## Interview Prep

**Mid**: "Auto-scaling runners."

**Senior**: "Karpenter for CI."

**Staff**: "CI cost optimization."

## Next Topic

→ [T02 — ARC (Actions Runner Controller)](T02-ARC.md)
