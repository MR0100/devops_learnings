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

Samples/sec and active series are **independent** quantities — one does not cause the other. They are linked by the scrape interval:

```
samples/sec = active_series / scrape_interval_seconds
```

So derive, don't assert. Given a 1M samples/sec ingest target and a 15s scrape interval:

```
active_series = samples/sec × scrape_interval
             = 1,000,000 × 15
             = 15M active series
```

Halve the scrape interval to 30s and the **same** 15M series produce only 0.5M samples/sec; tighten it to 10s and you get 1.5M samples/sec. The interview point: state your scrape interval explicitly, then either quantity follows from the other. Active-series count drives **memory** (each series ≈ a few KB resident in the ingester head block); samples/sec drives **CPU and write bandwidth**. Size them separately:
- Sharded ingest (capacity scales with samples/sec)
- Memory headroom (capacity scales with active series)
- Cluster-wide query (fan-out scales with series touched)

For 10 TB logs/day, derive the storage and ingest cost:
```
raw_logs/day      = 10 TB
compression       ≈ 3–4×  (Loki chunks / gzip)
stored/day        ≈ 10 TB / 3.5 ≈ 3 TB compressed → S3
ingest_rate       = 10 TB / 86,400 s ≈ 120 MB/s sustained
```
Loki indexes only labels (not full text), so the index stays small and the bulk lands cheaply in S3 — that's the cost lever. Keep label cardinality low or the index explodes (the logging analogue of the metrics cardinality problem).

For traces, sample because storing every span is infeasible — derive the stored rate:
```
spans/sec         = 100,000 traces/sec   (assumed)
sample_rate       = 5%   (tail-based: keep errors + slow traces)
stored/sec        = 100,000 × 0.05 = 5,000 traces/sec
```
Tail sampling (decide after the trace completes) keeps the *interesting* traces — errors and high-latency — unlike head sampling, which decides blindly at ingest. The cost: the sampler must buffer spans until the trace finishes, which needs memory and a gateway tier.

## Multi-Tenancy

Per team:
- Own namespace / org
- Quotas
- Isolation

## Deep Dive: Cost & Tiering

Storage dominates the bill at this scale, so tier by access pattern:
- **Hot (recent, queried constantly)**: in-memory ingester head blocks + SSD-backed object cache. Expensive per GB but small window (e.g. last few hours).
- **Warm**: S3 standard for the 7-day query window — most queries hit here.
- **Cold**: S3 Glacier / IA for the 2-year compliance tail — cheap, rarely read, restore latency acceptable.

The **compactor** is the cost engine: it merges small blocks into large ones, deduplicates replicated samples, and downsamples old data (5m/1h resolution for year-old metrics nobody queries at 15s granularity). Without it, 2-year retention is ~10 PB; with downsampling + compaction it's a fraction of that. Per-tenant cardinality limits cap the worst-case blast so one team can't 10× the bill.

## Deep Dive: HA & No SPOF

- **Ingest**: replication factor 3 across ingesters (Mimir/Thanos Receive) — a sample is written to 3 replicas, so losing one ingester loses nothing. Quorum write means an ack survives a node crash.
- **Query**: queriers are stateless and horizontally scaled; the query-frontend splits and caches queries so a single huge query can't take down the path.
- **Buffering**: agents (or Kafka in front) buffer on `remote_write` failure so a transient receiver outage doesn't drop data — backpressure, not loss (C03/T02).
- **Object store**: S3 is the durable backstop; if ingesters all restart, data is rehydrated from S3, not lost.

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

**Mid**: "Why push (remote_write) instead of pull at scale?" — Pull means a central Prometheus must discover and scrape tens of thousands of targets, which doesn't fan out and creates a scaling and networking nightmare across clusters. Push has each cluster's Prometheus scrape locally and `remote_write` to a central receiver tier, which scales horizontally and survives network blips by buffering.

**Senior**: "Size a metrics pipeline for 1M samples/sec." — First separate the two independent quantities: samples/sec = active_series / scrape_interval, so at a 15s interval 1M samples/sec implies ~15M active series. Samples/sec drives CPU and shard count (~10 ingesters at 100k/s each); active series drive ingester memory. I'd use Mimir/Thanos with replication factor 3, S3 for retention, a compactor for downsampling, and per-tenant cardinality limits to cap blast radius.

**Staff**: "A team's cardinality just exploded and is threatening the whole cluster — what happens?" — Per-tenant series limits reject the offending tenant's new series and alert them, while everyone else keeps ingesting — the limit is the blast-radius firewall. I'd surface a cardinality dashboard so they can find the offending label (usually an unbounded one like user_id or request_id in a label), and the replication-factor-3 + S3 design means even an ingester OOM doesn't lose committed data. The lesson is that cardinality, not raw volume, is the thing that kills metrics systems.

**Principal**: "Design the whole observability platform — metrics, logs, traces — at Datadog-ish scale and keep the bill sane." — One OTel collection tier (agent + gateway) feeding the LGTM stack: Mimir for metrics, Loki for logs (label-indexed, body in S3), Tempo for traces with tail-based sampling. Cost control is the design: tier storage (hot SSD → warm S3 → cold Glacier), downsample old metrics via the compactor, sample traces (keep errors/slow), and enforce per-tenant quotas on series, log volume, and trace rate. Multi-tenancy is native (Mimir/Loki orgs) so teams are isolated, and everything buffers on `remote_write` failure so transient outages mean delay, not data loss.

## Next Topic

→ [T04 — Design a Secrets Management Platform](T04-Design-Secrets-Platform.md)
