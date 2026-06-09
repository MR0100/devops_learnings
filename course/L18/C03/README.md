# L18/C03 — Loki

## Topics

- **T01 Architecture** — Distributor, Ingester, Querier
- **T02 LogQL** — Query language
- **T03 Cost Tradeoffs vs ELK** — When Loki wins

## Why Loki

> "Like Prometheus but for logs"

- Indexes only **labels** (low cardinality), not log content
- Stores logs in object storage (S3, GCS, Azure Blob) — cheap
- Query language inspired by PromQL
- Pairs with Grafana

Result: 10-100× cheaper than ELK at similar log volume.

## Architecture

```
[Promtail / Fluent Bit / Vector] (log shippers, push)
   ↓
[Loki Distributor] (validates, routes)
   ↓
[Loki Ingester] (in-memory + flush to object storage)
   ↓ blocks
[Object storage: S3 / GCS / Azure Blob]
   ↑
[Loki Querier] (reads recent from ingesters; older from object storage)
   ↑
[Grafana] (queries via LogQL)
```

### Components in Microservice Mode
- Distributor — receives + distributes to ingesters
- Ingester — buffers in memory, flushes to object storage
- Querier — answers queries (recent from ingesters, older from storage)
- Compactor — merges old blocks
- Ruler — evaluates alerting rules on logs

In monolithic mode, all in one binary.

## Streams

A stream is a unique combo of labels:
```
{job="myapp", level="error", instance="pod-1"} → one stream
{job="myapp", level="info", instance="pod-1"}  → another stream
```

Loki indexes only the labels. The log line itself is stored as-is.

### Cardinality Rules
- Use labels for: service, env, level, namespace, pod
- DON'T use as labels: user_id, trace_id, request_id, IP (high cardinality → millions of streams)

## LogQL

```logql
{service="api"}                                           # all logs from service api
{service="api"} |= "error"                                # contains "error"
{service="api"} |~ "5\\d\\d"                               # regex
{service="api"} != "healthz"                              # NOT contains
{service="api"} |~ "error|warn"                           # regex match

# Parse JSON
{service="api"} | json | level="error"

# Parse logfmt
{service="api"} | logfmt | error_code="card_declined"

# Aggregations (metric queries)
sum by (level) (rate({service="api"}[5m]))                # logs/sec by level
count_over_time({service="api"} |= "error" [5m])          # errors in last 5m

# Pattern extraction
{service="api"} | pattern `<level> <_> <msg>` | level="error"

# unwrap for numeric aggregation
sum_over_time(
  {service="api"} | json | unwrap duration_ms [5m]
)
```

## Promtail

Loki's log shipper (Go).

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: [__meta_docker_container_name]
        target_label: container

  - job_name: kubernetes
    kubernetes_sd_configs:
      - role: pod
    pipeline_stages:
      - cri: {}
      - json:
          expressions:
            level: level
            msg: msg
            trace_id: trace_id
      - labels:
          level:
      - timestamp:
          source: time
          format: RFC3339Nano
```

Many teams use Fluent Bit / Vector instead — more flexible.

## Loki vs ELK

| | Loki | ELK |
|---|---|---|
| Index | Labels only | Full text |
| Storage | Object (cheap) | Disk (expensive) |
| Query | LogQL | KQL/Lucene |
| Resource cost | Low | High |
| Full-text search | Substring/regex (linear over filtered streams) | Native (sublinear) |
| Aggregations | Some | Excellent |
| Mature | Growing | Very mature |

## When Loki Wins
- High volume (TBs/day)
- Most queries are label-filtered → text grep
- Cost-sensitive
- Already on Grafana stack

## When ELK Wins
- Heavy full-text search
- Complex aggregations
- Need to search by extracted fields (without parsing in query)

## Hybrid
Loki for high-volume routine logs; ELK for security/audit logs that need rich search.

## Sizing

Production rule:
- Distributor: 2 vCPU per 1M lines/sec
- Ingester: 1 vCPU + 1 GB RAM per ~50K active streams
- Object storage: per-GB cost very low

## Loki on K8s

```bash
helm install loki grafana/loki -n loki -f values.yaml
helm install promtail grafana/promtail -n loki
```

Or use Loki Stack (Loki + Promtail + Grafana datasource).

## Operations Gotchas

- **Stream explosion** (high-cardinality labels) → index unusable
- **Bad timestamps** (clock skew, parsing failure) → ingester rejects
- **Cardinality limits** (default 10K streams per tenant)
- **Rate limits** (request lines/MB per second per tenant)

## Interview Themes

- "Loki vs ELK"
- "Cardinality discipline in Loki — what fails?"
- "LogQL examples"
- "How does Loki achieve cost savings?"
- "When mix ELK and Loki?"
