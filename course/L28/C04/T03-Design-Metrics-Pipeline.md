# L28/C04/T03 — Design a Metrics/Logging Pipeline at Scale

## Learning Objectives

- Design observability pipeline
- High throughput

## Requirements

### Functional
- Collect metrics, logs, traces
- Query
- Alert
- Long retention

### Non-Functional
- 1M metrics/sec
- 10 TB logs/day
- < 5 min query latency
- Years retention

## Components

### Collectors
- Prometheus (scrape)
- Fluent Bit / Vector (logs)
- OTel Collector

### Transport
- Kafka (buffer)
- Or remote write direct

### Storage
- Metrics: Mimir / Thanos / VictoriaMetrics
- Logs: Loki / ELK
- Traces: Tempo / Jaeger

### Query
- Prometheus / Grafana
- Search UI

### Alerting
- Alertmanager
- PagerDuty

## Architecture

```
Apps → OTel SDK → OTel Collector (agent + gateway)
                        ↓
               Kafka (buffer for logs)
                        ↓
               Mimir + Loki + Tempo
                        ↓
                    Grafana
                        ↓
                    Alertmanager
```

## Scale Numbers

For 1M metrics/sec:
- ~2-3M time series active
- Sharded ingest
- Cluster-wide query

For 10 TB logs/day:
- Loki: ~3 TB compressed
- S3 backed
- Multi-tenant

For traces:
- Tail sample 1-5%
- ~5% × 100k traces/sec = 5k stored/sec

## Multi-Tenancy

Per team:
- Own namespace / org
- Quotas
- Isolation

## Cost

- Hot store: SSD
- Cold: S3
- Tiered

Major cost: storage. Optimize.

## HA

- Ingest replicated
- Query distributed
- No SPOF

## Real Examples

### Cloudflare
ClickHouse, custom.

### Datadog
Commercial; own architecture.

### Many cloud-native
Grafana stack (LGTM).

## Trade-Offs

- Native vs commercial
- Self-host vs SaaS
- Detail vs cost

## Best Practices

- Sample traces
- Tier storage
- Per-team quotas
- Long-term off hot

## Common Mistakes

- All hot (cost)
- No sampling (huge volume)
- Single replica
- No quotas

## Quick Refs

```
Collectors: Prometheus, OTel, Fluent Bit
Transport: Kafka
Storage: Mimir / Loki / Tempo
Query: Grafana
Alert: Alertmanager
```

## Interview Prep

**Senior**: "Design metrics pipeline."

**Staff**: "Scale to 1M/sec."

**Principal**: "Observability platform."

## Next Topic

→ [T04 — Design a Secrets Management Platform](T04-Design-Secrets-Platform.md)
