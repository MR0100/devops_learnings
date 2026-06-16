# L18/C05/T01 — Spans, Traces, Context Propagation

## Learning Objectives

- Understand traces
- Propagate context

## Trace

End-to-end request:
```
trace_id: abc123
├─ span A (frontend)
├─ span B (auth service)
├─ span C (backend)
│  └─ span D (DB query)
└─ span E (cache)
```

## Span

Unit of work:
- name
- trace_id
- span_id
- parent_span_id
- start_time
- end_time
- attributes (kv)
- events
- links
- status

## Sample Span

```json
{
  "trace_id": "abc",
  "span_id": "def",
  "parent_span_id": "abc1",
  "name": "GET /users/{id}",
  "kind": "SERVER",
  "start_time": 1700000000000,
  "end_time": 1700000000050,
  "attributes": {
    "http.method": "GET",
    "http.status_code": 200,
    "user.id": "alice"
  },
  "status": "OK"
}
```

## Parent-Child

```
Root span (no parent)
├─ Child span (parent = root)
│  └─ Grandchild
```

Tree structure.

## Span Kind

- SERVER (incoming HTTP/RPC)
- CLIENT (outgoing)
- PRODUCER (queue)
- CONSUMER (queue)
- INTERNAL (no I/O)

## Context Propagation

Across services via headers:
```
traceparent: 00-{trace_id}-{span_id}-{flags}
tracestate: vendor=...
```

W3C standard.

## Manual Propagation

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract

# Outgoing
headers = {}
inject(headers)
requests.get(url, headers=headers)

# Incoming
ctx = extract(request.headers)
span = tracer.start_span("operation", context=ctx)
```

Or: HTTP framework middleware does it.

## Auto Propagation

OTel SDK + framework:
- Span auto-extends across services
- No code changes

For: most common.

## Service Map

From traces:
- Service A → Service B (latency)
- Service B → Service C
- Auto-rendered.

For: topology.

## Distributed Trace Use

- Find slow service
- Bottleneck
- Cross-service correlation
- Error propagation

## Latency Breakdown

Trace view shows:
- Frontend: 5ms
- Auth: 10ms
- Backend: 80ms
- DB: 60ms

Most time: DB. Optimize.

## Trace ID

128-bit; random or generated.

Used to correlate logs:
```json
{"msg": "Error", "trace_id": "abc"}
```

## Trace Context

In addition to trace_id + span_id:
- Sampled flag
- Baggage (per-request data)

## Baggage

```python
from opentelemetry import baggage
baggage.set_baggage("user_id", "alice")
```

Propagates across spans + services.

For: tenant, user context.

## Sampling Decision

(See T03.)

## Propagators

- W3C TraceContext (default)
- W3C Baggage
- B3 (Zipkin legacy)
- Jaeger
- AWS X-Ray

```python
OTEL_PROPAGATORS=tracecontext,baggage,b3multi
```

## Multi-Propagator

For: legacy services using B3 + new using W3C.

## Trace Sampling

```
parentbased(traceidratio(0.01))
```

If parent sampled: sample.
If parent not: ignore (consistent).

## Async Propagation

Background tasks:
```python
ctx = trace.set_span_in_context(span)
threading.Thread(target=run, args=(ctx,)).start()

def run(ctx):
    with tracer.start_as_current_span("background", context=ctx):
        ...
```

For: async context propagation.

## Logs in Trace Context

```python
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor
LoggingInstrumentor().instrument()

logger.info("hello")
# Auto: emits with trace_id, span_id
```

## Trace Sampling Decision

Per request:
1. Frontend gets request
2. Decides sample (yes/no based on rate)
3. Marks `sampled` flag in context
4. Propagates to all
5. All services emit (if sampled)

Consistent for entire trace.

## Sampling Strategies

- Always (debug only)
- 1% random
- Head-based
- Tail-based (Collector)

## Performance

Span creation: ~1 µs.
Span export: batched (negligible).

Auto-instrumentation: 1-5% overhead.

## Common Mistakes

- Forget context propagation (broken traces)
- High cardinality attributes (cost)
- Span name with IDs (cardinality)
- Wrong span kind

## Span Name

Low cardinality:
```
"GET /users/{id}"   # YES
"GET /users/123"    # NO
```

## Error Handling

```python
try:
    ...
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR))
```

## Events

```python
span.add_event("cache_miss", {"key": "..."})
```

Timeline within span.

## Best Practices

- Auto-instrument
- W3C TraceContext
- Sample tail (Collector)
- Propagate baggage carefully
- Logs link to traces
- Span name templated

## Quick Refs

```python
tracer.start_as_current_span("name") as span:
    span.set_attribute("k", "v")
    span.add_event("e")

# Propagation
inject(headers)
extract(headers)

# Baggage
baggage.set_baggage("k", "v")
```

## Interview Prep

**Junior**: "What's a span and a trace?" — A span is a single timed unit of work (with a name, start/end, attributes, and status); a trace is the tree of spans for one request, linked by a shared `trace_id` and `parent_span_id` relationships.

**Mid**: "How does context propagation work across services?" — The current span's `trace_id`, `span_id`, and sampled flag are injected into outgoing headers (W3C `traceparent`) and extracted on the receiving side to continue the same trace; OTel auto-instrumentation does this for HTTP/gRPC, but queues and async tasks need manual inject/extract.

**Senior**: "Why might a distributed trace appear broken?" — Usually a missing propagation hop — a service that doesn't forward context (often across Kafka/SQS or a background thread) starts a new root trace, so the chain splits; other causes are mismatched propagators (B3 vs W3C) or high-cardinality span names breaking grouping.

**Staff**: "How do you roll out tracing strategy across an org?" — Standardize on OpenTelemetry with W3C TraceContext, lean on auto-instrumentation to get coverage cheaply, enforce low-cardinality templated span names and bounded attributes, propagate context through every hop including queues and async work, and tail-sample to keep cost down while retaining errors and slow traces.

## Next Topic

→ [T02 — W3C Trace Context](T02-W3C-Trace-Context.md)
