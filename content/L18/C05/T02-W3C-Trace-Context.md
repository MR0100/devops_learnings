# L18/C05/T02 — W3C Trace Context

## Learning Objectives

- Use W3C standard
- Migrate from legacy

## W3C Trace Context

Standard headers:
```
traceparent: 00-{trace_id}-{span_id}-{flags}
tracestate: vendor1=value,vendor2=value
```

## traceparent

```
00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
│   │                                 │              │
│   trace_id (16 bytes)              span_id (8 b)  flags
version
```

Version: 00 (current).
Flags: 01 = sampled.

## tracestate

```
tracestate: vendor=value,otherVendor=otherValue
```

Vendor-specific data. Limited size.

For: chained vendors propagating extra.

## Example HTTP

```
GET /api HTTP/1.1
traceparent: 00-abc...-def...-01
tracestate: dd=trace_id=12345
```

Backend service reads, continues with parent.

## Why W3C

Before:
- Each vendor had own headers
- B3 (Zipkin)
- X-B3-TraceId etc.
- Jaeger had own

Interop pain.

W3C: one standard.

## Sampling Flag

```
flags = 01   # sampled = 1
flags = 00   # not sampled
```

Receiver sees:
- Sampled: emit span
- Not: skip

For: consistent decision propagation.

## Baggage

```
baggage: user.id=alice,tenant.id=acme
```

Separate header. Not auto-trace.

For: per-request data accompanying request.

## Implementation

OTel: W3C default.

```bash
OTEL_PROPAGATORS=tracecontext,baggage
```

## Migration

From B3:
- Add W3C
- Both supported (multi-propagator)
- Phase out B3

```bash
OTEL_PROPAGATORS=tracecontext,baggage,b3multi
```

## Limits

- traceparent: ~50 chars
- tracestate: limit 512 chars (recommended; max varies)
- baggage: limit recommended

## Vendor Behavior

vendors include their data in tracestate:
- Datadog: dd=...
- New Relic: nr=...
- Honeycomb: hc=...

Others pass through.

## Headers in gRPC

W3C extends to gRPC metadata.

## Lambda Functions

```
traceparent: ... (extracted from invoke headers)
```

For: Lambda → downstream propagation.

## Async / Queue

Encode trace context in messages:
```json
{
  "data": {...},
  "tracecontext": {
    "traceparent": "00-...",
    "tracestate": "..."
  }
}
```

Consumer extracts; continues trace.

For: cross-service via queue.

## Browsers

W3C Trace Context for HTML:
```html
<meta name="traceparent" content="...">
```

Browser → backend correlated trace.

For: RUM + APM.

## Limitations

- Privacy: sampled flag visible
- Security: trace_id observable
- Size: tracestate quota

## Best Practices

- W3C default
- Multi-propagator during migration
- Baggage minimal (size cost)
- Sample at source
- Propagate to all hops

## Common Mistakes

- Skip propagation (broken trace)
- Wrong propagator config
- baggage abuse (size)
- Different versions of W3C across services

## OTel Default

```bash
OTEL_PROPAGATORS=tracecontext,baggage
```

For: future-proof.

## OpenTelemetry Standard

W3C as default for OTel.

## Verify

```bash
curl -v https://my-app/api/test
# Check response: traceparent reflected back or in logs
```

## Quick Refs

```
traceparent: 00-{32}-{16}-{2}
tracestate:  vendor=value

W3C TraceContext = standard
b3 / jaeger = legacy
```

```bash
OTEL_PROPAGATORS=tracecontext,baggage,b3multi
```

## Interview Prep

**Junior**: "What is W3C Trace Context?" — A standard for propagating trace identity across services via two HTTP headers: `traceparent` (version, trace_id, span_id, flags) and `tracestate` (vendor-specific data), replacing the old per-vendor header zoo.

**Mid**: "What's in the `traceparent` header?" — Four hyphen-separated fields: version (`00`), a 16-byte trace_id, an 8-byte parent span_id, and trace flags where `01` means sampled; a receiver reads it to continue the same trace and respect the sampling decision.

**Senior**: "How do you migrate from B3 to W3C without breaking traces?" — Configure a multi-propagator (`OTEL_PROPAGATORS=tracecontext,baggage,b3multi`) so services emit and accept both formats during the transition, verify traces stay connected across mixed services, then drop B3 once everything speaks W3C.

**Staff**: "How do you ensure tracing interop across vendors and boundaries?" — Standardize on W3C TraceContext everywhere, let vendors carry their extras in `tracestate` (which others pass through unchanged), keep baggage minimal since it rides every request and counts against size limits, and explicitly propagate context across queues, browsers (RUM), and Lambda invokes where it isn't automatic.

## Next Topic

→ [T03 — Sampling (Head vs Tail)](T03-Sampling-Head-Tail.md)
