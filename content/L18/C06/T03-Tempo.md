# L18/C06/T03 — Tempo

## Learning Objectives

- Use Tempo
- Compare to Jaeger

## Tempo

Grafana Labs; tracing backend:
- S3 / GCS / Azure backed
- Cheap (object storage)
- LogQL-like TraceQL
- High throughput

## Install

```bash
helm install tempo grafana/tempo
```

## Architecture

- **Distributor**: receives + load balances
- **Ingester**: writes
- **Querier**: reads
- **Compactor**: optimizes blocks
- **Querier-frontend**: query splitting

S3 backend.

## Send

OTel:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
```

Or Jaeger / Zipkin / OTLP protocols.

## TraceQL

```
{ service.name = "api" }
{ duration > 1s }
{ status = error }
{ span.http.status_code = 500 }
{ resource.cluster = "us-east-1" }
```

For: search.

## Storage

```yaml
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: s3.amazonaws.com
```

Cheap; massive scale.

## Cost

For 1B spans/month:
- Jaeger (Cassandra): high $
- Tempo (S3): low $$

Order of magnitude cheaper.

## Performance

Query latency:
- Trace ID lookup: ms
- Search (TraceQL): seconds for large

For: trade-off vs Jaeger.

## Multi-Tenant

```
X-Scope-OrgID: team-a
```

Per-tenant isolation.

## Sampling

Tempo accepts all spans (no built-in sampling).

Sample at:
- App SDK
- OTel Collector (tail)

## Service Map

Auto from traces.

## Grafana Integration

Trace datasource:
- Click trace_id in logs → Tempo
- Service graph
- Metrics from traces

## Span Metrics

Generate metrics from traces:
- `traces_spanmetrics_calls_total`
- `traces_spanmetrics_latency_bucket`

For: RED metrics from spans.

## Service Graph Metrics

```
traces_service_graph_request_total{client="api",server="db"}
```

Topology emerges.

## When Tempo

- Cost-conscious
- LGTM stack
- S3-backed wanted
- High volume

## When Jaeger

- Need rich UI native
- Existing investment
- K8s-native Operator

## When Honeycomb / Datadog

- Hosted
- High-cardinality
- Rich query

## Vparquet (Newer Format)

Tempo storage format:
- Apache Parquet
- Better query performance
- Multi-tenant

## Best Practices

- OTel SDK
- Tail sampling in Collector
- S3 lifecycle (cleanup)
- Grafana integration
- TraceQL for search

## Common Mistakes

- 100% spans (storage)
- No sampling
- Wrong region (latency)
- Old format (use vparquet)

## Quick Refs

```yaml
storage:
  trace:
    backend: s3
    s3: ...

# OTel
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317

# TraceQL
{ service.name = "X", duration > 1s }
```

## Interview Prep

**Junior**: "What is Tempo?" — Grafana Labs' distributed-tracing backend that stores traces in object storage (S3/GCS/Azure), making it cheap and highly scalable, and queries them with TraceQL inside Grafana.

**Mid**: "How does Tempo keep cost so low?" — It backs everything with object storage instead of Cassandra/ES and ingests all spans without its own sampling, so for very high span volume it's roughly an order of magnitude cheaper than Jaeger on Cassandra; you sample upstream in the SDK or OTel Collector.

**Senior**: "Tempo vs Jaeger — when each?" — Tempo for cost-conscious, high-volume tracing in an LGTM/Grafana stack with S3 storage and TraceQL; Jaeger when you want a rich native UI, a K8s Operator, or an existing investment — Tempo historically leaned on fast trace-ID lookup and has since added richer TraceQL search.

**Staff**: "How do you build cost-effective tracing at scale with Tempo?" — Sample in the Collector (tail-sample to keep errors/slow), store in S3 with lifecycle cleanup, use the vParquet format for faster search, generate span/service-graph metrics so you get RED and topology without keeping every trace hot, and wire Grafana correlation (logs↔traces↔metrics) so the cheap storage still gives a fast investigation path.

## Next Topic

→ [T04 — Honeycomb](T04-Honeycomb-Detail.md)
