# L23/C04/T01 — In-Process vs Distributed

## Learning Objectives

- Choose cache type
- Combine

## In-Process

In app memory:
- functools.lru_cache (Python)
- Guava / Caffeine (Java)
- Ristretto (Go)
- node-cache (Node)

Pros:
- Sub-microsecond access
- No network
- Free

Cons:
- Per instance (not shared)
- Lost on restart
- Memory pressure on app

## Distributed

Network cache:
- Redis
- Memcached

Pros:
- Shared across instances
- Survives app restart
- Scale independently

Cons:
- Network latency (1-5 ms)
- Operational

## Layered

L1 + L2:
```
read:
  L1 (in-process)
  miss → L2 (Redis)
  miss → DB
  populate L1 + L2

write:
  L2.set
  invalidate L1
```

For: best of both.

## L1 Eviction

In-process limited:
- Small (KB-MB per instance)
- LRU eviction

For: hottest items only.

## Distributed Invalidation

App writes to DB:
```
db.update()
redis.del(key)
publish('invalidate', key)
# All instances drop L1 entry
```

For: coherence.

## Examples

### Caffeine + Redis (Java)
```java
LoadingCache<String, User> cache = Caffeine.newBuilder()
    .maximumSize(10000)
    .expireAfterWrite(1, TimeUnit.MINUTES)
    .build(key -> {
        return redis.get(key) ?: db.fetch(key);
    });
```

### Python
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user(user_id):
    # Check Redis first
    val = redis.get(f"user:{user_id}")
    if val: return val
    val = db.fetch(user_id)
    redis.set(...)
    return val
```

## When In-Process Only

- Stable read; rare write
- Per-instance OK
- Latency critical

## When Distributed Only

- Frequent invalidation
- Memory expensive
- Smaller working set per instance

## When Both

- High traffic
- Hot items
- Need consistency some

## Hit Rate Analysis

If L1 hit rate 90%:
- 90% requests served < 1 µs
- 10% hit L2 (1-5 ms)
- 1% hit DB (slow)

Massive improvement.

## Memory Allocation

For 16 GB app instance:
- 50% app
- 30% L1 cache
- 20% headroom

For: cache-heavy apps.

## Best Practices

- L1 small, hot
- L2 larger, broader
- Coherence via invalidation
- Monitor hit rate per layer

## Common Mistakes

- L1 only (instances out of sync)
- L2 only (network on every access)
- No invalidation (stale L1)
- Huge L1 (memory pressure)

## Quick Refs

```
In-process: functools.lru_cache, Caffeine, Ristretto, Guava
Distributed: Redis, Memcached
Pattern: L1 + L2 + DB
Invalidate: pub/sub or TTL
```

## Interview Prep

**Mid**: "In-proc vs Redis."

**Senior**: "Multi-layer cache."

**Staff**: "Cache strategy."

## Next Topic

→ [T02 — Caffeine, Guava, Ristretto](T02-Caffeine-Guava-Ristretto.md)
