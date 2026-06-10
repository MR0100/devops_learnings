# L18/C01/T03 — Log Sampling Strategies

## Learning Objectives

- Reduce log volume
- Preserve signal

## Why Sample

- Cost (storage + transport)
- Performance (write overhead)
- Searchability (less to grep)

For: high-volume.

## Random Sampling

```python
if random.random() < 0.01:
    log.debug("verbose", ...)
```

1% of events.

Pro: simple.
Con: may miss interesting.

## Reservoir Sampling

K random out of stream:
```python
# Keep K samples; replace randomly
```

For: representative sample.

## Adaptive

If rate spikes:
- Sample less
- Stay under cap

For: backpressure-aware.

## Head Sampling (Decide Early)

At request start:
```python
should_sample = random.random() < 0.01
if should_sample:
    span.set_attribute("sampled", True)
# All subsequent logs / spans for request: same decision
```

Pro: consistent per-request.
Con: don't know yet if interesting.

## Tail Sampling (Decide Late)

Buffer all request data:
- If error: keep 100%
- If slow: keep 100%
- Else: 10%

Pro: keeps interesting; drops boring.
Con: complex; memory.

OTel Collector tail sampling:
```yaml
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 1000 }
      - name: random
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }
```

## Per-Endpoint

```python
RATES = {
    '/health': 0.001,    # rare
    '/api/checkout': 1.0,  # always
    '/api/users': 0.1,    # sample
}

if random.random() < RATES.get(endpoint, 1.0):
    log.info(...)
```

For: critical endpoints fully logged.

## Per-User

```python
if user.id % 100 == 0:
    log.debug(...)
```

Same user always sampled. Consistent.

## Error Always

```python
if level == "error" or response.status >= 500:
    log.error(...)  # always
else:
    if random.random() < 0.1:
        log.info(...)
```

For: errors 100%, success 10%.

## Rate Limit

```python
from token_bucket import TokenBucket
bucket = TokenBucket(rate=100, capacity=100)  # 100/sec

if bucket.consume(1):
    log.info(...)
else:
    # drop
```

Hard cap. Avoid bursts overwhelming.

## Time-Window

```python
last_logged = {}
def log_periodic(key, msg, interval=60):
    now = time.time()
    if now - last_logged.get(key, 0) > interval:
        log.info(msg)
        last_logged[key] = now
```

Log a message at most once per minute.

For: repeated events.

## Volume Caps

Per service:
- Max X GB/day
- If exceeded: sample more aggressively
- Or drop

Tools (Datadog): per-host index budget.

## Cost Analysis

For 1 TB/day logs at $0.10/GB indexed:
```
1000 * $0.10 * 30 = $3000/mo per TB
```

Sample 1%:
```
$30/mo
```

Significant.

## Sampling vs Filtering

- Sampling: random subset
- Filtering: drop based on content

Both useful.

```yaml
# Filter (drop)
- match:
    namespace: "kube-system"
  drop
```

## OTel Sampling

Trace samplers:
- always_on
- always_off
- traceidratio (0.01 = 1%)
- parentbased
- ratelimiting
- tail (in Collector)

## Per-Level

```python
SAMPLE_RATES = {
    "debug": 0.001,
    "info": 0.1,
    "warn": 1.0,
    "error": 1.0
}

if random.random() < SAMPLE_RATES[level]:
    log(...)
```

## Trace-Aware

If trace_id is "interesting" (slow, error):
- Keep its logs

Else: sample.

For: correlated keep.

## Sticky Sampling

Same request_id → consistent decision:
```python
import hashlib
h = hashlib.md5(request_id.encode()).hexdigest()
should_sample = int(h, 16) % 100 < 10  # 10%
```

For: full request kept or all dropped.

## Best Practices

- Errors 100%
- Critical endpoints 100%
- Health checks rare
- Sample noisy
- Document rates
- Monitor drop rate

## Common Mistakes

- Sample errors (lose critical)
- Same rate everywhere
- No monitoring (drops invisible)
- Hardcoded (no tuning)

## Measuring

```python
log.info("event", sampled=True, sample_rate=0.01)
```

When analyzing: weight by rate.

## Tools

- Logstash: drop / sample filters
- Fluent Bit: built-in sample
- OTel Collector: tail sampling
- Datadog: index sampling

## Quick Refs

```
Head:        decide at start
Tail:        decide after request done
Probabilistic: random fraction
Rate limit:  hard cap
Per-endpoint: critical always
Errors:      always
```

## Interview Prep

**Mid**: "Log sampling."

**Senior**: "Tail sampling."

**Staff**: "Sampling strategy."

## Next Topic

→ Move to [L18/C02 — ELK Stack](../C02/README.md)
