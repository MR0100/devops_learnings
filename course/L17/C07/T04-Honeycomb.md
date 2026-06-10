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

"Observability is high-cardinality, high-dimensionality."

Wide events vs three pillars:
- Per-request rich data
- Query at runtime
- Don't aggregate prematurely

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

Click anomaly → auto-explore:
- Which dimension different?
- Outlier cohort?

For: incident diagnosis.

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

Sampling proxy:
- Tail-based
- Per-trace decision
- Keep errors

```yaml
SamplerType: dynamicsampler
SamplingFields: [error, status_code]
GoalSampleRate: 100
```

For: cost-effective full coverage.

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

**Mid**: "Wide events."

**Senior**: "Honeycomb model."

**Staff**: "Cardinality approach."

## Next Topic

→ [T05 — Splunk Observability](T05-Splunk.md)
