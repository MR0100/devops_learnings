# L25/C05 — Resilience Patterns

## Topics

- **T01 Circuit Breakers** — Stop calling failing dependencies
- **T02 Bulkheads** — Isolate resources
- **T03 Retries with Backoff & Jitter** — Smart retry
- **T04 Timeouts (Done Right)** — Bound waiting
- **T05 Idempotency Keys** — Safe retries

(See also L19/C07 SRE chaos coverage; L25/C01-C03 chaos tools; this chapter is the *protective patterns* that chaos engineering validates.)

## Circuit Breaker

Three states:
- **Closed**: normal; requests pass through
- **Open**: rejecting requests; downstream is unhealthy
- **Half-Open**: test request to see if recovered

```
Closed → N failures in window → Open
Open → cooldown elapsed → Half-Open
Half-Open → success → Closed
Half-Open → failure → Open
```

### Example: Resilience4j (Java)
```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)              // 50% failure → open
    .waitDurationInOpenState(Duration.ofSeconds(10))
    .slidingWindowSize(20)
    .build();

CircuitBreaker cb = CircuitBreaker.of("paymentService", config);
String result = cb.executeSupplier(() -> paymentService.charge(amount));
```

### Why
- Stop hammering broken dep
- Give dep time to recover
- Fail fast (don't wait for timeout)

### Pitfalls
- Threshold too tight (flapping)
- No fallback (every request fails when open)
- Misses partial failures (some endpoints OK, others not)

## Bulkheads

Isolate failure domains.

### Thread Pool Bulkheads
```
Service A → thread pool 1 → downstream X
Service A → thread pool 2 → downstream Y
```

If X is slow and fills its thread pool, Y traffic unaffected.

### Resource Pool Bulkheads
- DB connections per service
- Memory per tenant
- Rate limit per route

### K8s Bulkheads
- Pod-level resource limits (one pod can't starve another)
- Namespace quotas
- Network policies

## Retry with Backoff + Jitter

### Naive Retry (Bad)
```python
for attempt in range(5):
    try:
        return call()
    except:
        sleep(1)        # constant delay
```

If many clients retry at same time → thundering herd on recovery.

### Exponential Backoff
```python
for attempt in range(5):
    try:
        return call()
    except:
        sleep(2 ** attempt)    # 1, 2, 4, 8, 16
```

Better, but still synchronized.

### Backoff + Jitter
```python
import random
for attempt in range(5):
    try:
        return call()
    except:
        delay = (2 ** attempt) * random.uniform(0.5, 1.5)
        sleep(delay)
```

Different clients pick different delays. Recovery isn't a thundering herd.

### Full Jitter (best)
```python
delay = random.uniform(0, 2 ** attempt)
```

Even more spread.

### Retry Budget
Track retry rate; if exceeds budget, stop retrying.

### Don't Retry On
- 4xx errors (client mistake; won't fix on retry)
- Non-idempotent ops without idempotency keys
- Long-tail latency (deepens the queue)

## Timeouts

### Set them. Always.
Most production incidents involve "no timeout" somewhere.

### Right size
- Too tight: spurious timeouts
- Too loose: thread/connection exhaustion

### Compose Timeouts
Higher levels = longer timeouts (composing across services).

```
Frontend timeout: 10s
API timeout to service A: 5s
Service A timeout to DB: 1s
```

Each level adds margin.

### Connection vs Read vs Total
- Connection: time to establish TCP/TLS
- Read: time between bytes
- Total: end-to-end

Set all three.

### Cancellation Propagation
When a request times out, cancel downstream work.

```go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()
result, err := db.QueryContext(ctx, "SELECT ...")
```

Without cancellation: work continues, wastes resources.

## Idempotency Keys

Make retries safe.

```http
POST /charges
Idempotency-Key: abc-123
Content-Type: application/json

{"amount": 1000, "customer": "cust_42"}
```

Server stores key → response. Same key replayed → returns cached response. No duplicate charge.

### Lifetime
- Key TTL: 24h to 1 week
- Storage: Redis or DB
- Status codes: client retried on 5xx → may see "already processed"

### Stripe pioneered this for payments. Now standard for any non-idempotent op.

## Hedging

Send a second request after p99 delay; first response wins.

```
Send request to backend A
Wait for p99 timeout (say 200ms)
If no response: send request to backend B
First response wins; cancel the other
```

Trade more requests for better tail latency. Used by Google search.

## Load Shedding

When overloaded, reject requests early (with 503) rather than queue forever.

```python
if queue.depth > threshold:
    return 503
process(request)
```

Better to fail fast than slow.

## Graceful Degradation

When dependency fails, return partial response.

- Recommendation engine down → show non-personalized feed
- Search down → return cached or basic listing
- Image CDN down → show placeholder

Communicate degradation in API responses if needed.

## Combining Patterns

Modern resilient client:
1. Idempotency key on writes
2. Timeout per request
3. Circuit breaker around dependency
4. Retry with jitter on failure
5. Hedge for tail latency
6. Bulkhead for thread isolation
7. Graceful degradation when nothing works

Implement as middleware / library so every service gets it.

### Tools
- Resilience4j (Java)
- Polly (.NET)
- Failsafe (Java)
- Hystrix (Netflix; maintenance mode)
- Service mesh (Istio, Linkerd) — many patterns at sidecar level

## Interview Themes

- "Circuit breaker — explain"
- "Backoff + jitter — why jitter?"
- "Idempotency key — how implement?"
- "Bulkhead pattern"
- "Hedging — when valuable?"
- "Compose resilience patterns"
