# L13/C14/T03 — Prometheus Operator

## Learning Objectives

- Use Prometheus Operator
- Configure ServiceMonitor / PodMonitor

## Prometheus Operator

Manages Prometheus + ecosystem via CRDs:
- Prometheus
- Alertmanager
- ServiceMonitor
- PodMonitor
- PrometheusRule
- AlertmanagerConfig
- Probe

For: declarative monitoring.

## Kube-Prometheus-Stack

The standard install. Includes:
- Prometheus Operator
- Prometheus
- Alertmanager
- Grafana
- node-exporter
- kube-state-metrics
- Pre-built dashboards + alerts

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

## Prometheus CR

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: main
  namespace: monitoring
spec:
  replicas: 2
  retention: 30d
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: gp3
        resources:
          requests:
            storage: 100Gi
  resources:
    requests:
      cpu: 1
      memory: 4Gi
  serviceMonitorSelector:
    matchLabels:
      release: kube-prometheus-stack
  podMonitorSelector: {}
  ruleSelector: {}
  alerting:
    alertmanagers:
    - namespace: monitoring
      name: alertmanager-main
      port: web
```

Operator creates StatefulSet + Services.

## ServiceMonitor

Tells Prometheus what Services to scrape:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  namespace: my-namespace
  labels:
    release: kube-prometheus-stack    # matches Prometheus selector
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
  namespaceSelector:
    matchNames:
    - my-namespace
```

Prometheus discovers Service; scrapes pods backing it.

## PodMonitor

For Pods without Service:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: my-app
spec:
  selector:
    matchLabels:
      app: my-app
  podMetricsEndpoints:
  - port: metrics
    path: /metrics
```

Direct pod scraping.

## App Setup

Pod exposes metrics:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  selector:
    app: my-app
  ports:
  - name: metrics       # named port for ServiceMonitor
    port: 9090
    targetPort: 9090
```

```yaml
# Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        ports:
        - name: metrics
          containerPort: 9090
```

## PrometheusRule

Alert rules as CR:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: my-app-rules
spec:
  groups:
  - name: my-app
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "{{ $labels.service }} error rate {{ $value }}"
    - record: my_app:request_rate
      expr: sum(rate(http_requests_total[5m]))
```

Both alerts and recording rules.

## AlertmanagerConfig

Per-namespace alertmanager config:
```yaml
apiVersion: monitoring.coreos.com/v1alpha1
kind: AlertmanagerConfig
metadata:
  name: my-team
  namespace: my-namespace
spec:
  route:
    receiver: my-team
    groupBy: [alertname]
  receivers:
  - name: my-team
    slackConfigs:
    - apiURL:
        name: slack-secret
        key: url
      channel: '#alerts'
```

Multi-tenant alerting.

## Probe

For black-box monitoring:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: Probe
metadata:
  name: my-endpoint
spec:
  jobName: external-monitoring
  prober:
    url: blackbox-exporter:9115
  targets:
    staticConfig:
      static:
      - https://example.com
```

Pings external endpoints; alerts on failure.

## Default ServiceMonitors

Kube-Prometheus-Stack pre-configures:
- kube-apiserver
- kubelet
- node-exporter
- kube-state-metrics
- coredns
- etc.

All cluster components monitored out of box.

## Custom ServiceMonitor

Match by label:
```yaml
spec:
  serviceMonitorSelector:
    matchLabels:
      release: kube-prometheus-stack
```

Apps must have label to be scraped.

For wider:
```yaml
serviceMonitorSelector: {}    # match all
```

## Cross-Namespace

```yaml
spec:
  serviceMonitorNamespaceSelector:
    matchLabels:
      monitoring: enabled
```

Only namespaces with `monitoring=enabled` label have ServiceMonitors discovered.

For: tenant isolation.

## Sharding

For huge clusters:
```yaml
spec:
  shards: 3
```

Multiple Prometheus instances; targets split.

## Federation

Federate metrics from many Prometheus instances to central:
```yaml
spec:
  additionalScrapeConfigs:
    name: extra-configs
    key: federate.yaml
```

For: multi-cluster aggregation.

## Thanos / Cortex / Mimir

For long-term + global view:
- Thanos: sidecar to Prometheus; stores in S3
- Cortex / Mimir: scalable multi-tenant

Kube-Prometheus-Stack supports Thanos:
```yaml
spec:
  thanos:
    image: quay.io/thanos/thanos:v0.32.0
    objectStorageConfig:
      key: thanos.yaml
      name: thanos-config
```

For: years of metrics + global queries.

## Resources

For typical:
- Prometheus: 1 CPU, 4 GB RAM, 100 GB storage
- Per 1M time series: ~3 GB memory
- ~200 GB / month per cluster typical

## Storage

PVC for Prometheus:
```yaml
spec:
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: gp3
        resources:
          requests:
            storage: 200Gi
```

For: persistence.

Plus retention:
```yaml
retention: 30d
retentionSize: 150GB
```

## Alertmanager

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Alertmanager
metadata:
  name: main
spec:
  replicas: 3
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: gp3
        resources:
          requests:
            storage: 10Gi
```

HA via 3 replicas + mesh.

## Grafana

Bundled. Pre-configured dashboards:
- K8s cluster
- Node exporter
- Workloads
- API server

Auto-detects Prometheus data source.

## Common Mistakes

- Wrong ServiceMonitor label (not discovered)
- No retention (storage fills)
- Single Prometheus (HA risk)
- No remote write to long-term

## Best Practices

- Kube-Prometheus-Stack (standard)
- ServiceMonitor per app
- Retention 30d + Thanos for long-term
- HA Alertmanager (3 replicas)
- AlertmanagerConfig per team
- Recording rules for expensive queries
- Monitor Prometheus itself

## Monitoring Prometheus

```promql
# Self-metrics
prometheus_tsdb_head_series                  # series count
prometheus_target_scrape_pool_targets        # scraped
prometheus_engine_query_duration_seconds     # query speed
```

Alert if Prometheus unhealthy.

## Inspection

```bash
# CRs
kubectl get prometheus -A
kubectl get servicemonitor -A
kubectl get prometheusrule -A
kubectl get alertmanager -A

# Targets
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# http://localhost:9090/targets

# Alerts
http://localhost:9090/alerts
```

## Operations

```bash
# Reload rules without restart
curl -X POST http://prometheus:9090/-/reload

# Status
curl http://prometheus:9090/api/v1/status/config
```

## Quick Refs

```yaml
# ServiceMonitor
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
spec:
  selector:
    matchLabels: {app: my-app}
  endpoints:
  - port: metrics

# PrometheusRule
spec:
  groups:
  - name: my-app
    rules:
    - alert: NAME
      expr: PROMQL
```

## Interview Prep

**Mid**: "Prometheus Operator purpose."

**Senior**: "ServiceMonitor design."

**Staff**: "Long-term metrics architecture."

## Next Topic

→ [T04 — Container & Pod Metrics](T04-Container-Pod-Metrics.md)
