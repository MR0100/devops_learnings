# L18/C06 — Tracing Tools

## Topics

- **T01 Jaeger** — CNCF graduated
- **T02 Zipkin** — Original (Twitter)
- **T03 Tempo** — Grafana's S3-backed
- **T04 Honeycomb** — Commercial, observability-focused

## Jaeger

CNCF graduated. Originally Uber. Most popular OSS tracer.

### Architecture
```
[Apps] → OTLP/Jaeger thrift
   ↓
[Collector] (writes to storage)
   ↓
[Storage: Cassandra, Elasticsearch, badger (single-node), Kafka]
   ↓
[Query] (web UI)
```

### v2 (Jaeger 2.0+)
- OTel Collector + Jaeger backend, unified
- Reduces complexity

### Features
- Service graph (auto-derived)
- Trace search by tag, duration, service
- Span details with attributes/logs

## Zipkin

Twitter's original (2012). Simpler than Jaeger. Java-based.

- B3 propagation (older standard, predates W3C)
- Smaller community now
- Often replaced by Jaeger or Tempo

## Tempo

Grafana's S3-backed trace store. Cheap.

### Architecture
- Distributor (receive OTLP / Jaeger / Zipkin)
- Ingester (in-memory; flush to S3)
- Querier
- Object storage (S3, GCS)

### Features
- Trace by ID (cheap)
- TraceQL (newer query language for tag-based search)
- Service graph
- Exemplar links (from Prometheus metrics)

### Why Tempo Wins
- Cost: 10× cheaper than Jaeger on Cassandra/ES at the same volume
- Pairs natively with Grafana, Loki
- No external DB to operate

```promql
# Metric chart with exemplars
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
# Click an exemplar dot → opens trace in Tempo
```

## Honeycomb

Commercial. Built around "wide events" model:
- One data type: structured event
- High-cardinality querying
- BubbleUp: auto-find what's different about a failure cohort
- SLO + heatmaps + flame graphs

Premium price for premium UX.

## Comparison

| | Jaeger | Tempo | Zipkin | Honeycomb |
|---|---|---|---|---|
| Storage | Cassandra/ES | Object storage | Cassandra/ES | SaaS column store |
| Cost | $$$ | $ | $$ | $$$ |
| Query (by ID) | Fast | Fast | Fast | Fast |
| Tag search | Yes | TraceQL | Yes | Powerful |
| Service map | Yes | Yes | Limited | Yes |
| OTel native | Yes | Yes | Yes | Yes |
| Best for | Mature OSS, K8s | Cost + Grafana stack | Heritage | Mature obs culture |

## Service Maps

Auto-derived from spans (parent-child + service.name attribute):
```
[Frontend] ─→ [Order Svc] ─→ [Payment Svc] ─→ [Stripe]
                           ─→ [Inventory Svc] ─→ [DB]
```

Useful for: dependency awareness, blast radius, capacity planning.

## Common Operations

### Query by trace ID
- From logs (clicked trace_id → trace UI)
- From alerts ("first slow trace was XYZ")
- From customer support (provide trace_id with their ticket)

### Find slow traces
- "Show me traces > 1s on /checkout in last hour"
- TraceQL: `{ resource.service.name="checkout" && duration > 1s }`

### Find error traces
- "All ERROR-status traces touching payment service"

## Sizing (Tempo)

- ~1 GB ingester memory per 100K active traces
- S3 storage: ~5 KB per trace = $0.115/TB/month
- 1M traces/day × 30 days × 5 KB = 150 GB = $0.018/month storage
- Compare to ELK same volume: $10K+/month

## Operations

### Trace Loss
- Ingester crash before flush
- Network drop on sampling
- Some loss is acceptable (you've already sampled)

### Storage Growth
- Set retention (Tempo: time-based, e.g., 30 days)
- Tail sample to keep what matters

### Performance
- Sub-second query for trace by ID
- Multi-second for tag search (depends on indexed fields)

## Interview Themes

- "Compare Jaeger and Tempo"
- "Why is Tempo cheaper?"
- "Service map — how derived?"
- "TraceQL examples"
- "When commercial APM over OSS?"
