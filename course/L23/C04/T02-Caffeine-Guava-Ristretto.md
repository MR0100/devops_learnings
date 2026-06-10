# L23/C04/T02 — Caffeine, Guava, Ristretto

## Learning Objectives

- Use modern in-proc caches
- Pick by language

## Caffeine (Java)

State of art:
- Window TinyLFU
- Async loading
- Refresh-ahead

```java
LoadingCache<String, User> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(5))
    .refreshAfterWrite(Duration.ofMinutes(1))
    .build(key -> fetchFromDB(key));
```

## Guava (Java)

Older; superseded by Caffeine for caching.

```java
LoadingCache<String, User> cache = CacheBuilder.newBuilder()
    .maximumSize(10000)
    .expireAfterWrite(5, TimeUnit.MINUTES)
    .build(new CacheLoader<>() { ... });
```

For: legacy / simpler.

## Ristretto (Go)

High-perf Go cache:
- TinyLFU
- Buffered writes
- High concurrency

```go
import "github.com/dgraph-io/ristretto"

cache, _ := ristretto.NewCache(&ristretto.Config{
    NumCounters: 1e7,
    MaxCost:     1 << 30,
    BufferItems: 64,
})

cache.Set("key", value, cost)
val, _ := cache.Get("key")
```

## bigcache (Go)

Alternative:
- No GC pressure
- Fast

```go
cache, _ := bigcache.NewBigCache(bigcache.DefaultConfig(10 * time.Minute))
cache.Set("key", []byte("value"))
```

## groupcache (Go)

Distributed-ish:
- Peer-to-peer
- No central
- Used by Google internally

## Python

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive(arg):
    return ...
```

Or `cachetools`:
```python
from cachetools import LRUCache, TTLCache

cache = TTLCache(maxsize=1000, ttl=300)
```

## Node.js

```javascript
import LRU from 'lru-cache';

const cache = new LRU({ max: 1000, ttl: 1000 * 60 * 5 });
cache.set('key', value);
const val = cache.get('key');
```

## C# / .NET

`MemoryCache`:
```csharp
var cache = new MemoryCache(new MemoryCacheOptions { SizeLimit = 1024 });
cache.Set(key, value, new MemoryCacheEntryOptions {
    AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5)
});
```

## Comparison

| | Caffeine | Ristretto | bigcache | Guava |
|---|---|---|---|---|
| Lang | Java | Go | Go | Java |
| Algorithm | W-TinyLFU | TinyLFU | shard | LRU |
| Hit rate | best | great | good | good |
| Maturity | very high | high | medium | high |

## Best Practices

- Caffeine for Java
- Ristretto for Go (perf)
- TTL set
- Monitor hit rate
- Right size

## Common Mistakes

- Too small (low hit rate)
- Too large (GC pressure)
- No TTL (stale forever)
- Wrong eviction policy

## Quick Refs

```java
// Caffeine
Caffeine.newBuilder()
  .maximumSize(N)
  .expireAfterWrite(D)
  .refreshAfterWrite(D)
  .build(loader)
```

```go
// Ristretto
ristretto.NewCache(&Config{NumCounters, MaxCost, BufferItems})
cache.Set / Get / Del
```

## Interview Prep

**Mid**: "In-proc cache."

**Senior**: "Caffeine algorithms."

**Staff**: "Performance caching."

## Next Topic

→ Move to [L23/C05 — CDN Strategy](../C05/README.md)
