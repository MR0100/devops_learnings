# L13/C08/T02 — Vertical Pod Autoscaler (VPA)

## Learning Objectives

- Right-size pods
- Use VPA correctly

## VPA

Adjusts pod CPU/memory requests based on usage:
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  updatePolicy:
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 4
        memory: 8Gi
```

## How It Works

- Recommender: analyzes metrics; calculates ideal requests
- Updater: evicts pods to recreate with new requests
- Admission Controller: injects new requests on pod creation

## Update Modes

### Auto
Auto-evicts + recreates with new requests.

For: dev / non-critical.

### Recreate
Evict pod (restart with new requests). Manual control.

### Initial
Set on pod creation; don't update running.

### Off
Recommendations only; no action. Most common for safety.

```yaml
updateMode: Off   # safest
```

## Recommendations

```bash
kubectl get vpa web-vpa -o yaml
# status.recommendation:
#   containerRecommendations:
#   - containerName: app
#     target:
#       cpu: 250m
#       memory: 300Mi
#     lowerBound: ...
#     upperBound: ...
```

Use for tuning manually.

## When VPA

- Right-sizing analysis
- Resource-intensive apps
- Stable workloads (not bursty)

## When NOT VPA

- HPA already scales (conflict)
- Latency-critical (eviction disrupts)
- Pod restarts cause issues (stateful)

For HPA + VPA: VPA on memory only; HPA on CPU.

## HPA + VPA Conflict

HPA scales replicas based on CPU. If VPA also adjusts CPU requests: HPA target shifts.

Solution:
- Use HPA on different metric (custom)
- Or only VPA recommendations (mode: Off)

## Goldilocks

Open-source dashboard:
- Auto-creates VPA in Off mode for namespace
- Shows recommendations
- Helps tune

```bash
helm install goldilocks fairwinds/goldilocks
kubectl label ns my-ns goldilocks.fairwinds.com/enabled=true
```

For: discovery of right-size values.

## Process

1. Apply VPA in Off mode
2. Run for week (collect data)
3. Review recommendations
4. Update Deployment manually
5. Apply

Or in Auto mode for non-critical workloads.

## In-Place Resize (1.27+ Alpha)

Adjust requests without restart:
```yaml
spec:
  containers:
  - name: app
    resourceResizePolicy:
      requests:
        - resourceName: cpu
          restartPolicy: NotRequired
```

Future: VPA could resize in-place. Currently: still evicts typically.

## Resource Policy

```yaml
resourcePolicy:
  containerPolicies:
  - containerName: app
    minAllowed:
      cpu: 100m
      memory: 128Mi
    maxAllowed:
      cpu: 4
      memory: 8Gi
    controlledResources: [cpu, memory]
```

Bounds prevent extreme changes.

## Pod Disruption

VPA evictions respect PDB. But still disruptive.

For: schedule maintenance windows.

## Best Practices

- VPA in Off mode for recommendations
- Manual adjust based on data
- Goldilocks for visualization
- Test in staging
- Avoid HPA + VPA on same metric

## Common Mistakes

- HPA + VPA on CPU together
- Auto mode for critical workloads
- Without bounds (extreme adjustments)
- Not respecting PDB

## VPA Cost Optimization

Use case:
- Over-provisioned pods: reduce requests; save money
- Under-provisioned: increase to avoid OOM

Net savings: 20-50% typical.

## Multi-Container Pods

Per-container policies:
```yaml
containerPolicies:
- containerName: app
  controlledResources: [cpu, memory]
- containerName: sidecar
  mode: Off   # don't manage sidecar
```

## Install

```bash
git clone https://github.com/kubernetes/autoscaler
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

Or Helm:
```bash
helm install vpa fairwinds-stable/vpa
```

## Recommender Algorithm

Based on:
- Historical usage (percentiles)
- Current usage
- Trend
- Configurable margins

Outputs target, lowerBound, upperBound.

## Cluster Autoscaler Interaction

VPA changes pod requests → may not fit on existing nodes → Cluster Autoscaler adds nodes.

For: ensure capacity available.

## Karpenter Behavior

Karpenter sees larger requests; provisions optimal nodes. Handles VPA well.

## Limitations

- Eviction-based (disruptive)
- Not real-time (analysis takes time)
- Per-pod (not whole deployment fleet)
- Limited in-place support

## Alternative: VPA-Style Manual

```bash
# Get metrics
kubectl top pod -n production

# Or Prometheus
container_cpu_usage_seconds_total
container_memory_working_set_bytes
```

Calculate; update Deployment manually.

For: more control.

## Cost Savings

For 100-pod fleet over-provisioned by 30%:
- Cost ~$1000/mo over-spend
- VPA right-sizes: $700/mo savings

Real impact at scale.

## Common Patterns

### Discovery
VPA in Off mode → Goldilocks → quarterly review.

### Auto for Dev
```yaml
updateMode: Auto
```

For dev/test where restart OK.

### Manual for Prod
Recommendations only; engineers apply.

## Monitoring

```bash
# VPA status
kubectl get vpa
kubectl describe vpa web-vpa

# Recommendations
kubectl get vpa web-vpa -o jsonpath='{.status.recommendation}'
```

## Quick Refs

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  updatePolicy:
    updateMode: Off    # recommendations only
```

## Interview Prep

**Mid**: "VPA vs HPA."

**Senior**: "VPA + HPA conflict."

**Staff**: "Right-sizing program at scale."

## Next Topic

→ [T03 — Cluster Autoscaler](T03-Cluster-Autoscaler.md)
