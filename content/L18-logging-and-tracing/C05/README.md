# L18/C05 — Tracing Fundamentals

## Topics

- **T01 Spans, Traces, Context Propagation** — Core model
- **T02 W3C Trace Context** — Standard headers
- **T03 Sampling (Head vs Tail)** — How to keep volume manageable

## Core Concepts

```
Trace
└── Root Span: GET /checkout (450ms total)
    ├── Span: validate-user (5ms)
    ├── Span: fetch-cart (35ms)
    │   └── Span: redis-get (3ms)
    ├── Span: charge-payment
    │   └── Span: stripe-api-call (350ms)
    └── Span: send-confirmation
        └── Span: ses-send-email (45ms)
```

### Span
- An operation: name, start, end, attributes, events, status
- Parent-child relationships form a tree
- One span has: trace_id (groups), span_id (this), parent_span_id

### Trace
- A complete request flow
- All spans sharing the trace_id

### Context Propagation
When service A calls service B, A injects trace context into the request (HTTP headers). B extracts it and continues the trace.

## W3C Trace Context

The standard for cross-service propagation. Two HTTP headers:

```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
             │  │                                │                │
             │  trace_id (16 bytes hex)          parent_id (8 b)  flags
             │
             version (00 = current)

tracestate: vendor1=value1,vendor2=value2     (vendor-specific extensions)
```

Every modern tracing SDK uses these headers (OTel, Jaeger, Zipkin all support).

## Attributes

Key-value metadata on spans (semantic conventions in L17/C06):
```
http.method = "GET"
http.route = "/api/users/{id}"
http.status_code = 200
db.system = "postgresql"
db.statement = "SELECT * FROM users WHERE id = $1"
db.user_id = 42                                   # custom
```

## Events

Time-stamped log lines within a span:
```
span.add_event("cache miss")
span.add_event("retrying", attributes={"attempt": 2})
```

Lightweight; embedded in trace.

## Status

```
SpanStatus.OK
SpanStatus.ERROR (with description)
SpanStatus.UNSET (default)
```

## Sampling

At scale, can't keep every trace.

### Head Sampling (decide at trace start)
- Probabilistic: keep 10% of traces
- Cheap (decision made at root span)
- Limitation: may discard interesting traces (errors, slow)

```python
# OTel
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
provider = TracerProvider(sampler=TraceIdRatioBased(0.1))
```

### Tail Sampling (decide after trace completes)
- Keep all errors
- Keep slow ones (p99 latency)
- Random sample of healthy traces
- Smart; preserves interesting

Done in the OTel Collector (Tail Sampling Processor):
```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 10000
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 500 }
      - name: rate
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

### Hybrid
Head-sample 10% at app; collector tail-samples after.

### Cost
- Storage of traces: ~1-10 KB per trace
- 10K req/s × 100% sampling = lots of trace data
- Sample aggressively at high volume

## Parent Sampling

Decide based on parent's decision (consistency across services):
- If parent is sampled, child is sampled
- Otherwise, sample probabilistically

OTel default: `ParentBasedSampler(root=TraceIdRatioBased(0.1))`.

## Correlate with Logs

In every log, include `trace_id` and `span_id`:
```json
{"msg": "DB query slow", "trace_id": "abc...", "span_id": "def...", "duration_ms": 800}
```

In trace UI: click "logs for this trace" → Loki/ELK filtered by trace_id.

## Instrumentation Approaches

### Auto (OTel)
- Java: `-javaagent:otel.jar`
- Python: `opentelemetry-instrument`
- Node: `--require '@opentelemetry/auto-instrumentations-node/register'`

Instrumenters for common libraries (HTTP, gRPC, DB drivers, Kafka clients).

### Manual
```python
with tracer.start_as_current_span("calculate_total") as span:
    span.set_attribute("user_id", user_id)
    total = ...
    span.set_attribute("total_cents", total)
```

### Mix
Auto for common stuff; manual for business-specific operations.

## Common Pitfalls

- **Sampling all traces** at high volume → cost explosion
- **No trace_id in logs** → can't correlate
- **Missing context propagation** through async (queue, scheduled job) → broken trace
- **Spans too coarse** (whole request as one span) — no insight
- **Spans too fine** (every function) — noise + overhead

## Storage

Where traces live:
- Tempo (Grafana, S3-backed) — cheap
- Jaeger (Cassandra, ES, badger)
- Zipkin
- Datadog APM (commercial)
- AWS X-Ray
- Honeycomb (column-store optimized)

## Interview Themes

- "Walk me through tracing concepts"
- "W3C Trace Context — what's in traceparent?"
- "Head vs tail sampling"
- "Correlate traces and logs"
- "Async + traces — how do you propagate?"
