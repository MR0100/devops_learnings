# L23/C06/T02 — Cache Stampede

## Learning Objectives

- Recognize stampede
- Prevent

## Cache Stampede

Same as thundering herd; specifically for cache.

When key expires and many clients try to refetch.

## Symptoms

- DB CPU spike
- Latency spike
- Connection pool exhausted
- Cascading failures

## Why

```
Cache expires at T=0
T=0.001: 1000 requests all miss
T=0.002: 1000 DB queries
T=2.000: DB slow; queries pile up
T=10:   service down
```

## Patterns

### Mutex
```python
def get_cached(key):
    val = cache.get(key)
    if val: return val
    
    if redis.setnx(f"lock:{key}", 1):
        redis.expire(f"lock:{key}", 5)
        try:
            val = db.fetch(key)
            cache.set(key, val, ttl=300)
        finally:
            redis.delete(f"lock:{key}")
    else:
        # Spinning or fallback
        for _ in range(10):
            sleep(0.1)
            val = cache.get(key)
            if val: return val
        # Fallback: query DB directly (admit defeat)
        val = db.fetch(key)
    return val
```

## Probabilistic Early Expiration

```python
def get(key):
    val, expires_at = cache.get_with_expiry(key)
    now = time()
    delta = expires_at - now
    if delta < 0:
        # expired; fetch
        return refetch()
    # Probabilistic refresh
    if random() < (1 - delta / ttl) ** 2:
        spawn(refetch)
    return val
```

XFetch algorithm.

For: spreads load.

## Read-Through With SWR

```python
def get(key):
    val = cache.get_or_set_async(key, lambda: db.fetch(key), ttl=300)
    return val
```

Some libs handle: Caffeine, etc.

## Circuit Breaker

If origin overloaded:
- Stop hitting it
- Serve stale
- Or error

```python
if circuit.is_open():
    return cached_stale or None
val = db.fetch(key)
```

## Hot Key Detection

```promql
top_keys_by_request_rate
```

Special handling for hot:
- Longer TTL
- Pre-warmed
- Replicated

## Bursting

For known events (Black Friday):
- Pre-warm
- Extend TTL
- Increase capacity

## Best Practices

- Mutex on miss
- Stale-while-revalidate
- Probabilistic refresh
- Circuit breaker
- Hot key handling

## Common Mistakes

- No protection
- All clients refetch sync
- Long TTL with no jitter
- No metrics

## Real Examples

### CDN cold start
Cache server restart → all hit origin.

### Memcache crash
All cache lost; DB hit hard.

### Black Friday cache expiration
Bad timing → outage.

## Quick Refs

```python
# Mutex
if redis.setnx(lock_key, 1):
    val = db.fetch(...)
    cache.set(...)

# Probabilistic
if random() < (1 - delta / ttl) ** 2:
    refresh_async()
```

## Interview Prep

**Mid**: "Cache stampede."

**Senior**: "Mitigations."

**Staff**: "Design resilient cache."

## Next Topic

→ [T03 — Cache Penetration](T03-Cache-Penetration.md)
