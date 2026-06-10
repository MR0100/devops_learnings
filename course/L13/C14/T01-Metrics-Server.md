# L13/C14/T01 — Metrics Server

## Learning Objectives

- Install Metrics Server
- Use kubectl top + HPA

## Metrics Server

Lightweight metrics aggregator. Provides:
- `kubectl top pod`
- `kubectl top node`
- HPA resource metrics

NOT a full monitoring system; for current usage only.

## Install

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

For self-managed K8s.

EKS / GKE / AKS: install as add-on.

## Verify

```bash
kubectl top node
# NAME            CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
# ip-10-0-1-23    250m         12%    1024Mi          25%

kubectl top pod -n my-namespace
# NAME       CPU(cores)   MEMORY(bytes)
# my-app-1   100m         128Mi
```

## How It Works

```
kubelet (on each node)
  ↓ (cAdvisor metrics)
Metrics Server (aggregated)
  ↓ (Metrics API)
HPA, kubectl top, ...
```

cAdvisor (built into kubelet) collects container metrics.
Metrics Server aggregates across cluster.

## Resource Metrics API

```
GET /apis/metrics.k8s.io/v1beta1/pods
GET /apis/metrics.k8s.io/v1beta1/nodes
```

For tools needing current usage.

## HPA Uses

HPA queries Metrics Server every 15s for CPU/memory:
```yaml
metrics:
- type: Resource
  resource:
    name: cpu
    target:
      type: Utilization
      averageUtilization: 70
```

Without Metrics Server: HPA can't decide.

## Common Issues

### kubectl top fails
```
error: Metrics API not available
```

Causes:
- Not installed
- TLS issues (in some clusters)

Fix install:
```bash
# For TLS issue:
kubectl edit deployment metrics-server -n kube-system
# Add: --kubelet-insecure-tls
```

### Stale Metrics
Metrics Server polls kubelet every 15s. ~1 min lag possible.

For real-time: Prometheus + container_cpu_usage_seconds_total.

## Resources

Metrics Server itself:
- Small: 100m CPU, 200Mi memory
- Scales linearly with nodes / pods

## Cost

Cheap. ~$1-5/mo for small clusters.

## Limits

- Current metrics only (no history)
- No custom metrics
- 15s resolution

For more: Prometheus.

## When NOT Metrics Server

- Production monitoring (need history)
- Custom metrics
- Long-term analysis

Always install Metrics Server (cheap, needed for HPA). Plus Prometheus for full.

## Cluster Auto-Install

Most managed K8s ship it:
- EKS: install via add-on
- GKE: built-in
- AKS: built-in

For self-managed: install manually.

## Architecture

```
┌──────────────────────────┐
│ Metrics Server Pod       │
│ (1+ replicas)            │
└────┬─────────────────────┘
     ↓ (polls every 15s)
┌────┴────┐ ┌────┐ ┌────┐
│ kubelet │ │ k │ │ k  │
│ Node 1  │ │ 2 │ │ 3  │
└─────────┘ └───┘ └────┘
```

## Metrics Pipeline

```
Container → cgroups → cAdvisor → kubelet /metrics/resource → Metrics Server
```

For Prometheus path: similar but Prometheus scrapes cAdvisor directly.

## Configuration

```yaml
# Args to Metrics Server
- --kubelet-preferred-address-types=InternalIP
- --kubelet-insecure-tls
- --kubelet-use-node-status-port
```

## Scaling

Metrics Server is HPA target itself:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: metrics-server
  namespace: kube-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: metrics-server
  minReplicas: 2
  maxReplicas: 5
```

For HA / huge clusters.

## Monitoring Metrics Server

Self-monitoring:
- Pod healthy?
- Memory usage?
- Latency to kubelets?

Prometheus alerts.

## kubectl top Output

```bash
# Sort
kubectl top pod --sort-by=cpu
kubectl top pod --sort-by=memory

# Containers
kubectl top pod my-pod --containers

# Namespace
kubectl top pod -n my-ns

# Labels
kubectl top pod -l app=web
```

## VPA Uses

VPA (Vertical Pod Autoscaler) also queries Metrics Server (and Prometheus optionally).

## Best Practices

- Install always
- Add to HA install (2+ replicas)
- Monitor uptime
- Use for HPA + kubectl top
- Pair with Prometheus for history

## Common Mistakes

- Not installed (HPA fails)
- TLS misconfig
- Single replica (HA risk)

## Resources

Latest from sigs.k8s.io/metrics-server. Active development.

## Quick Refs

```bash
# Install
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify
kubectl get apiservice v1beta1.metrics.k8s.io

# Top
kubectl top node
kubectl top pod -A
kubectl top pod --sort-by=cpu
```

## Interview Prep

**Junior**: "What's Metrics Server."

**Mid**: "HPA + Metrics Server."

**Senior**: "Metrics Server vs Prometheus."

## Next Topic

→ [T02 — kube-state-metrics](T02-Kube-State-Metrics.md)
