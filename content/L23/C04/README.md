# L23/C04 — Application-Level Caching

## Topics

- **T01 In-Process vs Distributed** — Where the cache lives
- **T02 Caffeine, Guava, Ristretto** — Libraries

## In-Process vs Distributed

### In-Process (Local) Cache
- Cache in app's memory
- Sub-microsecond access
- Per-instance (each app instance has its own)
- Lost on restart
- Inconsistent across instances (without coordination)
- Limited by RAM per instance

### Distributed Cache (e.g., Redis)
- Network call (~1ms)
- Shared across instances
- Survives app restart
- Scales independently

### Use Both (Tiered)
- L1: in-process (super fast, eventually consistent)
- L2: distributed (shared truth)

L1 hit → no network. L1 miss → check L2 (network) → populate L1.

## Caffeine (Java)

The de-facto JVM cache library. Replaces Guava cache.

```java
LoadingCache<Long, User> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(5, TimeUnit.MINUTES)
    .refreshAfterWrite(1, TimeUnit.MINUTES)
    .recordStats()
    .build(userId -> userRepository.findById(userId));

User user = cache.get(42L);
```

### Why Caffeine
- Window TinyLFU eviction (smarter than LRU)
- Async loading
- Refresh while serving stale
- Stats built in
- Concurrent (no global lock)

## Guava Cache (Java, legacy)
- Predecessor of Caffeine
- Slower; less features
- Migrate to Caffeine

## Ristretto (Go)

```go
cache, _ := ristretto.NewCache(&ristretto.Config{
    NumCounters: 1e7,     // track frequency of 10M keys
    MaxCost:     1 << 30, // ~1GB cap
    BufferItems: 64,
})

cache.Set(key, value, cost)  // cost in bytes
val, ok := cache.Get(key)
```

- TinyLFU-based
- Async writes (buffer + batch)
- Cost-based (track size of values)

## Python: cachetools, functools.lru_cache

```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def expensive(x):
    return ...

from cachetools import TTLCache
cache = TTLCache(maxsize=10000, ttl=300)
cache[key] = value
```

`functools.lru_cache` is fast but no TTL; `cachetools` has TTL.

## Node.js: lru-cache

```javascript
import LRU from 'lru-cache';

const cache = new LRU({
  max: 10000,
  ttl: 5 * 60 * 1000,    // 5 min
});

cache.set('key', 'value');
const val = cache.get('key');
```

## Tiered Caching Pattern

```python
def get_user(user_id):
    # L1: in-process
    user = local_cache.get(f"user:{user_id}")
    if user: return user
    
    # L2: Redis
    user = redis.get(f"user:{user_id}")
    if user:
        local_cache.set(f"user:{user_id}", user)
        return user
    
    # L3: DB
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    redis.setex(f"user:{user_id}", 300, user)
    local_cache.set(f"user:{user_id}", user)
    return user
```

L1 invalidation is per-instance and complex; usually rely on TTL.

## Invalidation in Distributed In-Process Caches

If you must invalidate:
- Redis pub/sub: publish "invalidate user:42" → all instances listen and delete
- ETag-style version key: include version in cache key
- Short TTLs to bound staleness

## Negative Caching

Cache "doesn't exist" responses to avoid repeated DB hits:
```python
val = cache.get(key)
if val is NEG_SENTINEL: return None
if val: return val
val = db.fetch(key)
cache.set(key, val if val else NEG_SENTINEL, ttl=60)
return val
```

Without negative caching: same missing key hammers DB.

## Cache Stampede / Thundering Herd

Many concurrent requests miss cache → all hit DB.

Mitigations:
- Single-flight lock (only one goroutine fetches)
- Probabilistic early refresh (refresh before TTL expires for some requests)
- Pre-warming

## Interview Themes

- "In-process vs distributed cache — when each?"
- "Tiered cache design"
- "Caffeine — what makes it good?"
- "Cache stampede — mitigations"
- "Negative caching"
