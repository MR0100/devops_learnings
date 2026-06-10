# L13/C14/T02 — kube-state-metrics

## Learning Objectives

- Use kube-state-metrics
- Query K8s object state

## kube-state-metrics (KSM)

Exposes K8s object STATE as Prometheus metrics:
- Deployment.spec.replicas
- Pod.status.phase
- Node conditions
- ConfigMap counts
- etc.

vs Metrics Server: resource usage (CPU/memory).

Both needed.

## Install

```bash
helm install kube-state-metrics prometheus-community/kube-state-metrics
```

Or via Kube-Prometheus-Stack (includes it).

## Output

Scrapeable Prometheus endpoint:
```
# HELP kube_deployment_status_replicas Number of replicas
# TYPE kube_deployment_status_replicas gauge
kube_deployment_status_replicas{deployment="my-app", namespace="default"} 3

kube_pod_status_phase{namespace="default", pod="my-app-1", phase="Running"} 1
kube_pod_status_phase{namespace="default", pod="my-app-1", phase="Pending"} 0

kube_node_status_condition{node="ip-10-0-1-23", condition="Ready", status="true"} 1
```

## Metrics Exposed

### Deployment
- kube_deployment_status_replicas
- kube_deployment_status_replicas_available
- kube_deployment_status_replicas_unavailable
- kube_deployment_spec_replicas
- kube_deployment_status_condition

### Pod
- kube_pod_status_phase
- kube_pod_status_ready
- kube_pod_container_status_restarts_total
- kube_pod_container_resource_requests
- kube_pod_container_resource_limits

### Node
- kube_node_status_capacity
- kube_node_status_allocatable
- kube_node_status_condition
- kube_node_info

### Service
- kube_service_info
- kube_service_spec_type

### Other
- kube_configmap_info
- kube_secret_info
- kube_namespace_info
- kube_hpa_status_current_replicas
- kube_job_status_succeeded

## Useful Queries

### Deployment Health
```promql
# Replicas not available
kube_deployment_status_replicas - kube_deployment_status_replicas_available

# Below desired
kube_deployment_status_replicas < kube_deployment_spec_replicas
```

### Pod Issues
```promql
# Pods in CrashLoopBackOff
kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"} == 1

# Pods restarting
rate(kube_pod_container_status_restarts_total[5m]) > 0
```

### Node Issues
```promql
# Nodes not Ready
kube_node_status_condition{condition="Ready", status="true"} == 0

# Memory pressure
kube_node_status_condition{condition="MemoryPressure", status="true"} == 1
```

### Resource Usage
```promql
# CPU requested vs allocatable
sum(kube_pod_container_resource_requests{resource="cpu"}) / sum(kube_node_status_allocatable{resource="cpu"})

# Memory by namespace
sum(kube_pod_container_resource_requests{resource="memory"}) by (namespace)
```

## Alerts (Examples)

```yaml
- alert: DeploymentReplicasMismatch
  expr: kube_deployment_status_replicas != kube_deployment_spec_replicas
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Deployment {{ $labels.deployment }} replica mismatch"

- alert: PodCrashLooping
  expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Pod {{ $labels.pod }} crash looping"

- alert: NodeNotReady
  expr: kube_node_status_condition{condition="Ready", status="true"} == 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Node {{ $labels.node }} not ready"
```

## vs Other Sources

| Source | Use |
|---|---|
| Metrics Server | Resource usage (CPU/RAM) |
| kube-state-metrics | Object state |
| cAdvisor | Container metrics |
| node-exporter | Node OS metrics |

All needed for full observability.

## Architecture

```
kube-apiserver
   ↓ (watch)
kube-state-metrics
   ↓ (Prometheus format on /metrics)
Prometheus (scrape)
```

KSM watches API server; converts to Prometheus metrics.

## Performance

For huge clusters: KSM CPU/memory grows with object count.

Sharding:
```yaml
spec:
  containers:
  - name: kube-state-metrics
    args:
    - --shard=0
    - --total-shards=3
```

Run 3 instances; each handles subset.

## Customization

Limit metrics:
```yaml
args:
- --metric-allowlist=kube_pod_*,kube_deployment_*
- --metric-denylist=kube_pod_status_phase
```

For: reduce metric volume.

## ServiceMonitor

For Prometheus Operator:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kube-state-metrics
spec:
  endpoints:
  - port: http-metrics
  selector:
    matchLabels:
      app.kubernetes.io/name: kube-state-metrics
```

Auto-discovers + scrapes.

## Common Dashboards

Grafana dashboards using KSM:
- Cluster overview
- Deployment health
- Pod restarts
- Resource capacity
- Etc.

Many pre-built (grafana.com dashboard ID).

## Common Mistakes

- Forgot KSM (only Metrics Server installed)
- Too many metrics (cardinality)
- No sharding for huge clusters
- No labels for filtering

## Best Practices

- Install via Kube-Prometheus-Stack
- ServiceMonitor for auto-scrape
- Allowlist if metric volume issue
- Sharding for >5000 nodes
- Standard alerts
- Pre-built dashboards

## Labels

Each metric has labels:
- namespace
- pod / deployment / node / etc.
- Plus K8s labels on object (with `--metric-labels-allowlist`)

For: filtering by team, env, etc.

## Custom Labels

```yaml
args:
- --metric-labels-allowlist=pods=[team,env],deployments=[team]
```

Include specific labels.

## Resources

KSM defaults:
- 100m CPU, 100Mi memory

For huge clusters:
- 500m CPU, 1Gi memory
- Or shard

## Inspection

```bash
# Get metrics endpoint
kubectl get svc kube-state-metrics -n kube-system

# Port-forward
kubectl port-forward svc/kube-state-metrics 8080:8080
curl localhost:8080/metrics | head
```

## Quick Refs

```bash
# Install
helm install kube-state-metrics prometheus-community/kube-state-metrics

# Verify
kubectl get pods -l app.kubernetes.io/name=kube-state-metrics

# Curl metrics
kubectl port-forward svc/kube-state-metrics 8080:8080
curl localhost:8080/metrics
```

## Interview Prep

**Mid**: "kube-state-metrics purpose."

**Senior**: "kube-state-metrics vs Metrics Server."

**Staff**: "Scale KSM for 10000-node cluster."

## Next Topic

→ [T03 — Prometheus Operator](T03-Prometheus-Operator.md)
