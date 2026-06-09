# L17/C02 — Prometheus

## Topics

- **T01 Architecture** — Server, Pushgateway, Alertmanager
- **T02 Service Discovery** — Kubernetes, EC2, file, DNS
- **T03 Scrape Configs & Relabeling** — How targets are configured
- **T04 Storage (TSDB, WAL)** — Time-series DB internals
- **T05 Federation & Remote Write** — Scale strategies
- **T06 Long-Term Storage** — Thanos, Cortex, Mimir

## Architecture

```
Targets (apps with /metrics endpoint)
   ↑
   │ pull (scrape)
   │
[Prometheus Server]
   - Service Discovery
   - Scrape configs
   - TSDB (local disk)
   - PromQL engine
   - Alert evaluator
   │
   ├─ remote_write → Long-term store (Thanos/Mimir/VictoriaMetrics)
   │
   ├─ Alertmanager (alerts go here for routing/dedup)
   │
   └─ Grafana queries via HTTP API
```

Prometheus is **pull-based** — it scrapes targets. Pushgateway is for short-lived jobs that can't be scraped.

## Service Discovery

```yaml
scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
```

Discoverers: Kubernetes, EC2, GCE, Azure, Consul, file, DNS, EC2 tags, more.

## Relabeling

Two phases:
- **relabel_configs**: before scrape (decide WHICH targets)
- **metric_relabel_configs**: after scrape, before storage (modify labels)

Operations: keep, drop, replace, hashmod, labelmap, labeldrop, labelkeep.

```yaml
# Drop high-cardinality metric
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'noisy_metric_with_user_id'
    action: drop
```

## TSDB (Time-Series Database)

```
Series ID = labels hashed
Sample = (timestamp, value)
WAL (Write-Ahead Log) for durability
Blocks of 2 hours compacted on disk
Older blocks merged (downsample)
Retention by time (default 15d)
```

### Compression
Gorilla compression: ~1.37 bytes per sample (vs 16 bytes raw).
A million series × 30s samples × 24h = 2.88B samples × 1.37B = ~4GB/day.

### Local Storage Limits
- Practical local TSDB: ~10M active series, ~30d retention
- Beyond that: remote write

## Federation

Hierarchical scraping:
```yaml
- job_name: federate
  scrape_interval: 60s
  honor_labels: true
  metrics_path: '/federate'
  params:
    'match[]':
      - '{job="my-service"}'
  static_configs:
    - targets: ['prom-local-1:9090', 'prom-local-2:9090']
```

Use: aggregate metrics from per-cluster Prometheus to a central one. Lossy at scale.

## Remote Write

Send all samples (or filtered) to a remote backend:
```yaml
remote_write:
  - url: https://thanos-receive.example.com/api/v1/receive
```

Used by Thanos Receive, Mimir, VictoriaMetrics, Datadog, etc.

## Long-Term Storage

### Thanos
- Sidecar on each Prometheus uploads blocks to S3
- Querier fans out queries to Prometheus + Store Gateway (S3)
- Compactor downsamples older blocks
- Backed by object storage (cheap)

### Cortex / Mimir
- Horizontally scalable multi-tenant Prometheus
- Mimir is Grafana's fork (most active)
- Receives via remote write
- Backed by S3-compatible storage

### VictoriaMetrics
- Single binary or cluster
- Often faster + cheaper than Thanos/Cortex/Mimir
- vmagent for scraping; vmstorage for storage

### Comparison
| | Thanos | Mimir | VictoriaMetrics |
|---|---|---|---|
| Model | Sidecar-based | Remote-write-based | Either |
| Complexity | Medium | High (microservice) | Lower |
| Scale | Very large | Very large | Very large |
| Cost (ops) | Medium | Higher | Lower |

## Sizing

Production rule of thumb:
- 1 GB RAM per ~100K active series
- Disk: 1 byte per sample (compressed)
- CPU: 1 core per ~1M samples/sec scraped

## Best Practices

- **Pull**: keep it. Push only via Pushgateway for batch jobs.
- **Label discipline**: low cardinality only as label
- **Don't put user_id, trace_id in labels** (use exemplars instead)
- **Recording rules** for expensive queries
- **Alerting via PrometheusRule** (managed declaratively)
- **HA**: run 2 Prometheus replicas; deduplicate via Thanos/Mimir

## Interview Themes

- "Walk me through Prometheus architecture"
- "How do you scale Prometheus to 100M time series?"
- "Pull vs push — why Prometheus pulls"
- "TSDB compression — what's special?"
- "Compare Thanos, Mimir, VictoriaMetrics"
