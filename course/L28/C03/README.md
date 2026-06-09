# L28/C03 — Reliability Patterns

## Topics

- **T01 Idempotency** — Safe retries
- **T02 Backpressure** — Don't accept what you can't handle
- **T03 Graceful Degradation** — Reduce functionality, not availability

## Idempotency

> An operation is idempotent if performing it N times has the same effect as performing it once.

GET, PUT, DELETE: usually idempotent.
POST: usually not.

### Why Critical
- Retries need to be safe
- Network failures cause duplicate requests
- Message queues are at-least-once

### Implementation: Idempotency Key

Client generates unique key per logical operation:
```http
POST /charges
Idempotency-Key: ord-abc-123
Content-Type: application/json
{"amount": 1000, "customer": "c_42"}
```

Server stores key + response. Replay → return cached response.

### Storage
- Redis with TTL
- DB table
- Stripe uses key for 24h

### Key Generation
- UUID per business operation
- Hash of (user_id + order_id + ts) for deterministic
- Don't reuse keys (defeats purpose)

## Backpressure

When system is overloaded, push back rather than queue indefinitely.

### Push Back Patterns
- Return 429 (Too Many Requests) + Retry-After
- Return 503 (Service Unavailable) + Retry-After
- Reject TCP (refused connection)
- Drop low-priority work

### Don't Just Queue
A queue that grows unbounded is hiding the problem:
- Memory exhausts
- Latency grows
- Eventually crashes
- Cascading failure

### Bounded Queues
```
Queue size: 1000
On enqueue: if full, drop or 429
```

Force decisions: which work matters?

## Graceful Degradation

When dependency fails, reduce functionality, don't fail entire request.

### Examples
- Recommendation engine down → show non-personalized feed
- Search index down → return cached or simpler results
- Image CDN down → show placeholder
- Real-time tracker down → show last-known location
- Personalization service down → generic homepage

### Implementation
```python
def homepage(user):
    try:
        recs = recommendations.get(user, timeout=200ms)
    except (TimeoutError, ServiceUnavailable):
        recs = static_top_10()    # fallback
    
    feed = render(recs)
    return feed
```

### Trade-offs
- Some features lost during failure
- User still served
- Better than full outage

## Circuit Breaker (Recap)

Stop hammering dead service. Three states: closed, open, half-open.

After N failures: open. After cooldown: try one (half-open). Success: close.

## Bulkheads (Recap)

Isolate failure domains.
- Per-dependency thread pool
- Per-tenant resource limit
- Pod resource limits (one bad pod doesn't starve neighbors)

## Retries with Jitter

Synchronized retries cause thundering herd. Add jitter:
```python
delay = random.uniform(0, 2 ** attempt)
```

## Timeouts

Set them. Always. Right-size. Compose (higher levels longer).

## Load Shedding

Drop work proactively when overloaded:
```python
if cpu_usage > 80:
    if request.priority == "low":
        return 503
```

Better to fail some than degrade all.

## Failure Injection

Use chaos engineering (L25) to verify reliability patterns work.

## Watchdogs

Detect stuck processes / threads:
- Heartbeat from worker
- No heartbeat in N seconds → kill + restart

K8s liveness probes do this for pods.

## Health-Aware Routing

LB / mesh routes around unhealthy:
- Active health checks
- Passive health checks (failure rate)
- Outlier detection (eject misbehaving)

## Hedging Requests

Send a duplicate after p99 timeout:
```
t=0: request to A
t=200ms (p99): no response yet; send to B
First response: win
Cancel the other
```

Trades cost for tail latency.

## Idempotency Combined with Retries

```
client                server
   │ POST /charge
   │ Idempotency-Key: abc-123
   │ ──────────────────→
   │   (server crashes mid-process)
   │ (timeout; retry)
   │ POST /charge
   │ Idempotency-Key: abc-123
   │ ──────────────────→
   │   server: "I've seen this key; return prev result"
   │ ←──────────────────
   │ 200 OK (no double charge)
```

The combo: client retries safely; server dedupes.

## Cascading Failure Prevention

```
Without backpressure:
A → B (slow) → A times out → retries → more load → B slower → more timeouts → cascade

With backpressure:
A → B (slow) → A circuit breaks → fast fail → A serves degraded → B recovers
```

## Slow Failures Worst

A service that fails fast is annoying. A service that succeeds slowly is catastrophic.

Always: timeout aggressively; fail fast.

## Production Examples

### Stripe
- Idempotency keys on every write
- Retry-after headers
- Graceful degradation for non-core features

### Netflix
- Hystrix (circuit breaker; now maintenance mode)
- Resilience patterns library
- Chaos engineering pioneered

### Cloudflare
- Edge degradation (serve stale on origin failure)
- Aggressive timeouts
- Backpressure built into core

## Interview Themes

- "Idempotency — why and how implement"
- "Backpressure — why not just queue?"
- "Graceful degradation example"
- "Cascading failure — prevent"
- "Combine resilience patterns"
