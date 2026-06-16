# L30/C03/T04 — Tempo + Trace Correlation

## Learning Objectives

- Stand up Tempo as the trace backend behind the OTel pipeline
- Wire the three-pillar correlation the stack promises: metric → trace → log
- Understand exemplars, span metrics, and `traceID` derived fields as the glue
- Reason about trace storage cost and why tail sampling lives in the gateway, not Tempo

## Why This Topic Exists

The whole point of building Prometheus, Loki, and Tempo *together* is not three
separate UIs — it's **correlation**. When a Grafana panel shows a p99 latency
spike, an on-call engineer should be one click from the exact slow trace, and
one more click from that request's logs. That click-path is what separates a
"production-grade observability stack" from three tools in a trenchcoat.

Tempo is the piece that makes traces cheap enough to keep. It's a
**trace-id-only** store: it indexes nothing but the trace ID and writes spans
straight to object storage. That's why it scales to millions of traces for the
price of an S3 bucket — and it's also why you can't query Tempo by arbitrary
attributes without TraceQL/metrics-generator. The trade-off is deliberate:
Tempo bets that you arrive at a trace *from somewhere else* (an exemplar, a log
line, a span-metric), not by browsing traces blind.

## Architecture

```
Apps (OTel SDK, W3C traceparent propagation)
   ↓ OTLP
[OTel Gateway]
   - tail_sampling (keep errors + slow + 10% baseline)
   - exporter: otlp → Tempo
        ↓
[Tempo]
   ├─ distributor → ingester → S3 (trace blocks, trace-id index only)
   └─ metrics-generator → Prometheus remote_write (span metrics + service graph)

[Grafana]
   Prometheus  ──exemplar(trace_id)──┐
   Loki        ──derived field──────┤──→ Tempo (open the trace)
   Tempo       ──"Logs for this span"──→ Loki
```

The three correlation edges, named:

1. **Metric → trace** — a Prometheus histogram carries an **exemplar** tagged
   with `trace_id`. Grafana renders it as a diamond on the latency panel; click
   it, jump to the trace in Tempo.
2. **Log → trace** — a structured log line includes `trace_id`. A Grafana Loki
   **derived field** turns that value into a link to Tempo.
3. **Trace → log** — from a span in Tempo, Grafana's "Logs for this span"
   button queries Loki for `{...} | trace_id="<id>"`.

## Tempo Setup

```bash
helm install tempo grafana/tempo-distributed -f tempo-values.yaml
```

```yaml
# tempo-values.yaml (key bits)
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: s3.amazonaws.com
      region: us-east-1

# Generate span metrics + service-graph metrics from incoming spans,
# then remote_write them into Prometheus/Mimir so RED metrics exist
# even for un-instrumented services.
metricsGenerator:
  enabled: true
  remoteWriteUrl: http://prometheus:9090/api/v1/write

overrides:
  defaults:
    metrics_generator:
      processors: [service-graphs, span-metrics]
```

`metrics-generator` is the quiet workhorse: it derives `traces_spanmetrics_*`
(rate/error/duration per service) and a service-graph from the span stream. You
get RED dashboards and a dependency map without instrumenting a single metric
by hand.

## Exemplars: Metric → Trace

Exemplars are sampled, trace-tagged sample points attached to a histogram
bucket. Three things must all be true or the click-path silently breaks:

1. **App emits them.** The histogram observation must attach the active
   `trace_id`:

   ```go
   duration := time.Since(start).Seconds()
   histogram.(prometheus.ExemplarObserver).
       ObserveWithExemplar(duration, prometheus.Labels{"trace_id": traceID})
   ```

2. **Prometheus stores them.** Exemplar storage is opt-in:

   ```yaml
   # Prometheus must be started with the feature enabled
   --enable-feature=exemplar-storage
   ```

   (Remote-write to Mimir/Thanos must also carry exemplars; check the
   `send_exemplars: true` remote-write setting.)

3. **Grafana links them.** On the Prometheus datasource, add an exemplar config
   that maps the `trace_id` label to the Tempo datasource:

   ```yaml
   # Grafana Prometheus datasource
   exemplarTraceIdDestinations:
     - name: trace_id
       datasourceUid: tempo
   ```

Miss any one and the panel shows latency but no diamonds — the most common
"correlation doesn't work" support ticket.

## Logs ↔ Traces

**Log → trace** (Loki derived field on the Loki datasource):

```yaml
derivedFields:
  - name: TraceID
    matcherRegex: '"trace_id":"(\w+)"'
    url: '$${__value.raw}'
    datasourceUid: tempo
```

**Trace → log** (Tempo datasource `tracesToLogsV2`):

```yaml
tracesToLogsV2:
  datasourceUid: loki
  tags: [{ key: 'service.name', value: 'service' }]
  filterByTraceID: true   # query Loki for trace_id of the span
```

For this to work end to end, the app's logging must inject `trace_id` into
every log line (OTel logging instrumentation, or a structured-logging hook that
reads the active span context).

## Tail Sampling Lives in the Gateway, Not Tempo

