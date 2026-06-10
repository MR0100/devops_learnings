# L23/C01/T02 — Cache Coherence & Invalidation

## Learning Objectives

- Keep caches fresh
- Strategies

## Phil Karlton

"There are only two hard things in CS: cache invalidation and naming things."

## Coherence

All caches show same value or staleness within bounds.

## Strategies

### TTL
Expire after time:
```python
cache.set(key, value, ttl=300)
```

Pros: simple.
Cons: stale before TTL; thundering herd on expire.

### Explicit Invalidation
On write: delete cache key:
```python
db.update(...)
cache.delete(key)
```

Pros: fresh after write.
Cons: complexity; missed paths.

### Write-Through
Update both at write.

### Versioning
```python
cache_key = f"product:{id}:v{version}"
```

Bump version; old keys orphaned.

For: easy bulk invalidate.

### Cache Tags
```python
cache.set(key, val, tags=['product:123', 'category:5'])
```

Invalidate by tag:
```python
cache.delete_by_tag('product:123')
```

Tools: Redis with custom.

## Stale-While-Revalidate

```
Cache-Control: max-age=60, stale-while-revalidate=300
```

Serve stale while fetching fresh.

For: edge.

## Stale-If-Error

```
stale-if-error=86400
```

If origin down: serve stale up to 24 hr.

For: resilience.

## Distributed Coherence

For Redis cluster:
- Each shard own keys
- Invalidate per key

For: simple.

For app cache (per-instance):
- Each instance own
- Use TTL
- Or pub/sub for invalidation

## Pub/Sub Invalidation

```python
# Writer
db.update(...)
redis.publish('invalidate', key)

# All app instances subscribed
def on_invalidate(key):
    local_cache.delete(key)
```

For: in-process across instances.

## Write Patterns

(See T04.)

## Invalidation Anti-Patterns

### Forgot to Invalidate
Stale data forever.

### Over-Invalidate
Cache useless.

### Race
Read miss → DB → set cache
But: write happened between
Now: stale in cache

### Cache Stampede
Many requests on miss → all hit DB.

(See L23/C06.)

## CDN Invalidation

```bash
# CloudFront
aws cloudfront create-invalidation --distribution-id X --paths "/path/*"

# Cloudflare
curl -X POST .../purge_cache -d '{"files":["url"]}'
```

For: explicit.

## Cache Stamping

```python
val, generated_at = cache.get(key)
if generated_at < db.last_update(key):
    val = db.fetch(key)
    cache.set(key, val, generated_at=now)
```

For: explicit version.

## ETag

HTTP:
```
ETag: "abc123"
```

Client sends:
```
If-None-Match: "abc123"
```

Server: 304 Not Modified if same.

For: revalidation cheap.

## Last-Modified

```
Last-Modified: Wed, 01 Jan 2026 12:00:00 GMT
```

Client:
```
If-Modified-Since: ...
```

For: HTTP caching.

## Stale Data Acceptable

Some data:
- User profile: minutes OK
- Stock price: seconds maybe
- Banking balance: live

Per use case.

## Best Practices

- TTL + invalidation
- Versioning for bulk
- Tags where useful
- Stale-while-revalidate for resilience
- Monitor staleness

## Common Mistakes

- TTL only (always stale)
- No TTL (never expires)
- Missed invalidation paths
- Race conditions

## Quick Refs

```
TTL:        time-based
Invalidate: explicit
Versioning: bump version
Tags:       group invalidate
SWR:        stale + background refresh
```

## Interview Prep

**Mid**: "Cache invalidation."

**Senior**: "Strategies."

**Staff**: "Coherence."

## Next Topic

→ [T03 — LRU, LFU, ARC](T03-LRU-LFU-ARC.md)
