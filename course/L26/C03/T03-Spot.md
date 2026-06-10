# L26/C03/T03 — Spot Instances (and Karpenter Strategy)

## Learning Objectives

- Use spot
- Karpenter for diversity

## Spot

Unused EC2 capacity:
- 70-90% off
- Evictable with 2-min warning

For: fault-tolerant workloads.

## Use Cases

### Stateless Web
HPA + spot.

### Batch
ML training.

### CI Runners
Build / test.

### Big Data
Spark, Hadoop.

## Eviction Handling

```python
# Listen to metadata
http://169.254.169.254/latest/meta-data/spot/instance-action
```

Or:
- Health check fails
- ASG replaces

## ASG with Spot

```bash
aws autoscaling create-auto-scaling-group \
  --mixed-instances-policy ...
  # Mix on-demand + spot
```

## Karpenter

K8s node autoscaler:
- Multiple instance types
- Spot first
- On-demand fallback

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: [spot, on-demand]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [c, m]
```

For: best of both.

## Diversification

```yaml
requirements:
  - key: node.kubernetes.io/instance-type
    operator: In
    values: [m6i.xlarge, m6a.xlarge, m6g.xlarge, c6i.xlarge]
```

Many types → more spot pool capacity → less eviction.

## Spot Diversification Math

Spot eviction rate:
- Single type: ~5-10%
- 5 types: ~2-3%
- 10+ types: < 1%

For: production spot viable.

## Stateful on Spot

Risky. Use:
- StatefulSets with PDB
- Persistent volumes (survive)
- Or only on-demand

## Stateless on Spot

Easy:
- K8s replaces
- LB removes evicted

## Eviction Tolerance

```yaml
nodeSelector:
  karpenter.sh/capacity-type: spot
tolerations:
  - key: spot-eviction
    operator: Exists
    effect: NoSchedule
```

For: opt-in pods.

## Mixed Workloads

- Production: on-demand
- Async / batch: spot
- Test envs: spot

## Cost Saving

For typical org:
- 60-80% spot for non-critical
- Save 50-70% on compute

## Best Practices

- Karpenter for K8s
- Diverse instance types
- Test eviction
- Monitor spot pool
- Mix with on-demand

## Common Mistakes

- One type (high eviction)
- Stateful on spot
- No eviction handling
- All on-demand (waste)

## Quick Refs

```yaml
# Karpenter NodePool
karpenter.sh/capacity-type: [spot, on-demand]
diverse instance types
```

```bash
# Check spot eviction rate
aws ec2 describe-spot-fleet-request-history
```

## Interview Prep

**Mid**: "Spot instances."

**Senior**: "Karpenter strategy."

**Staff**: "Spot at scale."

## Next Topic

→ [T04 — Graviton & ARM Migration](T04-Graviton-ARM.md)
