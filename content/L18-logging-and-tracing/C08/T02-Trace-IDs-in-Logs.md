# L18/C08/T02 — Trace IDs in Logs

## Learning Objectives

- Add trace_id to logs
- Correlate

## Why

Logs alone:
- Find error
- No context
- Hard to find related events

With trace_id:
- Click log → trace → other logs in trace

For: fast investigation.

## How

App: include trace_id automatically:
```json
{"ts": "...", "level": "info", "msg": "DB query", "trace_id": "abc", "span_id": "def"}
```

OTel: auto-instrument logging.

## Python

```python
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=True)

logger.info("hello")
# Auto-includes trace_id, span_id
```

## Java

```xml
<configuration>
  <appender name="JSON" class="...JsonEncoder">
    <pattern>{
      "trace_id": "%X{trace_id}",
      "span_id": "%X{span_id}",
      "msg": "%message"
    }</pattern>
  </appender>
</configuration>
```

MDC populated by OTel agent.

## Go

```go
import "go.opentelemetry.io/otel/trace"

span := trace.SpanFromContext(ctx)
spanCtx := span.SpanContext()

logger.Info("hello",
    "trace_id", spanCtx.TraceID().String(),
    "span_id", spanCtx.SpanID().String())
```

## Node.js

```js
const { trace } = require('@opentelemetry/api');

const span = trace.getActiveSpan();
const ctx = span ? span.spanContext() : null;

logger.info({
  msg: 'hello',
  trace_id: ctx?.traceId,
  span_id: ctx?.spanId
});
```

## Grafana Jump

Loki + Tempo:
```yaml
# Loki datasource config
derivedFields:
  - matcherRegex: '"trace_id":"(\w+)"'
    url: '$${__value.raw}'
    datasourceUid: tempo
    name: traceID
```

Loki UI: click trace_id → Tempo trace view.

## ELK Equivalent

```
{trace_id: "abc"}
```

Use index pattern + URL:
```
Link to Jaeger: http://jaeger/trace/{trace_id}
```

## OTel Standard

```
attributes:
  trace_id: ...
  span_id: ...
```

For: stand alone or as log attribute.

## In Span

```python
span.add_event("log message", {"level": "info", "data": ...})
```

Log inline with span. Less common.

## Datadog

Auto-inject trace_id:
```
dd.trace_id, dd.span_id
```

UI auto-links.

## Common Mistakes

- Forget to forward (broken)
- Multiple ID formats (confused)
- High-cardinality: trace_id in metric labels (bad)
- No frontend → backend correlation (RUM gap)

## Browser → Backend

RUM (Datadog, Sentry):
- Capture trace_id in browser
- Pass to backend
- Full trace

## Async Context

```python
import asyncio

async def task():
    # OTel async context propagation
    with tracer.start_as_current_span("async"):
        logger.info("inside")  # auto trace_id
```

## Multi-Process

Pass context:
- Env vars
- Headers
- Queue metadata

For: cross-process correlation.

## Best Practices

- Auto-instrument logging
- Same field name everywhere
- Link in UI (Loki → Tempo)
- Document field format
- Test in non-prod

## Common Mistakes

- Different field names per service
- Missing for async tasks
- No UI link config
- Skip context propagation

## Cost

trace_id in logs: small bytes.
For 1 TB logs: ~50 GB just trace_id (negligible).

## Quick Refs

```python
# Python
LoggingInstrumentor().instrument(set_logging_format=True)
```

```yaml
# Grafana
derivedFields:
  - matcherRegex: '"trace_id":"(\w+)"'
    datasourceUid: tempo
    name: traceID
```

```json
{"trace_id": "...", "span_id": "...", "msg": "..."}
```

## Interview Prep

**Junior**: "Why put trace IDs in logs?" — So a single log line links to its full distributed trace and to every other log sharing that `trace_id`, turning an isolated error message into the complete request story.

**Mid**: "How do you get trace_id into logs automatically?" — Use OTel logging instrumentation/MDC so the active span's `trace_id` and `span_id` are injected into every line (e.g. `LoggingInstrumentor().instrument(set_logging_format=True)` in Python, MDC in Java), rather than passing IDs by hand.

**Senior**: "Describe the log↔trace correlation workflow." — Configure Grafana's Loki datasource with a derived field that regex-extracts `trace_id` and links to Tempo, so in the log UI you click the ID and land on the trace; the same idea works for ELK→Jaeger via a URL template.

**Staff**: "What makes log↔trace correlation reliable across an org?" — One consistent field name everywhere (not `traceId` vs `trace_id`), context propagation through async tasks and queues so the ID survives every hop, the UI link wired up so the jump actually works, keeping `trace_id` out of metric labels (cardinality), and periodically testing the chain since it silently rots.

## Next Topic

→ Move to [L19 — Site Reliability Engineering](../../L19-sre/README.md)
