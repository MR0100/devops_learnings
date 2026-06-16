# L23/C06 — Cache Failure Modes

## Topics

- **T01 Thundering Herd** — Many concurrent misses
- **T02 Cache Stampede** — Similar; variants
- **T03 Cache Penetration** — Requests bypass cache
- **T04 Hot Keys** — Single key dominates

## Thundering Herd / Stampede

A popular key expires. 1000 concurrent requests miss → all hit DB simultaneously → DB overloaded.

```
t=0:    cached_value (5 min TTL)
t=300:  TTL expires
t=300+ε: 1000 reqs/sec start missing
        1000 reqs/sec hit DB
        DB CPU 100%, slow → cascade failure
```

### Mitigations

#### 1. Single-Flight Lock
Only one process fetches; others wait.
```python
def get(key):
    val = cache.get(key)
    if val: return val
    if lock.acquire(key, timeout=5):
        try:
            val = cache.get(key)  # double-check after lock
            if val: return val
            val = db.fetch(key)
            cache.set(key, val, ttl=300)
            return val
        finally:
            lock.release(key)
    else:
        # waited; cache should be populated
        return cache.get(key) or db.fetch(key)
```

#### 2. Probabilistic Early Refresh (XFetch)
Refresh before TTL with increasing probability as expiry approaches.

```python
import random
import math

def xfetch(key, beta=1.0):
    val, ttl, computed_in = cache.get_with_metadata(key)
    if val and random.random() < math.exp(-beta * computed_in * math.log(random.random()) / ttl):
        return val
    val = db.fetch(key)
    cache.set_with_metadata(key, val, ttl, time.elapsed)
    return val
```

#### 3. Randomized TTL (Jitter)
Don't expire all keys at same time:
```python
ttl = base_ttl + random.randint(0, 60)  # 5-6 min instead of exactly 5
```

#### 4. Stale-While-Revalidate
Serve stale; refresh async.

## Cache Penetration

Requests for non-existent keys hit DB every time (cache never has them).

Attack vector: request `/api/user/<random_uuid>` repeatedly → DB hammered.

### Mitigations

#### Negative Caching
Cache the "not found" result:
```python
val = cache.get(key)
if val == NULL_SENTINEL: return None
if val: return val
val = db.fetch(key)
cache.set(key, val if val else NULL_SENTINEL, ttl=60)
return val
```

#### Bloom Filter
Pre-check existence:
```python
if not bloom_filter.might_exist(key):
    return None  # definitely not there
val = cache.get(key) or db.fetch(key)
```

False positives possible (might_exist returns True for some non-existent); never false negatives.

#### Rate Limit Per Source
Block clients hitting many unique non-existent keys.

## Cache Avalanche

Many keys expire at once → DB overwhelmed (similar to thundering herd but cluster-wide).

Causes:
- Cache restart (everything cold)
- Synchronized TTL (all set at app start with same TTL)
- Mass invalidation

### Mitigations
- Pre-warm cache after restart
- Randomized TTL (jitter)
- Tiered cache (L1 in-process retains during L2 restart)
- Graceful degradation (limited functionality during cache outage)

## Hot Keys

One key dominates request volume.

```
99% of requests for /api/featured-product (single popular item)
Redis instance owning that key saturates network
```

### Symptoms
- One Redis shard at 100% CPU/network; others idle
- Latency spike on that key
- `redis-cli --hotkeys` (Redis 4.0+) identifies

### Mitigations

#### Client-Side Caching
Cache popular items in in-process cache (sub-microsecond access).

#### Key Replication
Shard the key:
```
/api/featured-product:0
/api/featured-product:1
...
/api/featured-product:9
```

Client picks random suffix. Spreads load across 10 keys (potentially 10 shards).

#### Read-Through to Read Replicas
For Redis: read from replicas (`READONLY` after MOVED, or use replica-aware client).

#### Dedicated Tier
Move the hot key to its own dedicated cache instance.

## Network / Cache Unavailable

Cache server down → app must handle:

### Fallback to DB
- App detects cache unavailable; fetches from DB directly
- Risk: DB overload (didn't expect that traffic)

### Circuit Breaker
- Detect cache unhealthy; bypass it
- After timeout, try cache again
- Avoid: cascading retries (each call waits for cache, times out)

### Graceful Degradation
- Some features disabled when cache unhealthy
- E.g., recommendations off, basic listing still works

## Cache Inconsistency

Cache + DB out of sync.

### Causes
- Write to DB, fail to invalidate cache
- Race between writer A (sets key) and writer B (sets key)
- Replication lag (replica returns stale read; cache stores stale)

### Mitigations
- Write-through (atomic cache + DB updates)
- Short TTLs to bound staleness
- Event-driven invalidation via CDC

## Memory Pressure

Cache server OOM → process killed.

### Causes
- Unbounded keys (no expiration)
- Memory leak (large values)
- Surge of writes

### Mitigations
- `maxmemory` + eviction policy
- Monitor and alert on memory usage
- Cap value size at app layer (don't cache 100MB items)

## Operational Best Practices

- Monitor: hit ratio, p99 latency, memory, evictions
- Alert: hit ratio drop, memory > 80%, replication lag
- Capacity: 30% headroom for cache memory
- Pre-warming for known hot keys after restart
- Game day: kill cache; verify app degrades gracefully
- Quarterly: review what's cached; remove stale

## Interview Themes

- "Thundering herd — diagnose and fix"
- "Cache penetration vs cache avalanche"
- "Hot key — strategies"
- "Cache + DB inconsistency"
- "Graceful degradation on cache failure"
