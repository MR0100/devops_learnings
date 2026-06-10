# L18/C05/T03 — Sampling (Head vs Tail)

## Learning Objectives

- Choose sampling strategy
- Implement in OTel

## Why Sample

- Cost (storage)
- Network (export)
- Display (UI)

100% in dev. < 5% in prod typical.

## Head Sampling

At trace start:
- Decide: sample yes/no
- Mark in `traceparent` flags
- All services respect

Pro: simple, consistent.
Con: doesn't know if interesting (yet).

## Implementation

```bash
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.01   # 1%
```

If parent sampled: emit.
If parent not: skip.

For: consistent.

## Tail Sampling

After trace complete:
- All spans buffered (in Collector)
- Decide based on outcome:
  - Error: keep
  - Slow: keep
  - Else: 1%

Pro: keep interesting; drop boring.
Con: complex, memory.

## Tail in Collector

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
        latency: { threshold_ms: 1000 }

      - name: probabilistic
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }

      - name: customer-vip
        type: string_attribute
        string_attribute:
          key: tenant.tier
          values: [vip]
```

For: ANY policy matches → keep.

## Decision Wait

```yaml
decision_wait: 10s
```

Buffer trace for 10s; decide.

For: ensure all spans arrive.

## Memory

Buffer all traces. ~MB per trace.

For high volume: lots of RAM.

## Trade-Off Summary

| | Head | Tail |
|---|---|---|
| Complexity | low | high |
| Cost | low | higher (RAM) |
| Quality | random | high signal |
| Setup | env vars | Collector config |

## Combine

Head sample 50% → Tail keep errors + slow.

```yaml
# App SDK
OTEL_TRACES_SAMPLER_ARG=0.5

# Collector
tail_sampling: keep errors, drop ok at 10%
```

For: keep interesting, drop random.

## Adaptive

Some Collectors:
- Adjust rate based on volume
- Cap total spans/sec

## Per Service

```yaml
policies:
  - name: high-priority-svc
    type: and
    and:
      - name: svc
        type: string_attribute
        string_attribute: { key: service.name, values: [api] }
      - name: rate
        type: probabilistic
        probabilistic: { sampling_percentage: 50 }

  - name: noisy-svc
    type: and
    and:
      - name: svc
        type: string_attribute
        string_attribute: { key: service.name, values: [analytics] }
      - name: rate
        type: probabilistic
        probabilistic: { sampling_percentage: 1 }
```

For: per-service rate.

## Honeycomb Refinery

Dedicated tail-sampling proxy:
- Smart policies
- Dynamic
- Built for high cardinality

```yaml
SamplerType: dynamicsampler
SamplingFields: [error, status_code, service.name]
GoalSampleRate: 100
```

Auto-keep diverse representatives.

## Sampling Math

For SLO:
- 99.9% availability
- Need to keep most errors

If 100 req/sec, 0.1% errors = 0.1/sec.
Sample errors 100% = 0.1/sec emitted.
Sample success 1% = 1/sec emitted.

Total: 1.1/sec. Manageable.

## Always Sample

For specific traces:
```python
span.set_attribute("sampling.priority", 1)
```

Some samplers honor.

## Force Decision

```python
import opentelemetry.context as ctx
ctx_with_sample = ctx.set_value("sampled", True)
```

## Span vs Trace Sampling

OTel: trace-level decision propagates.

Span-level rarely useful.

## Cost Examples

Datadog APM:
- 1M spans = ~$X
- 10% sampling = 10× cost
- 1% sampling = manageable

For: budget.

## Best Practices

- Head sample low rate (1-5%)
- Tail sample to keep errors + slow
- Combine for best signal/cost
- Refinery for high-cardinality
- Monitor sampled vs total

## Common Mistakes

- 100% (cost)
- Random sampling misses errors
- Tail sample without enough RAM
- Wrong policy order

## Statistical

If 1% sample:
- Each kept trace represents ~100
- Account for in metrics

OTel automatically scales counts.

## Verify Sample Rate

```bash
# Total traces seen
opentelemetry_collector_received_traces_total

# Sampled
opentelemetry_collector_processed_traces_total
```

Ratio = sample rate.

## Quick Refs

```bash
# Head (SDK)
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.01

# Tail (Collector)
processors:
  tail_sampling:
    policies: [...]
```

## Interview Prep

**Mid**: "Head vs tail."

**Senior**: "Sampling policy design."

**Staff**: "Trace sampling at scale."

## Next Topic

→ Move to [L18/C06 — Tracing Tools](../C06/README.md)
