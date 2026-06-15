# L23/C01/T04 — Read-Through, Write-Through, Write-Back

## Learning Objectives

- Apply cache patterns
- Trade-offs

## Cache-Aside (Lazy Loading)

App manages:
```python
val = cache.get(key)
if val is None:
    val = db.fetch(key)
    cache.set(key, val, ttl=300)
return val
```

Pros: simple, flexible.
Cons: stale on update unless invalidate.

## Read-Through

Cache fetches on miss:
```python
val = cache.get(key)  # cache fetches from DB if missing
```

Cache (with provider) handles.

For: simpler app code.

## Write-Through

Write to cache + DB simultaneously:
```python
def update(key, val):
    cache.set(key, val)
    db.update(key, val)
```

Pros: cache always fresh.
Cons: write latency.

## Write-Back (Write-Behind)

Write to cache; async to DB:
```python
def update(key, val):
    cache.set(key, val)
    queue.put((key, val))   # background DB write
```

Pros: fast writes.
Cons: data loss if cache crashes before flush.

## Write-Around

Write to DB; skip cache:
```python
db.update(key, val)
# Don't touch cache
```

Cache populated on next read (cache-aside).

For: writes not soon read.

## Choosing

```
Cache-aside: most common; flexible
Read-through: simpler reads
Write-through: critical freshness
Write-back: write-heavy; tolerable loss
Write-around: writes not read soon
```

## Examples

### Web Page
Cache-aside for reads. Invalidate on write.

### Counter
Write-back for fast increments. Periodic flush.

### Session
Write-through; can't lose.

### Analytics
Write-back; OK if some lost.

## Hybrid

Different keys, different patterns:
- Hot user profile: write-through
- Counter: write-back
- Catalog: cache-aside

## Cache Layers

L1 (in-process) + L2 (Redis):
```
read: L1 → L2 → DB
write: write-through to L2; L1 invalidated
```

## Eviction Trigger

Even if cache-aside:
- Cache hit; serve
- Cache miss; fetch DB; populate
- Eviction: oldest removed (LRU)

## Pre-Warming

```python
def prewarm():
    for key in hot_keys:
        val = db.fetch(key)
        cache.set(key, val)
```

For: avoid cold start.

## Refresh-Ahead

Cache refreshes near TTL:
```python
if cache.ttl(key) < 60:
    val = db.fetch(key)
    cache.set(key, val)
```

For: avoid expiration miss.

## Negative Caching

```python
val = cache.get(key)
if val is None:
    val = db.fetch(key)
    if val is None:
        cache.set(key, NOT_FOUND, ttl=60)   # short
    else:
        cache.set(key, val, ttl=3600)
```

For: prevent DB hammering on misses.

## Consistency

Strong: write-through.
Eventual: write-back.

Trade-off.

## Best Practices

- Cache-aside default
- Write-through for critical
- Write-back for high-write
- Refresh-ahead for hot
- Negative cache for misses
- Monitor hit rate

## Common Mistakes

- Cache-aside without invalidation
- Write-back without flush guarantee
- No negative cache (DB hammer)
- TTL too long (stale)

## Quick Refs

```
Cache-aside:    app fetches; cache stores
Read-through:   cache fetches on miss
Write-through:  write cache + DB
Write-back:     write cache; async DB
Write-around:   write DB; skip cache

Negative cache: cache misses too
Refresh-ahead:  proactive refresh
```

## Interview Prep

**Mid**: "Cache patterns."

**Senior**: "Choose pattern."

**Staff**: "Cache architecture."

## Next Topic

→ Move to [L23/C02 — Redis](../C02/README.md)
