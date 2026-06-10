# L23/C06/T01 — Thundering Herd

## Learning Objectives

- Avoid thundering herd
- Mitigate

## Thundering Herd

Many waiters wake up; all try to fetch:
- Cache expires → all check DB
- One DB query becomes 1000s
- DB overload

## Causes

- Cache key expires
- Cache eviction
- Cache server restart
- High traffic on cold key

## Example

```
T=10: cache.get(key) → MISS
T=10: 1000 instances all hit DB simultaneously
T=11: DB melts
```

## Mitigations

### Single Flight

Only one fetch; others wait:
```python
lock = redis.lock(f"fetch:{key}")
if lock.acquire():
    try:
        val = db.fetch(key)
        cache.set(key, val)
    finally:
        lock.release()
else:
    # Wait then check cache
    sleep(0.1)
    val = cache.get(key)
```

For: one fetch.

### Probabilistic Expiration

```python
if cache_age > ttl * 0.9 and random() < (cache_age - ttl * 0.9) / (ttl * 0.1):
    refresh()
return cached_value
```

Some refresh early; spread load.

### Stale-While-Revalidate

Serve stale; refresh in background:
```python
val, age = cache.get_with_age(key)
if age > ttl:
    return val   # stale
elif age > ttl * 0.9:
    spawn(refresh, key)
    return val   # fresh enough
return val
```

For: never empty cache.

### Pre-Warming

Before peak:
```python
for key in hot_keys:
    cache.set(key, db.fetch(key))
```

## Cache-Aside with Lock

```python
def get(key):
    val = cache.get(key)
    if val is not None:
        return val
    
    with redis_lock(f"lock:{key}"):
        val = cache.get(key)  # double check
        if val is not None:
            return val
        val = db.fetch(key)
        cache.set(key, val, ttl=300)
    return val
```

## Negative Cache

```python
val = cache.get(key)
if val == NOT_FOUND:
    return None
if val is None:
    val = db.fetch(key)
    cache.set(key, val or NOT_FOUND, ttl=60)
return val
```

For: prevent DB hammering on missing items.

## TTL Jitter

```python
ttl = 300 + random.randint(0, 60)
cache.set(key, val, ttl=ttl)
```

Spread expirations.

## Real Examples

### Twitter
Famous outages from thundering herd.

### Many sites
Cache server restart → traffic spike.

## Mitigations Summary

- Single-flight (Redis lock)
- Probabilistic refresh
- Stale-while-revalidate
- Pre-warming
- Negative caching
- TTL jitter

## Best Practices

- Multiple mitigations layered
- Test under load
- Monitor cache stampede signals
- Circuit breaker on origin

## Common Mistakes

- No protection (assume cache always populated)
- Long TTL (fewer events but big stampedes)
- Synchronous fetch (block many)
- No monitoring

## Quick Refs

```python
# Single flight
with redis_lock(key):
    val = db.fetch(key)
    cache.set(key, val)

# Stale
val, age = cache.get_with_age(key)
if age > refresh_threshold:
    spawn(refresh, key)
return val

# Jitter
ttl = base + random.randint(0, jitter)
```

## Interview Prep

**Mid**: "Thundering herd."

**Senior**: "Mitigate."

**Staff**: "Cache stampede design."

## Next Topic

→ [T02 — Cache Stampede](T02-Cache-Stampede.md)
