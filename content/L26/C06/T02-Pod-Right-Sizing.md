# L26/C06/T02 — Pod Right-Sizing

## Learning Objectives

- Right-size pods
- Tune requests / limits

## Requests vs Limits

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

- Requests: scheduling; reserved
- Limits: max allowed

## Why Right-Size

Over-provisioned:
- Wasted cluster capacity
- Need more nodes
- Higher bill

Under-provisioned:
- OOM kills
- CPU throttling
- Performance issues

## Tools

### VPA (Vertical Pod Autoscaler)
Recommends or auto-adjusts.

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: Recommendation   # or Auto
```

### Goldilocks
Suggested resources per workload:
```bash
helm install goldilocks fairwinds-stable/goldilocks
```

### Kubecost
Recommendations.

## Manual

Monitor:
```promql
container_memory_usage_bytes
container_cpu_usage_seconds_total
```

Set:
- requests ≈ p95 usage
- limits ≈ p99 + buffer

## QoS Classes

- Guaranteed: requests == limits
- Burstable: requests < limits
- BestEffort: no requests/limits

For prod: Guaranteed (predictable) or Burstable.

## CPU

- Hard to over-throttle (throttled, slow)
- Often: no limit (let burst)

Some say:
- requests = baseline
- No limit (let burst)

## Memory

- OOM if exceeds
- Limit important

For:
- requests = stable baseline
- limits = max safe

## HPA

Horizontal scaling:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

For: handle variable load.

## VPA + HPA

Don't conflict on CPU:
- HPA scales replicas
- VPA sizes pods

For: combined; VPA off for CPU.

## Best Practices

- Profile actual usage
- VPA in Recommendation mode
- Goldilocks for guidance
- Monitor saturation
- Per-workload sizing

## Common Mistakes

- Default huge requests (waste)
- No limits on memory (OOM cluster)
- VPA in Auto for stateful (recreates)
- Skip monitoring

## Quick Refs

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

# VPA
kind: VerticalPodAutoscaler
updateMode: Recommendation | Auto | Off
```

## Interview Prep

**Mid**: "Pod sizing."

**Senior**: "VPA / HPA."

**Staff**: "K8s cost optimization."

## Next Topic

→ [T03 — Cluster Bin-Packing](T03-Bin-Packing.md)
