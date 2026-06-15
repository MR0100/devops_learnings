# L18/C08/T03 — Unified Query Experiences

## Learning Objectives

- Understand what "single pane of glass" actually means for an investigation
- Wire up click-through correlation between metrics, traces, logs, and profiles
- Compare self-hosted (Grafana stack) vs commercial APM correlation UX

## The Correlation Problem

Each observability pillar is powerful alone. Real investigation is **jumping between them**:

> See a metric anomaly → open an example trace → read the logs for that trace → view the profile for that pod and time.

If the pillars don't link, each jump means a manual copy-paste of a timestamp or trace ID into another tool — and investigation takes 10× longer. A unified query experience makes those jumps a single click.

## What "Single Pane of Glass" Actually Means

A concrete incident walkthrough:

```
1. Alert fires            (Prometheus + Alertmanager)
   "p99 latency on /checkout > 1s"
2. Dashboard shows metric + exemplars
   Click an exemplar dot (a specific slow request)
3. Tempo opens the trace
   See: span "fetch-order" → DB call took 800ms
4. Click "logs for this trace"
   Loki shows the slow-query log with the SQL text
5. Click "profile for this pod / time"
   Pyroscope shows the hot code path during the incident
```

Alert → root cause in ~5 minutes. Without correlation, the same investigation is closer to 50 minutes of context-switching.

## Unified Query in Grafana

Grafana's **Explore** mode is the open-source path. One UI, a datasource picker (Prometheus, Loki, Tempo, Pyroscope), and configured links that carry `trace_id` between them.

| From | To | Mechanism |
|---|---|---|
| Prometheus | Tempo | Click an **exemplar** dot → opens the trace |
| Loki | Tempo | LogQL result has a `trace_id` field → click opens the trace |
| Tempo | Loki | Trace view "logs for this trace" → Loki query filtered by `trace_id` |
| Tempo | Pyroscope | Span "view profile" → Pyroscope at that pod/time |

These links are configured in the datasource settings as **derived fields** (Loki) and **trace-to-logs / trace-to-metrics** (Tempo). The plumbing only works if every signal carries a consistent `trace_id`.

## Commercial APMs (Datadog / New Relic / Honeycomb)

Commercial APMs make correlation *invisible* — all signals live in one platform, pre-joined:

- Click an error-rate spike → drill straight to the failing traces
- Click a slow trace → see its logs already filtered
- See the related profile / flame graph inline

This is the major UX advantage over self-hosted stacks. The trade-off is cost and data gravity (vendor lock-in). Grafana's stack is catching up but requires you to wire the links yourself.

## Making the Plumbing Work

Correlation is only as good as the IDs flowing through the system.

### Trace ID Everywhere

- Structured logs (always)
- Customer-facing error pages (so the user can quote it in a support ticket)
- HTTP response headers (`X-Request-Id` or `traceparent`)
- Slow-query logs (database)
- Messages on internal queues (carry `trace_id` in headers)

### Cross-Service Propagation

Verify trace context propagates through every hop:

- HTTP / gRPC calls — automatic via OpenTelemetry instrumentation
- Kafka / SQS — **manually inject** trace context into message headers
- Async batch jobs — carry the trace context explicitly

### Test It

Most teams have broken correlation they don't know about. Trigger a deliberately slow request and verify, end to end:

- The trace appears in Tempo
- The logs contain the `trace_id`
- Logs are queryable by that `trace_id`
- A metric exemplar exists for the request
- Every click-through actually opens the right view

## Cost vs Value

Full correlation emits many fields per event. Cost-conscious teams keep the cheap, high-value links at 100% and sample the expensive parts:

- Trace IDs in 100% of logs (cheap)
- Exemplars on 100% of metrics (cheap)
- **Tail-sample** traces — keep only the interesting ones (errors, slow)
- Continuous profiling at a low rate

## Common Mistakes

- Treating the three pillars as separate dashboards with no links
- Emitting traces but not putting `trace_id` in logs (no log↔trace jump)
- Forgetting to propagate trace context across Kafka/SQS (trace breaks at the queue)
- Never testing click-through, so correlation silently rots
- Head-sampling traces so the slow request you need was already dropped

## Best Practices

- Standardize on OpenTelemetry context propagation across all services
- Put `trace_id` and `span_id` in every structured log line
- Emit exemplars on latency histograms so metric→trace is one click
- Tail-sample traces to keep cost down without losing the interesting ones
- Periodically run a synthetic slow request and verify the full correlation chain

## Quick Refs

```
# Prometheus exemplar (trace_id annotation on a histogram bucket)
http_request_duration_seconds_bucket{le="0.5"} 1234 # {trace_id="abc"} 0.45 @1717920000

# Grafana correlation config
Loki  → derived field: trace_id → Tempo
Tempo → trace-to-logs: Loki, filtered by trace_id
Tempo → trace-to-metrics / view profile: Pyroscope
```

## Interview Prep

**Junior**: "What are the three pillars of observability?" — Metrics, logs, traces (plus profiling as a fourth).

**Mid**: "How do you correlate logs, metrics, and traces?" — Carry a consistent `trace_id` through all of them; exemplars link metric→trace, `trace_id` in logs links log↔trace.

**Senior**: "Walk me through investigating an incident across all signals." — Alert → exemplar → trace → logs-for-trace → profile, each a single click; explain the derived-field/trace-to-logs config that makes it work.

**Staff**: "Self-hosted Grafana stack vs commercial APM for correlation — trade-offs?" — APMs give zero-config single-pane UX at high cost and data gravity; Grafana is cheaper and avoids lock-in but you own the wiring (exemplars, derived fields, context propagation) and the testing discipline; decision hinges on team size, ops maturity, and TCO.

## Next Topic

→ Move to [L19 — Site Reliability Engineering](../../L19/README.md)
