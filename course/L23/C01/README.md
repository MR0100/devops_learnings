# L23/C01 — Caching Theory

## Topics

- **T01 Cache Hierarchies** — Where caches live
- **T02 Cache Coherence & Invalidation** — Keep caches honest
- **T03 LRU, LFU, ARC** — Eviction strategies
- **T04 Read-Through, Write-Through, Write-Back** — Patterns

## Why Cache

> Compute is cheap; memory is faster than disk; disk is faster than network. Caching moves data closer to where it's needed.

Wins:
- Latency reduction (10× to 1000×)
- Throughput increase (offload DB)
- Cost reduction (fewer expensive queries)
- Availability (cached data survives DB blip)

## Cache Hierarchies

```
[Browser cache]     ms     (HTTP cache headers)
   ↓ miss
[CDN edge cache]    10ms   (CloudFront, Fastly)
   ↓ miss
[Reverse proxy cache]      (Varnish, Nginx)
   ↓ miss
[App-level cache]   1ms    (Redis, Memcached)
   ↓ miss
[DB query cache]
   ↓ miss
[Database]          10ms+
```

Each layer catches what it can; misses fall through.

## Cache Patterns

### Read-Through (Lazy)
1. App reads from cache
2. If miss, cache loads from DB
3. Cache returns to app

```python
def get_user(id):
    val = cache.get(f"user:{id}")
    if val: return val
    val = db.query("SELECT * FROM users WHERE id = ?", id)
    cache.set(f"user:{id}", val, ttl=300)
    return val
```

### Write-Through
1. App writes to cache + DB synchronously
2. Cache always consistent with DB

### Write-Back (Write-Behind)
1. App writes to cache
2. Cache writes to DB async
3. Faster writes, risk of loss if cache dies

### Cache-Aside
- App manages: read from cache; on miss, read DB and write to cache
- App invalidates cache on write to DB

Most common pattern.

## Invalidation Strategies

> "There are only two hard things in CS: cache invalidation and naming things." — Phil Karlton

### TTL (Time-Based)
- Set expiration
- Simple
- Stale data possible up to TTL

### Event-Driven
- DB write triggers cache invalidation
- Via CDC (Debezium) or app code
- More current; more complex

### Versioned Keys
- `user:42:v3` → on update, key becomes `user:42:v4`
- Old key untouched; falls out naturally
- Avoid stampede on invalidation

### Stale-While-Revalidate (SWR)
- Serve stale; refresh in background
- Used in CDNs and Next.js
- Combines freshness + availability

## Eviction Policies

When cache full, what to remove?

### LRU (Least Recently Used)
- Evict the item not used longest
- Good general default
- O(1) with linked list + hash map

### LFU (Least Frequently Used)
- Evict least accessed
- Bad for changing patterns (old hot items persist)

### FIFO
- Evict oldest
- Simple; usually worse than LRU

### TinyLFU + LRU (used in Caffeine/Ristretto)
- Track frequency with sketch
- Smarter than pure LRU
- Modern default in many systems

### ARC (Adaptive Replacement Cache)
- Self-tuning between LRU and LFU
- Used in ZFS

### Random
- Pick random victim
- Surprisingly OK as baseline

### Allkeys-LRU (Redis)
- Apply LRU to all keys (not just expired)
- Default for cache use

## Cache Hit Ratio

```
hit ratio = hits / (hits + misses)
```

- High (>90%) for hot keys
- Low (<50%) means cache underutilized or wrong things cached
- Track and alert on degradation

## Cache Sizing

- Total memory available
- Expected key count × avg value size + overhead
- Headroom for spikes (don't run at 95% capacity)

Redis tip: `INFO memory` for stats.

## When NOT to Cache

- Data changes faster than TTL benefits
- Read pattern non-uniform (rarely repeated)
- Strong consistency required (cache adds eventual lag)
- Cost of cache > saved compute/storage

## Interview Themes

- "Cache hierarchies — explain"
- "Cache-aside vs write-through"
- "Eviction policies — LRU vs LFU"
- "Cache invalidation — strategies"
- "Calculate cache hit ratio"
