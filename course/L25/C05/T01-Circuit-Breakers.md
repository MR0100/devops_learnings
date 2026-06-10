# L25/C05/T01 — Circuit Breakers

## Learning Objectives

- Implement circuit breaker
- Avoid cascading failures

## Circuit Breaker

Pattern:
- Detect failing dependency
- Stop calling it
- Periodically test
- Resume when healthy

For: avoid cascading.

## States

- **Closed**: normal; calls flow
- **Open**: blocked; fail fast
- **Half-Open**: test; few calls

## Logic

```
fails > threshold → Open
After timeout → Half-Open
Probe succeeds → Closed
Probe fails → Open
```

## Why

Without:
- Slow dependency hangs all calls
- Threads exhausted
- Cascading

With:
- Fail fast
- Resources freed
- Quick recovery

## Implementation

Libraries:
- Hystrix (legacy, Netflix)
- Resilience4j (Java)
- Polly (.NET)
- pybreaker (Python)
- gobreaker (Go)

## Example

```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

@breaker
def call_external_service():
    return requests.get('https://external/api', timeout=5)
```

## Configuration

```python
fail_max=5         # 5 failures → open
reset_timeout=60   # try again after 60s
```

## Service Mesh

Istio outlier detection:
```yaml
trafficPolicy:
  outlierDetection:
    consecutive5xxErrors: 5
    interval: 30s
    baseEjectionTime: 30s
```

Per-instance breaker.

For: app-transparent.

## When Open

Return:
- Cached
- Default
- Error fast

```python
try:
    val = breaker(call_service)()
except CircuitBreakerError:
    val = cached_value or default
```

## Half-Open

Probe:
- One call
- If succeeds: close
- If fails: open again

## Best Practices

- Fail fast (timeout)
- Fallback (cache, default)
- Different breakers per dependency
- Monitor state changes
- Service mesh for auto

## Common Mistakes

- One breaker for everything
- No fallback (hard error)
- Wrong threshold (false positives)
- No monitoring

## Real Examples

### Netflix Hystrix
Pioneered concept.

### Many SaaS
Standard pattern.

## Quick Refs

```python
breaker = CircuitBreaker(fail_max=5, reset_timeout=60)
@breaker
def call(): ...

# Or
try: breaker.call(fn)
except CircuitBreakerError: fallback()
```

## Interview Prep

**Mid**: "Circuit breaker."

**Senior**: "Implement."

**Staff**: "Resilience patterns."

## Next Topic

→ [T02 — Bulkheads](T02-Bulkheads.md)
