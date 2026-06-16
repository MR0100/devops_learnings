# L17/C02/T01 — Prometheus Architecture

## Learning Objectives

- Install Prometheus
- Understand components

## Components

- **Prometheus Server**: scrape + TSDB
- **Pushgateway**: push for short-lived jobs
- **Alertmanager**: handle alerts
- **Exporters**: expose metrics (node_exporter, etc.)
- **Client libraries**: app instrumentation

## Pull Model

Prometheus scrapes targets:
```
prometheus → HTTP GET /metrics → target
```

Every 15s (typical).

For: app exposes endpoint; Prom polls.

## Install

```bash
# Docker
docker run -p 9090:9090 -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

# Helm (K8s)
helm install prom prometheus-community/kube-prometheus-stack
```

## Config

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['node1:9100', 'node2:9100']

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

## Storage

TSDB (Time Series Database):
- Local disk
- Block-based (2h then merged)
- Compressed
- Retention: 15 days default

## /metrics Endpoint

```
# HELP http_requests_total Total requests
# TYPE http_requests_total counter
http_requests_total{method="GET",code="200"} 1234
http_requests_total{method="GET",code="500"} 5

# HELP process_resident_memory_bytes Resident memory
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 12345678
```

## Metric Types

### Counter
Monotonic; only goes up:
```
http_requests_total
```

Use `rate()` for per-sec.

### Gauge
Can up/down:
```
memory_usage_bytes
queue_size
```

### Histogram
Buckets + sum + count:
```
http_request_duration_bucket{le="0.1"} 100
http_request_duration_bucket{le="0.5"} 200
http_request_duration_bucket{le="1.0"} 250
http_request_duration_sum 50.5
http_request_duration_count 250
```

For: p95/p99 via quantile().

### Summary
Quantiles computed in app:
```
http_request_duration{quantile="0.5"} 0.2
http_request_duration{quantile="0.99"} 1.5
```

Less flexible than histogram.

## Exporters

Pre-built:
- **node_exporter**: host metrics
- **cAdvisor**: container
- **kube-state-metrics**: K8s state
- **postgres_exporter**: Postgres
- **redis_exporter**: Redis
- Many more

## Alertmanager

Receives alerts; routes:
- Slack
- PagerDuty
- Email
- Webhook

(See L17/C05.)

## High Availability

```
Prometheus A    Prometheus B   (both scrape; redundant)
       ↓               ↓
   Alertmanager (cluster mode; dedupe)
```

For: redundancy.

## Federation

Larger Prom scrapes from smaller:
```yaml
- job_name: 'federation'
  honor_labels: true
  metrics_path: '/federate'
  params:
    'match[]':
      - '{job="api"}'
  static_configs:
    - targets: ['prom-team-1:9090', 'prom-team-2:9090']
```

For: scale across teams.

## Remote Write

Stream metrics to long-term:
```yaml
remote_write:
  - url: https://thanos-receive.example.com/api/v1/receive
```

For: cross-region, long retention.

## Cardinality

Each unique label combination = series.
```
http_requests_total{service="api", method="GET", code="200"}
http_requests_total{service="api", method="GET", code="500"}
```

Avoid:
- user_id labels
- request_id labels

Millions of series → OOM.

## TSDB Internals

- Blocks: 2h chunks
- WAL: write-ahead log
- Compaction: merge blocks
- Retention: delete old

## Resource Sizing

For 1M series:
- ~10-15 GB RAM
- ~50-100 GB disk (15d retention)

Larger: shard or use Thanos.

## Service Discovery

(See T02.)
- K8s SD
- Consul SD
- File SD
- DNS SD
- EC2/GCE SD

## Best Practices

- Sensible scrape interval (15s)
- node + cAdvisor + kube-state-metrics
- Cardinality limits
- HA pairs
- Alertmanager cluster
- Long-term via Thanos / Mimir
- Tag with cluster / env

## Common Mistakes

- High cardinality labels (OOM)
- One Prom for everything (scale)
- No HA (gaps during restart)
- Short retention without remote
- Manual rules (use kube-prometheus-stack)

## Quick Refs

```bash
# Endpoints
GET /metrics          # exposed by target
GET /-/healthy        # liveness
GET /-/ready          # readiness
GET /api/v1/query     # query
GET /api/v1/query_range
GET /api/v1/targets

# CLI
promtool check config prometheus.yml
promtool check rules alerts.yml
```

## Interview Prep

**Junior**: "Prometheus."

**Mid**: "Pull vs push."

**Senior**: "Cardinality + scale."

**Staff**: "Prometheus at scale."

## Next Topic

→ [T02 — Service Discovery](T02-Service-Discovery.md)
