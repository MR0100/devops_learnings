# L13/C14/T04 — Container & Pod Metrics

## Learning Objectives

- Source K8s metrics
- Use cAdvisor + node-exporter

## Metric Sources

| Source | Provides |
|---|---|
| cAdvisor (kubelet) | Container metrics |
| node-exporter | Node OS metrics |
| kube-state-metrics | K8s object state |
| App | Application-level |
| API server | Control plane |

All feed Prometheus.

## cAdvisor

Built into kubelet. Collects container metrics from cgroups:
- CPU usage
- Memory usage
- Network I/O
- Disk I/O
- Filesystem

Exposed via kubelet's `/metrics/cadvisor`.

## Useful Metrics

```promql
# CPU usage per container
rate(container_cpu_usage_seconds_total{namespace="my-ns"}[5m])

# Memory working set
container_memory_working_set_bytes{namespace="my-ns"}

# Network bytes
rate(container_network_receive_bytes_total[5m])
rate(container_network_transmit_bytes_total[5m])

# Disk usage
container_fs_usage_bytes
```

## Memory Metrics

- container_memory_rss: resident set
- container_memory_working_set_bytes: working set (most relevant for OOM)
- container_memory_cache: page cache
- container_memory_usage_bytes: total

For OOM analysis: working_set.

## CPU Throttling

```promql
# Throttled time
rate(container_cpu_cfs_throttled_seconds_total[5m])

# Throttled percentage
rate(container_cpu_cfs_throttled_periods_total[5m]) / rate(container_cpu_cfs_periods_total[5m])
```

If > 0: CPU limit too low (or not needed).

## node-exporter

DaemonSet running on every node. Exports Linux OS metrics:
- CPU per core
- Memory + swap
- Disk (per partition)
- Network (per interface)
- Filesystem
- Load average

Standard for K8s monitoring.

```bash
helm install node-exporter prometheus-community/prometheus-node-exporter
```

## Useful Metrics

```promql
# Node CPU
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Node memory
100 * (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes

# Disk space
100 - (node_filesystem_avail_bytes{mountpoint="/"} * 100 / node_filesystem_size_bytes{mountpoint="/"})

# Network
rate(node_network_receive_bytes_total{device="eth0"}[5m])
```

## App Metrics

Apps expose `/metrics` endpoint (Prometheus format):
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET", status="200"} 1234
http_requests_total{method="POST", status="200"} 567

# HELP http_request_duration_seconds Request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 1000
http_request_duration_seconds_bucket{le="0.5"} 1200
```

ServiceMonitor scrapes.

## RED Metrics

For services:
- **Rate**: requests/sec
- **Errors**: failed requests/sec
- **Duration**: latency

```promql
# Rate
rate(http_requests_total[5m])

# Errors
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Duration p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## USE Metrics

For resources:
- **Utilization**: % busy
- **Saturation**: queue depth
- **Errors**: failures

```promql
# CPU utilization
avg(rate(container_cpu_usage_seconds_total[5m])) by (pod) * 100

# CPU saturation (throttling)
rate(container_cpu_cfs_throttled_seconds_total[5m])

# Errors (from app)
rate(errors_total[5m])
```

## Dashboards

Pre-built Grafana:
- 1860 Node Exporter Full
- 7249 Kubernetes Cluster
- 6417 Kubernetes Pods
- 14584 Kubernetes Views Pod

Import by ID.

## Custom App Metrics

Python:
```python
from prometheus_client import Counter, Histogram, start_http_server

requests = Counter("http_requests_total", "Total requests", ["method", "status"])
latency = Histogram("http_request_duration_seconds", "Latency")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    with latency.time():
        response = await call_next(request)
    requests.labels(method=request.method, status=response.status_code).inc()
    return response

start_http_server(9090)
```

Go:
```go
import "github.com/prometheus/client_golang/prometheus/promhttp"

http.Handle("/metrics", promhttp.Handler())
http.ListenAndServe(":9090", nil)
```

## Cardinality

High cardinality kills Prometheus:
- `user_id` label: millions of users → millions of series
- Bad: histogram with too many buckets

For: bound labels (status, method, endpoint pattern).

## Histograms

For latency:
```python
latency = Histogram("http_request_duration_seconds", "Latency",
    buckets=[0.001, 0.01, 0.1, 1, 10])
```

Buckets chosen for percentiles you want.

Sum of `_bucket{le="X"}` series ≤ ~10 per histogram.

## Labels Best Practices

- Bound dimensions (env, method, status, endpoint)
- Avoid unbound (user_id, request_id)
- Lowercase, descriptive
- Consistent across metrics

## OpenTelemetry

Modern standard:
- Metrics, traces, logs
- Vendor-agnostic
- Exporters for Prometheus, OTLP

For new: OpenTelemetry SDK.

## Alerting on Metrics

```yaml
groups:
- name: cluster
  rules:
  - alert: NodeMemoryHigh
    expr: 100 * (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 90
    for: 10m
    labels:
      severity: warning
  - alert: PodNotReady
    expr: kube_pod_status_ready{condition="true"} == 0
    for: 10m
  - alert: CPUThrottling
    expr: rate(container_cpu_cfs_throttled_seconds_total[5m]) > 0
    for: 30m
    annotations:
      summary: CPU limit may be too low
```

## Dashboard Layers

1. Cluster overview (CPU, memory, nodes)
2. Per-namespace breakdown
3. Per-workload deep dive
4. Per-pod debug

## Scrape Intervals

Default 30s. Reduce for fast (e.g., 15s for HPA-relevant); increase for low-priority (60s).

Tradeoff: storage + CPU vs resolution.

## Common Mistakes

- Cardinality explosion (kill Prometheus)
- No retention (storage fills)
- High-cardinality labels in CR
- Missing node-exporter (no node OS metrics)
- App not exposing metrics

## Best Practices

- node-exporter + cAdvisor + kube-state-metrics + app metrics
- Bound cardinality
- RED + USE methods
- Standard dashboards + custom
- Alerts SLI-based
- OpenTelemetry for new

## Metrics Pipeline

```
App + cAdvisor + node-exporter + KSM
   ↓ /metrics endpoints
Prometheus (scrape, store)
   ↓
Alertmanager / Grafana
```

For long-term: Prometheus → Thanos / Cortex → S3.

## Inspection

```bash
# Cluster overview
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# http://localhost:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
# http://localhost:3000  (admin / prom-operator)

# Targets
http://localhost:9090/targets

# Rules
http://localhost:9090/rules

# Alerts
http://localhost:9090/alerts
```

## Quick Refs

```promql
# CPU usage
rate(container_cpu_usage_seconds_total[5m])

# Memory
container_memory_working_set_bytes

# Disk
node_filesystem_avail_bytes

# Network
rate(container_network_receive_bytes_total[5m])
```

## Interview Prep

**Junior**: "Where do K8s metrics come from."

**Mid**: "RED vs USE methods."

**Senior**: "Cardinality issue."

**Staff**: "Observability platform for 100 clusters."

## Next Topic

→ Move to [L13/C15 — Logging in K8s](../C15/README.md)
