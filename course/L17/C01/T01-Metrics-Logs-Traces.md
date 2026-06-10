# L17/C01/T01 — Metrics, Logs, Traces

## Learning Objectives

- Understand three pillars
- Use each correctly

## The Three Pillars

### Metrics
Numeric measurements over time:
- Counter (requests_total)
- Gauge (cpu_percent)
- Histogram (latency)
- Summary

### Logs
Discrete event records:
```json
{"timestamp": "...", "level": "error", "message": "DB query failed"}
```

### Traces
Request flow across services:
```
Span: API gateway
  Span: Auth service
  Span: Backend
    Span: DB query
```

## When Each

### Metrics
- High-cardinality summary
- Alerting (thresholds)
- Trends
- Dashboards

### Logs
- Debug details
- Audit trail
- Exceptions
- Forensics

### Traces
- Cross-service latency
- Causal chains
- Distributed debugging
- Bottleneck location

## Cost

| | Storage | Cardinality |
|---|---|---|
| Metrics | low/GB | low |
| Logs | medium/GB | high |
| Traces | high/GB | very high |

For: trade-off.

## Tools

### Metrics
- Prometheus
- Datadog
- New Relic
- CloudWatch
- VictoriaMetrics

### Logs
- Loki
- ELK
- Splunk
- Datadog Logs
- CloudWatch Logs

### Traces
- Jaeger
- Tempo
- Datadog APM
- Honeycomb
- X-Ray

## Correlation

Best:
- Same trace_id across all
- Logs linked to trace
- Metrics tagged with trace

Tools: OpenTelemetry.

## RED Method

For services:
- **R**ate: requests/sec
- **E**rrors: errors/sec
- **D**uration: latency

For: service health summary.

## USE Method

For resources:
- **U**tilization: % used
- **S**aturation: queue length
- **E**rrors: failures

For: infrastructure health.

## Cardinality

Metrics: keep low.
- Per-service OK
- Per-user: bad (millions of series)

Labels:
```
http_requests_total{service="api", code="200", method="GET"}
```

Don't add `user_id`, `request_id` to metrics.

## Logs: Structured

```json
{
  "ts": "2026-01-01T00:00:00Z",
  "level": "error",
  "service": "api",
  "trace_id": "abc",
  "msg": "DB failed",
  "err": "connection refused"
}
```

Searchable; parseable.

Bad: plain text.

## Logs: Volume

Cost grows fast. Strategies:
- Sample (1% of debug)
- Filter (drop noise)
- Retain short (7 days hot)
- Archive cold

## Traces: Sampling

100% expensive. Sample:
- Head (decide at start)
- Tail (decide at end; capture errors)
- Probabilistic (1%)

Production: ~1-5%.

## Three Pillars Critique

Charity Majors: "observability is high-cardinality, high-dimensionality."

Argument:
- Metrics are aggregates (lose detail)
- Traces capture cardinality
- Combine for deeper

For: think beyond pillars.

## Wide Events

Honeycomb model: emit per-request event with many dimensions.

For: query later. Don't pre-aggregate.

```json
{
  "trace_id": "abc",
  "service": "api",
  "endpoint": "/users",
  "user_id": 123,
  "tenant_id": 456,
  "latency_ms": 50,
  "status": 200,
  "db_queries": 3,
  "cache_hits": 2,
  "feature_flags": {...}
}
```

For: ad-hoc queries.

## SLO Driven

Use metrics for SLO:
- 99.9% requests succeed
- p99 latency < 500ms

(See L17/C08.)

## OpenTelemetry

Standard for emitting:
- Metrics
- Logs
- Traces

Vendor-agnostic.

(See L17/C06.)

## Best Practices

- Metrics for trends + alerts
- Traces for cross-service
- Logs for detail
- Correlate via trace_id
- Structured logs
- Sample traces
- Low-cardinality metrics

## Common Mistakes

- High-cardinality metrics (Prometheus OOM)
- Unstructured logs (unsearchable)
- 100% traces (cost)
- No correlation (debug pain)

## Tools per Layer

```
Metrics: Prometheus + Grafana
Logs:    Loki / ELK
Traces:  Tempo / Jaeger

OR

Commercial: Datadog / New Relic / Honeycomb
```

## Cost Comparison

Open source (Prom/Loki/Tempo): cheaper, ops.
Commercial: pricier, less ops.

For: scale + team.

## Real Usage

### Netflix
Custom + open source.

### Stripe
Custom; metrics-heavy.

### Cloudflare
Massive scale; custom + Prometheus.

## Quick Refs

```
Metrics: prom_http_requests_total{code="200"}
Logs:    JSON structured
Traces:  span context propagated
```

## Interview Prep

**Junior**: "Three pillars."

**Mid**: "When each."

**Senior**: "Cardinality concerns."

**Staff**: "Observability strategy."

## Next Topic

→ [T02 — Profiles as the 4th Pillar](T02-Profiles.md)
