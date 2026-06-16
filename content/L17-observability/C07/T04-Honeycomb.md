# L17/C07/T04 — Honeycomb

## Learning Objectives

- Use Honeycomb
- Wide events approach

## Honeycomb

Modern observability:
- Wide events (high cardinality)
- BubbleUp (auto-explore)
- Charity Majors' company
- Cloud-native focus

## Philosophy

"Observability is high-cardinality, high-dimensionality." (Charity Majors.)

Honeycomb rejects the three-pillars split (separate metrics, logs, traces)
in favor of a single primitive: the **wide event**. Each request emits one
event carrying *every* dimension you might later want to slice by — user ID,
tenant, region, build SHA, feature flags, downstream latencies. Spans are
just wide events with trace context.

Why this matters:

- **Cardinality is a feature, not a cost.** Pre-aggregated metrics throw away
  the high-cardinality fields (you can't ask "which user?" of a counter).
  Wide events keep them, so you can ask questions you didn't predict.
- **Aggregate at query time, not write time.** You decide the grouping when
  you investigate, so you're never blocked by "we didn't add that dimension
  to the dashboard."
- **Unknown-unknowns.** The design target is debugging novel failures —
  "this is slow for *some* users" — rather than watching predefined
  dashboards. That's the line between *monitoring* (known questions) and
  *observability* (arbitrary questions).

## Send Events

```python
import beeline
beeline.init(writekey=KEY, dataset="api")

@beeline.traced
def handle_request(req):
    beeline.add_context_field("user.id", req.user_id)
    beeline.add_context_field("feature.flag", flag_value)
    # ... process ...
```

Or via OTel:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_EXPORTER_OTLP_HEADERS=x-honeycomb-team=KEY
```

## Datasets

= "tables":
- Per app
- Wide schema

## Queries

```
COUNT, group by user.id
WHERE error = true
LAST 1 hour
```

Filter, group, visualize.

## BubbleUp

The signature workflow, and the payoff of keeping high cardinality. You
select a region of a graph that looks wrong (a latency spike, an error
cluster). BubbleUp compares the **distribution of every dimension** inside
your selection against the baseline outside it and ranks which fields differ
most.

- Result: "the slow requests are 90% `tenant=acme`, `region=eu-west`,
  `build=4f2a` — versus ~3% in the baseline."
- It surfaces the *correlated* dimensions automatically instead of you
  guessing and adding group-bys one at a time.

This is only possible because the raw, unaggregated, high-cardinality events
are still there to compare — a pre-aggregated metrics store has nothing to
"bubble up." For interviews this is the concrete answer to "why does
high-cardinality matter in practice."

## Triggers

Alerts.

## Distributed Trace

```
Spans linked via trace_id
Service map auto
Waterfall view
```

For: cross-service debug.

## Refinery

Honeycomb's **tail-based** trace-sampling proxy. Because per-event pricing
makes 100% ingest expensive at scale, Refinery buffers the *whole trace*,
then decides whether to keep it based on its contents — the opposite of head
sampling, which decides at the first span before it knows the outcome.

```yaml
SamplerType: dynamicsampler
SamplingFields: [error, status_code]
GoalSampleRate: 100
```

Typical policy: **keep 100% of error or slow traces, aggressively sample the
boring successful ones.** A `dynamicsampler` adjusts rates per key so rare
combinations stay visible while high-volume happy-path traffic is thinned.
The trade-off is operational: Refinery must hold each trace in memory until
its spans arrive, so you size it for trace throughput and span latency, and
run it as a cluster for high volume. This is the same head-vs-tail sampling
distinction introduced in L17/C01 — Honeycomb makes tail sampling the
default path because keeping the interesting traces is core to its model.

## Pricing

Per event ingest:
- Free tier: 20M events
- Paid: scales

For: medium scale; cheaper than DD often.

## Pros

- Wide events superior debug
- BubbleUp incident workflow
- High-cardinality friendly
- OTel native

## Cons

- Different mental model
- Smaller ecosystem
- Less integrations
- Trace-only focus (less infra)

## When Honeycomb

- App-centric (services)
- Want high-cardinality
- Debug-focused
- OTel + investment in events

## When Not

- Infra-heavy (use Datadog / DD)
- Many integrations needed
- Resource limits

## Mental Model Shift

From:
- Metrics for everything
- Pre-aggregated

To:
- Events
- Aggregate at query time
- High cardinality OK

For: easier deep debug.

## Example

Slow checkout for some users:
```
COUNT, p99(duration)
group by user.tier, payment.method, region
where endpoint = "checkout"
```

Find pattern instantly.

## Compared

| | Honeycomb | Datadog | OSS Tempo |
|---|---|---|---|
| Model | wide events | three pillars | three pillars |
| Cardinality | high | medium | high (Tempo only) |
| UI | BubbleUp innovative | classic | basic |
| Cost | mid | high | infra |
| OTel | native | supported | native |

## Best Practices

- **Instrument with OpenTelemetry**, not the legacy Beeline SDK — Honeycomb
  is OTel-native and it keeps you portable. Beeline is effectively in
  maintenance mode.
- **Make events wide on purpose.** Add the dimensions you might ever want to
  slice by (tenant, region, build SHA, flags, downstream timings) at the
  point you have them; a missing field is a question you can't ask later.
- **Use tail sampling via Refinery** with a keep-the-interesting policy:
  100% of errors and slow traces, sample the happy path. Size Refinery for
  trace throughput and run it clustered at volume.
- **Drive incidents with BubbleUp**, not pre-built dashboards — select the
  bad region and let it rank the differing dimensions.
- **Pair Honeycomb with infra metrics elsewhere** (Prometheus/CloudWatch);
  it's app/trace-centric, not a host-metrics tool.

## Common Mistakes

- **Logging unstructured strings as event fields** instead of typed,
  queryable dimensions — kills the whole grouping/BubbleUp workflow.
- **Stuffing PII into event fields** (raw emails, tokens) — high cardinality
  is fine, but secrets and personal data don't belong in telemetry.
- **Head sampling that drops the error traces** you most needed — use
  tail-based Refinery so the decision sees the outcome.
- **Expecting it to replace infrastructure monitoring** — it won't dashboard
  your hosts and disks like Datadog does.
- **Pre-aggregating before send** ("we'll just emit a counter") — that
  discards the cardinality that makes Honeycomb worth using.

## Quick Refs

```bash
# OTel to Honeycomb
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_EXPORTER_OTLP_HEADERS=x-honeycomb-team=KEY

# Beeline (older SDK)
import beeline
beeline.init(...)
```

## Interview Prep

**Junior**: "What is a 'wide event' and how is it different from a metric?" —
A wide event is a single structured record emitted per request that carries
many dimensions — user ID, tenant, region, status, latency, feature flags. A
metric is a pre-aggregated number that has already thrown those dimensions
away, so you can count requests but can't ask "which user?" of it. Honeycomb
stores the wide events raw so the dimensions are still there to query.

**Mid**: "Why does Honeycomb care so much about high cardinality when
Prometheus tells you to avoid it?" — They're solving different problems.
Prometheus is a metrics store indexed by label set, so high-cardinality
labels (user IDs, request IDs) explode its index and memory — that's a real
operational limit. Honeycomb stores wide events in a columnar store built for
exactly those high-cardinality fields, and its core workflow (BubbleUp)
*needs* them: to find that a spike is concentrated in one tenant or build, it
has to still have the per-event tenant and build fields. So cardinality is a
cost in Prometheus and a feature in Honeycomb.

**Senior**: "Walk me through diagnosing 'checkout is slow for some users'
in Honeycomb." — I'd graph p95 (or heatmap) `duration` for the checkout
endpoint, see the elevated band, and select it. Then BubbleUp compares every
dimension inside the slow selection against the fast baseline and ranks the
differences — say the slow requests are overwhelmingly `tenant=acme`,
`region=eu-west`, `payment.method=ach`, `build=4f2a`. That immediately points
at a cohort or a bad deploy without me guessing group-bys one at a time, and
I can pivot into a trace waterfall for an example slow request to see which
span dominates.

**Staff**: "A team wants to standardize on Honeycomb. What's your
recommendation and what are the boundaries?" — Adopt it for app and
trace-level observability and instrument with OpenTelemetry so we stay
vendor-neutral. The big wins are arbitrary, high-cardinality investigation
and the BubbleUp incident workflow, which suit a mature observability culture
debugging unknown-unknowns. The boundaries: Honeycomb is event/trace-centric,
not an infrastructure-metrics platform, so I'd keep Prometheus/CloudWatch for
host and resource monitoring. I'd control cost with tail sampling via
Refinery — keep all error/slow traces, sample the happy path — and enforce a
hygiene policy that fields are typed and PII-free, since "make events wide"
must not become "log secrets."

## Next Topic

→ [T05 — Splunk Observability](T05-Splunk.md)
