# L28/C03/T02 — Backpressure

## Learning Objectives

- Apply backpressure
- Avoid overload

## Backpressure

Signal upstream to slow down:
- Don't accept what can't handle
- Push back

## Why

Without:
- Queue grows
- Memory exhausted
- Crash

With:
- Bounded
- Drop excess
- Sustain

## Mechanisms

### Bounded Queue
```python
queue = Queue(maxsize=100)
# put() blocks if full
```

### Rate Limit
Cap requests/sec.

### Circuit Breaker
Stop calling failing.

### Connection Pool
Limit concurrent.

### LB
Refuse if backend overloaded.

## Reactive Streams

```
Subscriber requests N
Publisher emits up to N
Subscriber requests more
```

Pull-based; demand-driven.

## TCP

Built-in:
- Window
- Slow start
- Congestion control

For: free at transport.

## HTTP/2

Stream-level:
- Flow control per stream

For: well-designed.

## Examples

### Kafka Consumer
```python
consumer.pause(partition)
process()
consumer.resume(partition)
```

For: stop more messages.

### gRPC Streaming
Backpressure built-in.

### Akka / Reactor
Reactive patterns.

## Drop Excess

If backpressure:
- 429 Too Many Requests
- 503 Service Unavailable
- Retry-After header

For: graceful.

## Best Practices

- Bounded queues
- Rate limit
- 429 / 503 on overload
- Graceful degradation

## Common Mistakes

- Unbounded queues (OOM)
- No backpressure (cascading)
- 500 instead of 429 (wrong)

## Quick Refs

```
Bounded queue
Rate limit
Circuit breaker
429 / 503 + Retry-After
```

## Interview Prep

**Junior**: "What is backpressure?" — A mechanism for a system to signal upstream "slow down, I can't take more" instead of silently accepting work it can't handle. Without it, queues grow unbounded, memory exhausts, and the service crashes.

**Mid**: "How do you implement backpressure in practice?" — Bound your queues (a `Queue(maxsize=N)` that blocks or rejects when full), cap concurrency with connection/worker pools, and on overload return `429 Too Many Requests` or `503` with a `Retry-After` header rather than accepting and timing out. For pull-based consumers (Kafka), pause the partition when you're behind and resume when you catch up — demand-driven by design.

**Senior**: "Why is returning 429 better than just letting requests queue?" — A growing queue converts an overload into rising latency for *everyone*, then an OOM crash — you've turned a partial problem into a total outage. Shedding load with 429/503 keeps the system up and serving what it can, fails fast so clients can retry with backoff, and gives a clear signal instead of mysterious timeouts. Fast rejection is more available than slow acceptance.

**Staff**: "Design backpressure into a multi-stage pipeline so one slow stage doesn't collapse it." — Make demand flow backward: each stage pulls from a bounded buffer, so a slow downstream stage naturally throttles the upstream by not pulling — the bound propagates the signal without explicit messaging. At the ingress, shed with 429 + jittered Retry-After once buffers fill, so the spike sheds load instead of amplifying. Lean on transport-level flow control (TCP windows, HTTP/2 per-stream) for free, pair it with circuit breakers so a failing dependency stops receiving calls, and combine with graceful degradation (T03) so shedding drops the optional work first. The anti-pattern is one unbounded queue anywhere — it hides the backpressure until it's an OOM.

## Next Topic

→ [T03 — Graceful Degradation](T03-Graceful-Degradation.md)
