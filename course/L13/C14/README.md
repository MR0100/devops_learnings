# L13/C14 — Observability for K8s

## Topics

- **T01 Metrics Server** — Lightweight metrics aggregator. Powers `kubectl top` and HPA's resource metrics.
- **T02 kube-state-metrics** — Exposes Kubernetes object state as Prometheus metrics (Deployment replicas, Pod phase, etc.) — not resource usage.
- **T03 Prometheus Operator** — Manages Prometheus, ServiceMonitor, PodMonitor, AlertmanagerConfig. Kube-Prometheus-Stack is the standard install.
- **T04 Container & Pod Metrics** — cAdvisor (built into kubelet) for container metrics; node-exporter for node metrics.

## Standard Stack (Kube-Prometheus-Stack)

Installs:
- Prometheus + ServiceMonitor/PodMonitor CRDs
- Grafana with prebuilt K8s dashboards
- Alertmanager
- node-exporter (DaemonSet)
- kube-state-metrics
- Default ServiceMonitors for control plane components

## ServiceMonitor Example

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
  namespace: myns
  labels:
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

## Key Metric Sources

| Metric | Source |
|---|---|
| Container CPU/memory | cAdvisor (kubelet) |
| Node CPU/memory/disk | node-exporter |
| K8s object counts/states | kube-state-metrics |
| Kubelet performance | kubelet itself |
| API server latency | apiserver |
| etcd | etcd metrics endpoint |
| Application | your app's /metrics |

## Common Issues

- Missing scrapes → check ServiceMonitor selector matches Prometheus's serviceMonitorSelector
- Too much cardinality → label hygiene (don't put high-cardinality fields in labels)
- Retention too short → remote write to Thanos/Mimir/Cortex

## Interview Themes

- "Compare metrics-server, kube-state-metrics, cAdvisor"
- "How does the Prometheus Operator simplify scraping?"
- "Diagnose: HPA shows 'unknown' for CPU metric"
- "How would you store 1 year of Prometheus data?"
