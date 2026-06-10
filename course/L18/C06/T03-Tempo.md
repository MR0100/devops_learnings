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

**Mid**: "What's Tempo."

**Senior**: "Tempo vs Jaeger."

**Staff**: "Cost-effective tracing."

## Next Topic

→ [T04 — Honeycomb](T04-Honeycomb-Detail.md)
