# L23 — Caching & CDN

## Overview

Latency is a feature. Caching at every layer is how modern systems hit p99 < 100ms. This lecture covers caching theory, Redis, CDN strategy, and failure modes.

**6 chapters, 19 topics.**

## Chapter Map

### [C01](C01/) — Caching Theory
- T01 Cache Hierarchies
- T02 Cache Coherence & Invalidation
- T03 LRU, LFU, ARC
- T04 Read-Through, Write-Through, Write-Back

### [C02](C02/) — Redis
- T01 Data Types Deep Dive
- T02 Persistence (RDB, AOF)
- T03 Replication, Sentinel, Cluster
- T04 Lua Scripting
- T05 Redis Modules (Bloom, JSON, Search)

### [C03](C03/) — Memcached
- T01 Simplicity vs Redis

### [C04](C04/) — Application-Level Caching
- T01 In-Process vs Distributed
- T02 Caffeine, Guava, Ristretto

### [C05](C05/) — CDN Strategy
- T01 CloudFront, Cloudflare, Fastly, Akamai
- T02 Edge Computing (CF Workers, Lambda@Edge)
- T03 Cache Keys & Vary Headers
- T04 Image Optimization at Edge

### [C06](C06/) — Cache Failure Modes
- T01 Thundering Herd
- T02 Cache Stampede
- T03 Cache Penetration
- T04 Hot Keys

## Cache Hierarchy (Typical Web App)

```
User
 │
 ▼
[CDN edge] (static + cacheable HTML, ~10ms)
 │ miss
 ▼
[Load Balancer]
 │
 ▼
[App-level cache] (Redis, Memcached)
 │ miss
 ▼
[Database]
```

## Cache Strategies

| Strategy | Behavior |
|---|---|
| Read-through | App reads from cache; cache loads from DB on miss |
| Write-through | App writes to cache and DB synchronously |
| Write-back | App writes to cache; DB written async (risky) |
| Write-around | App writes only to DB; cache populates on next read |

## Invalidation

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

Common approaches:
- TTL (time-based)
- Event-driven invalidation (CDC, pub/sub)
- Stale-while-revalidate (serve stale, refresh async)
- Versioned keys (`user:42:v3` → new key on update)

## Failure Modes

### Thundering Herd / Cache Stampede
N concurrent requests miss cache, all hit DB.
**Fix**: locks (probabilistic early refresh), request coalescing.

### Cache Penetration
Repeated queries for non-existent keys bypass cache.
**Fix**: cache the negative result (null), or Bloom filter.

### Hot Keys
One key gets disproportionate traffic.
**Fix**: replicate to multiple cache nodes, client-side caching.

### Cache Avalanche
Mass eviction at the same time.
**Fix**: randomize TTLs (jitter).

## Redis Production Notes

- Single-threaded — don't run slow Lua scripts; use multiple instances
- Cluster for >50GB or for write throughput beyond single-node
- Sentinel for failover (without cluster)
- AOF + everysec for durability balance
- maxmemory-policy: allkeys-lru is common for caches

## CDN Cache Keys

A cache key typically: URL + Host + selected headers (via `Vary`).

Pitfalls:
- `Vary: User-Agent` explodes cache cardinality
- Cookies invalidate cache (configure CDN to ignore cookies for static)
- Different paths for same content → multiple keys

## Edge Computing

Run code at the edge:
- Cloudflare Workers (V8 isolates, ~5ms cold start)
- Lambda@Edge (heavier, slower)
- Fastly Compute (WebAssembly)

Use cases: auth at edge, A/B testing, geo-routing, custom logic per request.

## Recommended Reading

- *Designing Data-Intensive Applications* — Ch 1 (caching), Ch 5 (replication)
- *Redis in Action* — Josiah Carlson
- Cloudflare engineering blog

## Interview Themes

- "Walk me through cache strategies and tradeoffs"
- "Cache stampede — what is it and how to fix?"
- "Design a CDN cache strategy"
- "Redis vs Memcached"
- "Edge computing — when?"

## Next

→ [L24 — Production Networking](../L24/README.md)
