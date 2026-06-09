# L30/C03 — Project 3: Production-Grade Observability Stack

## Topics

- **T01 Prometheus + Thanos** — Long-term metrics
- **T02 Loki + Grafana** — Logs
- **T03 OTel Collector Fleet** — Unified pipeline

## Goal

Demonstrate operating a production-grade observability stack handling realistic volume.

## Architecture

```
Apps (instrumented with OTel SDK)
   ↓ OTLP
[OTel Collector DaemonSet] per node
   ↓
[OTel Gateway tier]
   - Tail sampling
   - Enrichment
   - Routing
   ↓
   ├──→ Prometheus / Thanos (metrics)
   ├──→ Loki (logs)
   └──→ Tempo (traces)

[Grafana] queries all three; exemplars link
```

## Component Setup

### Prometheus + Thanos

```bash
helm install prom prometheus-community/kube-prometheus-stack \
  --set prometheus.thanosService.enabled=true \
  --set prometheus.thanosServiceMonitor.enabled=true
```

Add Thanos:
- Sidecar uploads blocks to S3
- Receive tier for remote write (alternative)
- Querier fans out
- Compactor downsamples

```bash
helm install thanos bitnami/thanos -f thanos-values.yaml
```

### Loki

```bash
helm install loki grafana/loki \
  -f loki-values.yaml
```

Configure S3 storage backend:
```yaml
loki:
  storage:
    type: s3
    s3:
      region: us-east-1
      bucketnames: loki-chunks
```

### Tempo

```bash
helm install tempo grafana/tempo \
  -f tempo-values.yaml
```

Backend: S3.

### OTel Collector

Two deployments:
- DaemonSet (node-level; collect from local apps)
- Gateway (cluster-level; processing)

```yaml
mode: daemonset
config:
  receivers:
    otlp: { protocols: { grpc: {}, http: {} } }
    kubernetesattributes: {}
    hostmetrics: { collection_interval: 30s }
  
  processors:
    batch: {}
    memory_limiter: { limit_mib: 1024 }
    resource:
      attributes:
        - { key: cluster, value: prod-us-east-1, action: insert }
  
  exporters:
    otlp: { endpoint: otel-gateway.observability:4317 }
  
  service:
    pipelines:
      metrics: { receivers: [otlp, hostmetrics], processors: [batch, memory_limiter], exporters: [otlp] }
      logs: { receivers: [otlp], processors: [batch], exporters: [otlp] }
      traces: { receivers: [otlp], processors: [batch], exporters: [otlp] }
```

Gateway:
```yaml
mode: deployment
config:
  processors:
    tail_sampling:
      policies:
        - { type: status_code, status_code: { status_codes: [ERROR] } }
        - { type: latency, latency: { threshold_ms: 500 } }
        - { type: probabilistic, probabilistic: { sampling_percentage: 10 } }
  
  exporters:
    prometheusremotewrite: { endpoint: http://thanos-receive:19291/api/v1/receive }
    loki: { endpoint: http://loki:3100/loki/api/v1/push }
    otlp: { endpoint: tempo:4317 }
```

## Sample App for Demo

A Go app with OTel auto-instrumentation:
- HTTP server emits trace + metrics
- Structured JSON logs with trace_id

Generate load via k6 or similar.

## Dashboards

Pre-built Grafana dashboards:
- Service Overview (per service: rate, errors, p99)
- Cluster Overview (K8s metrics)
- Log search (Loki)
- Trace search (Tempo)

Provision dashboards as code (JSON in ConfigMap):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-dashboard
  labels:
    grafana_dashboard: "1"
data:
  dashboard.json: |
    { ... }
```

Grafana sidecar discovers and loads.

## Exemplars

In sample app:
```go
duration := time.Since(start).Seconds()
histogram.WithLabelValues(method).
    (prometheus.ExemplarObserver).
    ObserveWithExemplar(duration, prometheus.Labels{"trace_id": traceID})
```

In Grafana dashboard: enable exemplars on histogram panels.

## SLOs

Use Sloth to generate SLO rules:
```yaml
service: my-app
labels: { team: payments }
slos:
  - name: availability
    objective: 99.9
    sli:
      events:
        error_query: rate(http_requests_total{status=~"5..", service="my-app"}[5m])
        total_query: rate(http_requests_total{service="my-app"}[5m])
    alerting:
      page_alert: { labels: { severity: critical } }
      ticket_alert: { labels: { severity: warning } }
```

Sloth generates Prometheus alerts (multi-window burn rate).

## Sizing

For demo:
- 10 sample services
- 1000 req/s aggregate
- 100K traces/day (sampled)
- 10 GB/day logs

Storage:
- Metrics: ~1 GB/day raw → compressed
- Logs: 10 GB/day → S3 (Loki)
- Traces: ~100 MB/day (tail-sampled)

Costs: ~$50/month for full stack at this volume.

## Demo Script

15-min Loom:
1. Architecture (2 min)
2. Show app + load generation (1 min)
3. Service overview dashboard (2 min)
4. Click exemplar → trace in Tempo (2 min)
5. From trace → logs in Loki (2 min)
6. SLO dashboard with burn rates (2 min)
7. Simulated failure → alert fires (2 min)
8. Investigate via correlation (1 min)
9. Lessons (1 min)

## What to Highlight

- Cross-pillar correlation (exemplar → trace → logs)
- Tail sampling for cost
- SLO-based alerting (not threshold)
- Multi-tier collector
- Storage tiering (recent in memory; older in S3)

## Scale Considerations

For production-realistic claims:
- 50K services × 100 metrics × 10s → 5M samples/sec
- Prometheus + Thanos can handle
- Mimir alternative (multi-tenant native)

For 100K sample/sec demo: enough to show patterns.

## Lessons Learned

Things you'll discover building this:
- Cardinality discipline (high-cardinality labels explode Prometheus)
- Tail sampling reduces cost massively
- Exemplars require coordinated SDK + storage
- Grafana provisioning takes time to debug
- Object storage costs add up if not lifecycle-managed

## README Template

```markdown
# Production-Grade Observability Stack

## Demo
- Metrics: Prometheus + Thanos
- Logs: Loki
- Traces: Tempo
- All via OTel Collector
- Correlated in Grafana

## Scale Demonstrated
- 1000 req/s, 100K traces/day
- Costs: $50/month
- Production-realistic patterns at lower volume

## How to Run
[steps]

## What I Learned
[specifics]
```

## Interview Themes

- "Walk me through observability project"
- "Cross-pillar correlation"
- "How would you scale to 100M time series?"
- "Tail sampling — value"
- "SLO-based alerting"
