# L13/C19/T04 — Capacity Planning

## Learning Objectives

- Plan cluster capacity
- Maintain headroom

## Why

Without planning:
- Pods Pending (no capacity)
- Slow scaling (lag for nodes)
- Cost over-spending (over-provisioned)
- Eviction storms

## Metrics

### Allocatable
What pods can use (after kubelet, system reserved):
```bash
kubectl describe node | grep -A 5 Allocatable
```

### Requested
What current pods request:
```bash
kubectl describe node | grep -A 5 "Allocated resources"
```

## Headroom

Target: keep 20-30% Allocatable free.

```
Headroom = (Allocatable - Requested) / Allocatable
```

If <20%: scale up.
If >40%: scale down.

## Cluster Capacity

Per resource (CPU, memory):
```promql
# Cluster CPU
sum(kube_node_status_allocatable{resource="cpu"})

# Requested CPU
sum(kube_pod_container_resource_requests{resource="cpu"})

# Headroom
1 - sum(kube_pod_container_resource_requests{resource="cpu"}) / sum(kube_node_status_allocatable{resource="cpu"})
```

Track over time.

## Growth Rate

Track:
- Pod count
- Total requested CPU/memory
- Number of nodes

For: forecast.

```promql
# Pod growth rate
deriv(count(kube_pod_info)[1d:])
```

Linear extrapolation predicts future need.

## Plan Ahead

For:
- Holiday traffic
- Marketing campaign
- New product launch
- Expected user growth

Pre-provision; don't rely on autoscale lag.

## Karpenter

Auto-provisions nodes; near-instant. Reduces planning need.

But: still cap budget (`limits` on NodePool).

## Cluster Autoscaler

Scales ASG; 3-5 min lag.

Plan baseline + autoscale buffer.

## Burst Capacity

Two strategies:
- **Provisioned**: pay for headroom always
- **Just-in-time**: autoscale (cheaper but lag)

For latency-critical: provisioned.

## Cost vs Performance

Trade-off:
- More headroom = better perf, worse cost
- Less headroom = better cost, scale lag

Tune per app.

## Workload Patterns

- Stateless: easy to scale
- Stateful: slow to scale (PV provisioning)
- Burst: pre-warm
- Steady: tight planning OK

## Node Sizing

Few big nodes vs many small:
- Big: bin-pack efficiency; fewer kubelet overheads
- Small: granular scaling; smaller blast radius

For mixed workloads: heterogeneous node groups.

## Resource Requests Discipline

If apps don't request:
- BestEffort
- Schedule blindly
- OOM / evictions

Enforce via LimitRange:
```yaml
spec:
  limits:
  - default: {cpu: 500m, memory: 256Mi}
    defaultRequest: {cpu: 200m, memory: 128Mi}
    type: Container
```

## Right-Sizing

Per workload:
- Use VPA recommendations
- Or Goldilocks
- Or manual review

Reduce over-provisioning waste.

## Cluster Right-Sizing

```bash
kubectl describe node | grep -A 5 "Allocated resources"
```

If across nodes:
- Avg 30% utilized → over-provisioned
- Avg 80% utilized → tight; add capacity

## Kubecost / OpenCost

Tools for cost visibility:
- Per-namespace cost
- Per-workload cost
- Idle node cost

```bash
helm install kubecost kubecost/cost-analyzer
```

For: chargeback, optimization.

## ResourceQuota

Limit namespace capacity:
```yaml
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "100"
```

For: multi-tenant fairness.

## Multi-Tenancy

Per-team quota:
- Quota = budget
- Tracked + alerted

For: prevent noisy neighbor.

## Capacity Forecasting

Quarterly:
- Look at growth trend
- Plan node provisioning
- Reserve instance / Savings Plans

For: cost optimization.

## Reserved Instances

For steady baseline:
- 1-yr or 3-yr commit
- 30-72% discount
- Predict baseline usage

For burst: on-demand / spot.

## Spot Strategy

For tolerant workloads:
- Up to 90% off
- Karpenter handles
- Mix with on-demand

For 30% baseline + 70% spot: typical.

## Monitoring

Dashboards:
- Cluster headroom over time
- Per-namespace usage
- Pending pods
- Cost per workload

Alert:
- Headroom < 20%
- Pending pods > 0 for 5 min
- Node count near limits

## Scaling Decisions

Capacity decisions:
- Increase MaxReplicas (HPA)
- Add NodePool tier
- Adjust requests
- Pre-warm before event

## Common Mistakes

- Over-provisioning (waste)
- Under-provisioning (perf hit)
- No tracking
- Reactive only (no forecast)
- Reserve everything (no flexibility)

## Best Practices

- 20-30% headroom
- Track growth weekly
- Forecast quarterly
- Use Karpenter (modern AWS)
- Right-size with VPA
- Reserved for baseline
- Spot for tolerant
- Cost dashboards

## Patterns

### Always-On Baseline
- Reserved nodes for baseline
- On-demand for surge
- Spot for batch

### Auto-Scaled
- HPA scales pods
- Karpenter scales nodes
- Both metrics-driven

### Pre-Warm
- Known event upcoming
- Manually scale up before
- Scale down after

## When Cluster Full

Symptoms:
- Pods Pending: insufficient resources
- Slow scheduling

Actions:
- Scale up (autoscaler or manual)
- Right-size existing
- Defer non-critical
- Move to new cluster

## Disk Capacity

Don't forget:
- PVCs
- Node disk (image cache, logs)
- etcd

Track + plan.

## Network Capacity

For high-throughput:
- Bandwidth per node
- Cluster-wide
- Cross-AZ costs

Plan for traffic spikes.

## Quick Refs

```bash
# Node capacity
kubectl describe node | grep -A 5 "Allocated resources"

# Cluster capacity (prom)
sum(kube_node_status_allocatable{resource="cpu"})
sum(kube_pod_container_resource_requests{resource="cpu"})

# Pending pods
kubectl get pods --all-namespaces --field-selector=status.phase=Pending

# Kubecost
helm install kubecost kubecost/cost-analyzer
```

## Interview Prep

**Mid**: "Cluster capacity planning."

**Senior**: "Headroom tuning."

**Staff**: "Cost-optimized scaling at scale."

## Next Topic

→ Move to [L13/C20 — Production Kubernetes Checklist](../C20/README.md)
