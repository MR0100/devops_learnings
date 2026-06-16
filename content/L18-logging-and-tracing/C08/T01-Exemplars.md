# L18/C08/T01 — Exemplars

## Learning Objectives

- Use exemplars
- Jump metric → trace

## Exemplar

Metric sample paired with trace_id:
```
http_request_duration_seconds_bucket{le="0.5"} 100 # {trace_id="abc"} 0.45 1700000000
```

For: from metric chart → specific trace.

## Why

Metric: aggregate; loses request detail.
Trace: per-request.

Exemplar: bridge.

## Workflow

```
1. Spike in p99 latency
2. Click exemplar dot in Grafana
3. Open trace for that request
4. See spans + bottleneck
```

For: faster debug.

## Prometheus Support

Histogram metrics with exemplars:
```
# HELP http_request_duration Histogram
# TYPE http_request_duration histogram
http_request_duration_bucket{le="0.5"} 100 # {trace_id="abc"} 0.45
http_request_duration_bucket{le="1.0"} 150 # {trace_id="def"} 0.95
http_request_duration_sum 75
http_request_duration_count 200
```

Random sample of requests get exemplar.

## App Emits

OTel:
```python
from opentelemetry import metrics, trace

meter = metrics.get_meter(__name__)
hist = meter.create_histogram("http_request_duration")

with tracer.start_as_current_span("handle") as span:
    start = time.time()
    # ... handle ...
    duration = time.time() - start
    hist.record(duration, {"endpoint": "/api"})
    # Exemplar auto-attached with current trace_id
```

## Grafana View

In histogram panel:
- Dots = exemplars
- Click → trace view

For: visual jump.

## Tempo Integration

Grafana datasource linked:
```yaml
tempoSearch:
  hide: false
tracesToLogs:
  datasourceUid: loki
  tags: ['k8s.pod.name']
```

Trace ↔ logs ↔ metrics.

## OpenMetrics

```
http_requests_total 100
# {trace_id="abc", span_id="def"} 100 1700000000
```

OpenMetrics format supports exemplars.

## Limits

- Sampled (not every event)
- Storage overhead small
- Visual hint, not full data

## Native Histograms (Newer)

Prometheus native histograms:
- Better than bucket
- Exemplars supported

## Use Cases

### Slow Request
Latency spike → click exemplar → see why.

### Error
Error metric spike → exemplar → error trace.

### Database
DB query time spike → exemplar → query trace.

## Tools

- Prometheus (storage)
- Grafana (visualization)
- Tempo / Jaeger (trace backend)

## Implementation

```go
// Go
import "go.opentelemetry.io/otel/metric"

histogram, _ := meter.Float64Histogram("http_request_duration")

func handle(ctx context.Context) {
    span := trace.SpanFromContext(ctx)
    // ...
    duration := time.Since(start)
    histogram.Record(ctx, duration.Seconds())
    // OTel auto-attaches exemplar with span context
}
```

## Configuration

```bash
# Enable exemplars in Prometheus
--enable-feature=exemplar-storage

# In Grafana datasource
exemplarTraceIdDestinations:
  - name: trace_id
    datasourceUid: tempo
```

## Best Practices

- Histograms with exemplars
- Tempo as trace backend
- Grafana for jumping
- Sampling for storage

## Common Mistakes

- Counters w/o exemplars (use histogram)
- Exemplars but no trace backend (dead link)
- 100% exemplars (storage)

## Quick Refs

```
Metric:
  http_request_duration_bucket{le="0.5"} 100 # {trace_id="X"} 0.45

App:
  histogram.Record(value)
  (with active span context)

Grafana:
  Click exemplar dot → trace view
```

## Interview Prep

**Junior**: "What is an exemplar?" — A metric sample annotated with a `trace_id` (and timestamp), so a point on a histogram bucket links to one specific request's trace — the bridge from aggregate metric to individual example.

**Mid**: "How do exemplars get from app to chart?" — When the app records into a histogram inside an active span, OTel attaches the current `trace_id` as an exemplar; Prometheus stores it (with exemplar storage enabled) and Grafana renders it as a clickable dot that opens the trace in Tempo/Jaeger.

**Senior**: "Walk through using exemplars in an investigation." — A p99 latency spike on a dashboard shows exemplar dots; you click one, jump straight to that request's trace, and see which span (e.g. a slow DB call) caused it — turning an aggregate anomaly into a concrete root cause in seconds.

**Staff**: "Where do exemplars fit in an observability-correlation strategy?" — They're the cheap, high-value metric→trace link that makes the three pillars navigable; pair them with histograms (counters can't carry them), a real trace backend so the link isn't dead, `trace_id` in logs for the next hop, and sampling so exemplar storage stays bounded.

## Next Topic

→ [T02 — Trace IDs in Logs](T02-Trace-IDs-in-Logs.md)
