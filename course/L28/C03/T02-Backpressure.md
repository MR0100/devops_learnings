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

**Mid**: "Backpressure."

**Senior**: "Implement."

**Staff**: "System design."

## Next Topic

→ [T03 — Graceful Degradation](T03-Graceful-Degradation.md)
