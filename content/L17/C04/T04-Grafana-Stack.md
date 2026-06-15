# L17/C04/T04 — Grafana Loki, Tempo, Mimir

## Learning Objectives

- Use Grafana stack
- Compare to alternatives

## LGTM Stack

Grafana's observability:
- **L**oki: logs
- **G**rafana: visualization
- **T**empo: traces
- **M**imir: metrics (Cortex fork)

Plus: Pyroscope (profiles).

All open source.

## Loki

Log aggregator:
- Cheap (index labels only, not content)
- LogQL (similar to PromQL)
- Multi-tenant
- S3-backed

## Architecture

```
Promtail (collector) → Loki Distributor → Ingester → S3
Loki Querier ← S3 + Ingester
```

## Promtail

```yaml
scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
```

Per node DaemonSet; reads logs; sends to Loki.

Alternatives: Fluent Bit, Vector, OTel Collector.

## LogQL

Stream selectors:
```
{app="api", env="prod"}
```

Filters:
```
{app="api"} |= "error"
{app="api"} != "debug"
{app="api"} |~ "error|fail"     # regex
{app="api"} | json | status="500"   # parse JSON
```

Metric queries:
```
rate({app="api"}[5m])
sum by (status) (rate({app="api"} | json | __error__="" [5m]))
```

## Tempo

Tracing backend:
- Stores traces in S3
- TraceQL (newer query)
- Compatible with Jaeger, Zipkin, OTel
- Cheap; massive scale

## Architecture

```
App emits traces → OTel Collector → Tempo Distributor → Ingester → S3
Tempo Querier ← S3
```

## TraceQL

```
{ service.name = "api" }
{ duration > 1s }
{ status = error }
{ span.http.status_code = 500 }
```

## Mimir

Prom-compatible TSDB:
- Multi-tenant
- High scale
- Cortex fork

(See L17/C02/T06.)

## Pyroscope

Continuous profiling:
- CPU, memory, etc.
- Pyroscope agent in app
- Flame graphs

```python
import pyroscope
pyroscope.configure(application_name="my-app", server_address="http://pyroscope:4040")
```

## Cost Advantage

Loki:
- Index size: 100× smaller than ELK
- Cost: ~10× cheaper

Tempo:
- S3 backed
- 100% trace storage possible (with sampling)

Pyroscope:
- Continuous profiling at scale

For: cost-conscious observability.

## Vs ELK

| | Loki | ELK |
|---|---|---|
| Index | labels only | full content |
| Query | LogQL (filters) | DSL (rich) |
| Cost | low | high |
| Use case | grep + cardinality | rich search |

For: logs as streams: Loki.
For: complex search: ELK.

## Vs Jaeger

| | Tempo | Jaeger |
|---|---|---|
| Storage | S3 | Cassandra / Elastic |
| Cost | low | high |
| Query | TraceQL | Tag-based |
| Scale | huge | medium |

For: scale + cost: Tempo.

## Vs Datadog

| | LGTM | Datadog |
|---|---|---|
| Cost | infra | $$$ |
| Ops | self-host | none |
| Features | growing | rich |
| Integration | OTel | proprietary + OTel |

For: cost-conscious: LGTM.
For: hands-off: Datadog.

## Grafana Cloud

Hosted LGTM:
- Free tier
- Paid scales
- No ops

For: avoid self-hosting.

## OTel + LGTM

```
App → OTel SDK → OTel Collector → Loki + Tempo + Mimir
```

Unified pipeline.

## Multi-Tenant

Loki / Tempo / Mimir:
- X-Scope-OrgID header
- Isolated per tenant

For: org-wide observability.

## Querying Across

Grafana Explore:
- Logs (Loki)
- Traces (Tempo)
- Metrics (Mimir)

Click metric spike → traces → logs. Correlated via trace_id.

## Loki Storage

```yaml
storage:
  type: s3
  s3:
    bucket: loki-logs
```

Chunks + index in S3.

Retention:
```yaml
table_manager:
  retention_deletes_enabled: true
  retention_period: 720h   # 30 days
```

## Tempo Storage

```yaml
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
```

## Best Practices

- LGTM together
- OTel for instrumentation
- S3 for storage
- Sampling traces
- Loki labels: low cardinality
- Multi-tenant if many teams

## Common Mistakes

- High-cardinality Loki labels
- 100% trace sampling
- Multiple log collectors
- No retention limits

## Quick Refs

```
Loki:       {label="value"} |= "filter"
Tempo:      { service.name = "X", duration > 1s }
Mimir:      PromQL
Pyroscope:  flamegraphs
```

```bash
# Helm
helm install loki grafana/loki-stack
helm install tempo grafana/tempo
helm install mimir grafana/mimir-distributed
helm install pyroscope grafana/pyroscope
```

## Interview Prep

**Mid**: "LGTM stack."

**Senior**: "Loki vs ELK."

**Staff**: "Observability stack choice."

## Next Topic

→ Move to [L17/C05 — Alertmanager](../C05/README.md)
