# L23/C01/T01 — Cache Hierarchies

## Learning Objectives

- Understand cache layers
- Design hierarchies

## Layers

```
Browser cache
↓
CDN (edge)
↓
LB cache
↓
App-level cache (in-process)
↓
Distributed cache (Redis)
↓
DB
```

Each layer: less origin load.

## Browser

- HTTP cache headers
- Cache-Control: max-age
- ETag
- Service worker

For: instant repeat visits.

## CDN

Edge cache:
- Cloudflare
- CloudFront
- Akamai
- Fastly

(See L23/C05.)

## LB

Some LBs cache:
- ALB no
- Cloudfront yes
- Nginx + cache

For: hot content.

## App In-Process

Per-process:
- Caffeine (Java)
- Ristretto (Go)
- functools.lru_cache (Python)

For: ultra-low latency.

## Distributed

Shared:
- Redis
- Memcached
- DynamoDB DAX

For: cross-instance.

## DB

Last resort. Cache misses hit DB.

## Layered Example

```
Request: /api/products/123
↓ Browser cache miss
↓ CDN cache miss
↓ App cache hit (Caffeine)
↓ ← respond
```

90% hit at app; 10% hit Redis; 1% DB.

## Latency Per Layer

```
Browser cache: 0 ms
CDN:           20 ms (edge)
App cache:     <1 ms
Redis:         1-5 ms
DB:            10-100 ms
```

Each layer: order of magnitude faster.

## TTL Strategy

Per layer:
- Browser: minutes-hours
- CDN: minutes-days
- App: seconds-minutes
- Redis: minutes-hours

For: progressively longer at edge.

## Invalidation

Tricky:
- Browser: can't invalidate (must wait for max-age)
- CDN: purge API
- App: in-process eviction
- Redis: DEL key

For: design carefully.

## Cache Hierarchy Patterns

### Read-Through
```
Client → Cache (miss) → DB
                     ← populate cache
        ← Return
```

### Cache-Aside
App handles:
```python
val = cache.get(key)
if val is None:
    val = db.fetch(key)
    cache.set(key, val, ttl=300)
return val
```

### Write-Through
```
Client → Cache → DB
                ← OK
       ← OK
```

### Write-Behind
```
Client → Cache → return
              ↓ later
              → DB
```

(See T04.)

## Cache Levels

- L1: in-process (CPU-cache-like)
- L2: local disk
- L3: distributed (Redis)
- L4: edge (CDN)

## Multi-Level Misses

If L1 miss, check L2, L3, L4.

For: better hit rate aggregate.

## Cost

- Browser/CDN: free for repeats (huge save)
- App in-process: RAM (cheap)
- Redis: RAM + ops
- DB: expensive

For: cache where cheapest.

## Best Practices

- Multiple layers
- Appropriate TTL per
- Invalidation strategy
- Monitor hit rate per
- Bypass cache for stale-critical

## Common Mistakes

- Single layer (load on Redis/DB)
- TTL same everywhere
- No invalidation plan
- Cache by request (no hit)

## Quick Refs

```
Browser → CDN → App → Redis → DB

Hit rate target:
  CDN: 80%+
  App cache: 70%+
  Redis: 90%+
```

## Interview Prep

**Mid**: "Cache layers."

**Senior**: "Design hierarchy."

**Staff**: "Caching at scale."

## Next Topic

→ [T02 — Cache Coherence & Invalidation](T02-Coherence-Invalidation.md)
