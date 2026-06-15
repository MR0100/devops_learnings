# L18/C06/T04 — Honeycomb (Detail)

## Learning Objectives

- Use Honeycomb deeply
- BubbleUp + Refinery

## Honeycomb

Modern observability (covered L17/C07):
- Wide events
- Tracing + metrics + logs
- High cardinality friendly

## Send Traces

OTel:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_EXPORTER_OTLP_HEADERS=x-honeycomb-team=KEY
```

## BubbleUp

Click anomaly → auto-explore which dimensions different.

E.g.:
```
errors spike at 12:00
   ↓ BubbleUp
   most are: tenant=acme, endpoint=/checkout, region=us-east-1
```

For: incident diagnosis fast.

## Heat Maps

Latency over time + dimension:
```
Y: latency (ms)
X: time
Color: count
```

Shows distribution patterns.

## Refinery

Tail sampler:
```yaml
SamplerType: dynamicsampler
SamplingFields: [status_code, service.name]
GoalSampleRate: 100
```

For: smart sampling preserving signal.

## Sampling

For 1M req/min, 99.9% normal:
- Keep all errors (~1K)
- Sample success at 1% (~10K)
- Total: 11K kept

For: cost down without losing rare events.

## Triggers

Alerts based on queries:
```
COUNT > 100 in last 5 min for status=500
```

Send to Slack, PagerDuty.

## Service Map

Auto from trace data.

## Compared to Tempo

| | Honeycomb | Tempo |
|---|---|---|
| Hosted | yes | self-host |
| Cost | per-event ingest | infra |
| Cardinality | high (native) | medium |
| Query | BubbleUp magic | TraceQL |
| Use | deep debug | bulk traces |

## When Honeycomb

- Debug-focused
- High cardinality
- Wide events natural
- Hosted preference

## Wide Events Pattern

```python
span.set_attribute("user_id", user_id)
span.set_attribute("tenant_id", tenant_id)
span.set_attribute("feature_flag", flag_value)
span.set_attribute("db_queries", count)
span.set_attribute("cache_hits", hits)
```

Rich per-event.

Honeycomb stores; query at runtime.

## Beeline (Legacy SDK)

```python
import beeline
beeline.init(writekey=KEY, dataset="api")

@beeline.traced
def handle(req):
    beeline.add_context_field("user", req.user)
```

Now: OTel preferred.

## Free Tier

20M events/month.

For: medium apps.

## Pricing

Per-event:
- Beyond free: tiered
- Less than Datadog for many

## Best Practices

- Wide events (many attributes)
- Refinery for sampling
- OTel for emission
- BubbleUp for incidents
- Triggers for alerts

## Common Mistakes

- Not enough attributes (lose value)
- 100% events (cost)
- No Refinery (no smart sample)

## Quick Refs

```bash
# OTel to Honeycomb
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_EXPORTER_OTLP_HEADERS=x-honeycomb-team=KEY
OTEL_SERVICE_NAME=my-app
```

## Interview Prep

**Junior**: "What is Honeycomb?" — A hosted observability platform built around wide events with high-cardinality querying, known for fast incident debugging via BubbleUp and trace/heatmap views.

**Mid**: "What does BubbleUp do?" — When you select an anomaly (say an error spike), BubbleUp automatically compares the dimensions of those events against the baseline and surfaces which attributes differ most (e.g. `tenant=acme`, `endpoint=/checkout`), pointing you at the likely cause without manual slicing.

**Senior**: "Explain Honeycomb's data model and why cardinality matters." — It stores wide events — single rich records with many attributes (user, tenant, feature flag, query counts) — rather than pre-aggregated metrics, so it can group and filter by any high-cardinality field at query time, which is exactly what's needed to isolate a problem to one tenant or one flag.

**Staff**: "How do wide events and Refinery shape an observability strategy?" — Instrument with OTel emitting many attributes per span so you can ask unanticipated questions later, then use Refinery as a tail sampler with dynamic policies to keep all errors and a diverse, representative sample of normal traffic; this preserves the cardinality that makes BubbleUp powerful while controlling per-event ingest cost.

## Next Topic

→ Move to [L18/C07 — Profiling](../C07/README.md)