A frequent design mistake is sending 100% of spans to Tempo and "sampling
later." Sampling has to happen **before** storage, in the OTel gateway, because
the decision needs the *whole* trace (all spans) to keep error/slow traces
intact:

```yaml
# OTel gateway
tail_sampling:
  policies:
    - { type: status_code, status_code: { status_codes: [ERROR] } }   # always keep errors
    - { type: latency, latency: { threshold_ms: 500 } }                # always keep slow
    - { type: probabilistic, probabilistic: { sampling_percentage: 10 } } # 10% of the rest
```

This keeps the signal (errors, tail latency) at full fidelity while cutting
storage ~10× on the boring happy path. Tempo itself does not sample — it stores
what it's given.

## Cost & Sizing (demo scale)

- ~100K traces/day after tail sampling
- ~100 MB/day to S3 (trace blocks compress well; trace-id index is tiny)
- metrics-generator adds a modest series count to Prometheus (per-service, not
  per-request — bounded cardinality)
- Full traces tier: **~$5–10/month** at this volume; lifecycle-expire S3 blocks
  (e.g. 14–30d) so it stays flat

## Demo / Acceptance Criteria

You can claim this works when, in one screen-recording, you:

1. Generate load with k6 against the sample app.
2. Open a latency panel, see exemplar diamonds, click one → land on that trace
   in Tempo.
3. From a slow span, click "Logs for this span" → see that request's Loki logs.
4. From a Loki error line, click the derived `TraceID` field → land back on the
   trace.
5. Show a service-graph panel rendered from metrics-generator (no manual
   instrumentation).

If any hop requires copy-pasting a trace ID by hand, the correlation isn't
wired — fix the datasource config, not the apps.

## Best Practices

- One pipeline, three backends: OTLP everywhere; let the gateway fan out
- Sample in the gateway (tail), store everything you sample in Tempo
- Enable `exemplar-storage` in Prometheus and `send_exemplars` on remote-write
- Inject `trace_id` into logs at the SDK level so derived fields just work
- Turn on metrics-generator for free RED metrics + service graph
- Lifecycle-expire trace blocks in S3; traces are the cheapest pillar to lose

## Common Mistakes

- Storing 100% of traces (cost) instead of tail-sampling in the gateway
- Exemplars emitted by the app but `--enable-feature=exemplar-storage` not set
- `trace_id` missing from logs → log↔trace correlation silently dead
- Querying Tempo by attribute and expecting it to be fast without TraceQL search/metrics-generator
- Running multiple Tempo metrics-generators without dedup, double-counting span metrics

## Quick Refs

```
Tempo = trace-id-only store on S3; arrive via exemplar/log/span-metric
Metric→trace: histogram exemplar(trace_id) + Prometheus exemplar-storage + Grafana exemplarTraceIdDestinations
Log→trace:    Loki derivedFields (regex trace_id → Tempo)
Trace→log:    Tempo tracesToLogsV2 (filterByTraceID)
Free RED + service graph: Tempo metrics-generator → Prometheus remote_write
Sample in the gateway (tail), not in Tempo
```

## Interview Prep

**Junior**: "What is distributed tracing and what's a trace ID?" — A trace
follows a single request across services; each hop is a span, and they're all
tied together by one trace ID that propagates in the request headers (W3C
`traceparent`). It lets you see where time went across a request, not just
within one service.

**Mid**: "How does Tempo keep traces cheap, and what's the catch?" — Tempo
indexes only the trace ID and writes spans straight to object storage, so it
scales to millions of traces for the cost of an S3 bucket. The catch is you
can't browse or query by arbitrary attributes cheaply — you're expected to
*arrive* at a trace from an exemplar, a log line, or a span metric, so the rest
of the stack (exemplars, derived fields) has to be wired up for it to be
useful.

**Senior**: "Walk me through metric-to-trace correlation end to end." — The app
attaches an exemplar tagged with the active `trace_id` to its latency
histogram. Prometheus must run with exemplar storage enabled (and remote-write
must carry exemplars to Thanos/Mimir). In Grafana, the Prometheus datasource
maps the `trace_id` exemplar label to the Tempo datasource via
`exemplarTraceIdDestinations`. Then a latency panel shows exemplar diamonds and
one click opens the exact slow trace. The classic failure is the app emitting
exemplars while Prometheus isn't storing them — latency shows, diamonds don't.

**Staff**: "Where do you put sampling in this pipeline and why does it matter
for correlation?" — Tail sampling belongs in the OTel gateway, before Tempo,
because the keep/drop decision needs the complete trace — you want to *always*
keep error and high-latency traces and only probabilistically drop the happy
path. Head sampling at the SDK can't do that without dropping the spans you most
want. Putting it in the gateway preserves the exact traces an exemplar or a log
line will point at, so correlation stays trustworthy while storage drops ~10×.
If you sampled randomly, half your exemplar clicks would 404 in Tempo — which
quietly destroys trust in the whole stack.

## Next Topic

→ Move to [L30/C04 — Project 4: Internal Developer Platform](../C04/README.md)
