# L18 — Logging & Distributed Tracing

## Overview

L17 covered metrics deeply. This lecture goes into logs and traces — the other two pillars — plus profiles as the emerging fourth.

**8 chapters, 26 topics.**

## Chapter Map

### [C01](C01/) — Logging Fundamentals
- T01 Structured vs Unstructured Logs
- T02 Log Levels (and Why You're Wrong About Them)
- T03 Sampling Strategies

### [C02](C02/) — ELK Stack
- T01 Elasticsearch Architecture
- T02 Logstash & Beats
- T03 Kibana
- T04 Index Lifecycle Management

### [C03](C03/) — Loki
- T01 Architecture (Distributor, Ingester, Querier)
- T02 LogQL
- T03 Cost Tradeoffs vs ELK

### [C04](C04/) — Collectors & Shippers
- T01 Fluentd
- T02 Fluent Bit (Lightweight)
- T03 Vector (Rust-Based)
- T04 OpenTelemetry Collector for Logs

### [C05](C05/) — Tracing Fundamentals
- T01 Spans, Traces, Context Propagation
- T02 W3C Trace Context
- T03 Sampling (Head vs Tail)

### [C06](C06/) — Tracing Tools
- T01 Jaeger
- T02 Zipkin
- T03 Tempo
- T04 Honeycomb

### [C07](C07/) — Profiling
- T01 Pyroscope / Grafana Profiles
- T02 Continuous Profiling Patterns

### [C08](C08/) — Correlating Logs, Metrics, Traces
- T01 Exemplars
- T02 Trace IDs in Logs
- T03 Unified Query Experiences

## Structured Logging

Always emit JSON or other key=value:

```json
{
  "ts": "2026-06-09T12:34:56Z",
  "level": "info",
  "service": "payments",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "u-789",
  "msg": "payment processed",
  "amount_cents": 1234,
  "currency": "USD"
}
```

Then any aggregator (Loki, Splunk, ES) can index/filter cleanly.

## Tracing Basics

```
Trace
└── Span: GET /checkout
    ├── Span: validate user (1ms)
    ├── Span: fetch cart (3ms)
    ├── Span: charge payment
    │   └── Span: stripe API call (180ms)
    └── Span: send confirmation
        └── Span: SES SendEmail (40ms)
```

Each span has: traceId, spanId, parentId, name, start, end, attributes, events.

W3C Trace Context propagates IDs via headers (`traceparent`, `tracestate`).

## Sampling

- **Head sampling**: decide at trace start (cheap, lose interesting traces)
- **Tail sampling**: decide after trace finishes (expensive, smart — keep errors/slow)
- Typical mix: head-sample at 10% + always sample errors and outliers via tail

## Loki vs ELK

| | Loki | ELK |
|---|---|---|
| Indexed | Only labels | All fields |
| Cost | Object storage cheap | Search infra expensive |
| Query | LogQL | KQL |
| Scale | High volume, label-driven | Lower volume, deep search |

## OpenTelemetry

The unification standard. SDK (instrumentation) + Collector (process/route) + protocol (OTLP).

```
[App with OTel SDK] ──OTLP──► [OTel Collector]
                                   │
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
              Prometheus       Tempo            Loki/ES
              (metrics)        (traces)         (logs)
```

## Recommended Reading

- *Distributed Tracing in Practice* — Parker et al.
- *Observability Engineering* — Majors, Fong-Jones, Miranda
- OpenTelemetry docs

## Interview Themes

- "Difference between logs, metrics, traces"
- "When would you use Loki vs Elasticsearch?"
- "Head vs tail sampling tradeoff"
- "Correlate logs, metrics, traces — how?"

## Next

→ [L19 — Site Reliability Engineering](../L19-sre/README.md)
