# L18/C08 — Correlating Logs, Metrics, Traces

## Topics

- **T01 Exemplars** — Link from metric to trace
- **T02 Trace IDs in Logs** — Link from log to trace
- **T03 Unified Query Experiences** — Single-pane investigation

## The Correlation Problem

Each pillar is separately powerful. Real observability is jumping between them:
- See metric anomaly → jump to trace example → jump to logs of that trace

If pillars don't link, investigation takes 10× longer.

## Exemplars

Annotations on Prometheus histogram buckets with example trace IDs.

```
# A specific request that fell in the [le=0.5] bucket
http_request_duration_seconds_bucket{le="0.5"} 1234 # {trace_id="abc..."} 0.45 @1717920000
```

In Grafana, latency chart shows dots at exemplar locations. Click dot → opens trace in Tempo/Jaeger.

### How to Emit Exemplars

#### Go
```go
hist := prometheus.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Buckets: prometheus.DefBuckets,
    },
    []string{"path"},
)

// On request completion
hist.WithLabelValues("/checkout").(prometheus.ExemplarObserver).
    ObserveWithExemplar(duration, prometheus.Labels{
        "trace_id": currentTraceID,
    })
```

#### Auto via OTel SDK
OTel SDK can attach exemplars from spans to metrics automatically.

## Trace IDs in Logs

Always emit trace_id and span_id in structured logs:
```json
{
  "ts": "...",
  "msg": "DB query slow",
  "duration_ms": 800,
  "trace_id": "abc...",
  "span_id": "def..."
}
```

In Loki / Datadog / Splunk, filter logs by trace_id to see all logs from one request.

### Auto via OTel
- Java: OTel's logback bridge auto-injects MDC
- Python: structlog's `bind_contextvars` integration
- Go: explicit, via context propagation + log helper

### Pattern
```go
func loggerForCtx(ctx context.Context) *slog.Logger {
    span := trace.SpanFromContext(ctx)
    return slog.With(
        "trace_id", span.SpanContext().TraceID().String(),
        "span_id",  span.SpanContext().SpanID().String(),
    )
}
```

## Unified Query in Grafana

Grafana's "Explore" mode:
- Datasource picker (Prometheus, Loki, Tempo, Pyroscope)
- Link from one to another via trace_id

### Loki → Tempo
LogQL result has `trace_id` field. Click → opens trace.

### Tempo → Loki
Trace details show "logs for this trace" → opens Loki query filtered by trace_id.

### Tempo → Pyroscope
Span details show "view profile" → opens Pyroscope at that pod/time.

### Prometheus → Tempo
Click exemplar dot → opens trace.

## Datadog / New Relic / Honeycomb

Commercial APMs make correlation invisible — all data in one platform.

- Click error rate spike → drill to failing traces
- Click slow trace → see logs filtered by trace
- See related profile flame graph

This is the major UX advantage over self-hosted stacks (though Grafana is catching up).

## What "Single Pane of Glass" Actually Means

```
1. Alert fires (Prometheus + Alertmanager)
   "p99 latency on /checkout > 1s"
2. Dashboard shows metric + exemplars
   Click exemplar (slow trace)
3. Tempo shows trace
   See: DB call took 800ms in span "fetch-order"
4. Click "logs for this trace"
   Loki shows: slow query log with SQL text
5. Click "profile for this pod / time"
   Pyroscope shows hot code path during incident
```

Investigation went from alert → root cause in 5 minutes. Without correlation: maybe 50 minutes.

## Practical Tips

### Trace ID Everywhere
- Logs (always)
- Customer-facing errors (so user can include in support ticket)
- HTTP response headers (`X-Request-Id` or `traceparent`)
- Slow query logs (database)
- Internal queues (carry trace_id)

### Test the Plumbing
- Trigger a slow request, manually verify:
  - Trace shows up in Tempo
  - Logs contain trace_id
  - Logs queryable by trace_id
  - Metric exemplar exists
  - Click-through works

Most teams have broken correlation they didn't realize.

### Cross-Service Propagation
- Verify trace context propagates through:
  - HTTP calls (auto via OTel)
  - gRPC calls (auto)
  - Kafka / SQS (manually inject in message headers)
  - Async batch jobs (carry trace context)

## Cost vs Value

Full correlation requires emitting many fields per event. Cost-conscious teams:
- Trace IDs in 100% of logs (cheap)
- Exemplars on 100% of metrics (cheap)
- Tail-sample traces (only keep interesting)
- Profile continuously at low rate

## Interview Themes

- "How do you correlate logs, metrics, traces?"
- "What's a Prometheus exemplar?"
- "Walk me through investigating an incident with all four pillars"
- "Trace context through Kafka — how?"
- "Why is single-pane-of-glass UX important?"
