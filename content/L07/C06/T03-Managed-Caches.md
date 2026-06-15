# L07/C06/T03 — Managed Caches (ElastiCache, Memorystore)

## Learning Objectives

- Use caches correctly
- Avoid stampede / inconsistency

## Cache

In-memory KV store. Microsecond-latency. Volatile or persistent.

Used for:
- Speed up DB queries
- Session storage
- Rate limiting
- Queues / pub-sub (Redis)
- Counters

## ElastiCache (AWS)

Two engines:
- **Redis**: rich data types, persistence, replication, pub/sub, Lua
- **Memcached**: simple KV, multi-threaded

Redis far more popular for new apps.

### Redis Variants
- ElastiCache for Redis (single primary + replicas)
- ElastiCache Serverless (auto-scale)
- MemoryDB for Redis (durable; primary DB usage)

## Memorystore (GCP)

Redis or Memcached. Similar offering.

## Cache Patterns

### Cache-Aside (Lazy Loading)
```python
def get_user(id):
    cached = cache.get(f"user:{id}")
    if cached:
        return json.loads(cached)
    user = db.query(...)
    cache.set(f"user:{id}", json.dumps(user), ex=3600)
    return user
```

Pros: cache only what's used.
Cons: first request slow; cache misses hit DB.

### Write-Through
```python
def save_user(user):
    db.save(user)
    cache.set(f"user:{user.id}", json.dumps(user))
```

Pros: cache always fresh.
Cons: writes slower; unread items still cached.

### Write-Behind
Write to cache; flush to DB later (queue). Risk on cache failure.

### Refresh-Ahead
Refresh before expiry; reduces cache misses.

## Invalidation

The hard problem.

```
User updates profile
↓
DB updated
↓
Cache stale (until TTL or invalidate)
```

Strategies:
- TTL (stale tolerable)
- Explicit invalidate on write
- Pub-sub: write → publish; subscribers invalidate
- Versioned keys: increment version on update

## TTL

Set expiration:
```
SET user:1 "data" EX 3600
```

After 1 hour, evicted. Cache returns nil; cache-aside fetches fresh.

## Eviction Policies

When memory full:
- LRU (least recently used)
- LFU (least frequently used)
- TTL (expired first)
- random
- no-eviction (write fails)

`maxmemory-policy allkeys-lru` typical.

## Redis Data Types

- Strings
- Hashes (object-like)
- Lists (queue, stack)
- Sets (unique items)
- Sorted Sets (scored, ordered)
- Streams (durable log)
- HyperLogLog (cardinality)
- Bitmap, Geospatial, etc.

Use the right type:
- User session: Hash
- Recent items: List
- Unique counter: Set / HLL
- Leaderboard: Sorted Set
- Rate limit: counter with EXPIRE

## Cluster

For scale beyond one node:
- Redis Cluster: shards across nodes; client routes to shard
- ElastiCache Cluster Mode Enabled

Each key hash → shard. Pipelining requires keys in same shard ({hash_tag}).

## Persistence

- RDB: snapshots
- AOF: append-only log; durable
- Hybrid

For pure cache: no persistence (faster, cheaper).
For session / important data: AOF.

MemoryDB: Redis API with durability of DB.

## Common Failures

### Cache Stampede
TTL expires; many clients fetch from DB at once; DB overloaded.

Mitigations:
- Probabilistic early refresh (refresh slightly before expiry)
- Lock: first client refreshes; others wait
- Stale-while-revalidate: serve stale; refresh async

### Thundering Herd
Cache cluster restart; cold; everyone misses.

Mitigation: warmup; gradual rollout.

### Cache Penetration
Many requests for non-existent keys → DB hit every time.

Mitigation: cache negative result (with shorter TTL).

## Sizing

```
Memory = (avg item size) × (cached items) × overhead (~20%)
```

E.g., 1 KB user × 1M users × 1.2 = 1.2 GB.

Pick instance with enough RAM. Headroom for spikes.

## Replication

Primary + replicas:
- Reads from replicas
- Failover to replica on primary failure

Multi-AZ: replicas in different AZs.

## Cost

ElastiCache instance: $0.05-$5/hour depending size. 
For 100 GB Redis: ~$1000/mo.

For ephemeral cache: cheap. For DB: expensive.

## When NOT Cache

- Already fast enough
- Data changes every read
- Strong consistency required (caches add staleness)
- Small dataset (fits in DB memory anyway)

## Redis in K8s

Run yourself or use operator (Redis Enterprise, Bitnami Redis).
Or use cloud (ElastiCache, Memorystore).

For prod scale: cloud managed easier.

## Monitoring

- CPU
- Memory used / max
- Connections (hit limit?)
- Hit ratio (low = cache not useful)
- Evictions (rising = memory pressure)
- Replication lag

Alert on:
- Memory >85%
- Hit ratio <60%
- Evictions surging

## Multi-tier

L1 (in-process): map / LRU cache
L2 (Redis): shared cluster
L3 (DB): source of truth

Each tier hits less; faster.

## Distributed Lock with Redis

`SET key val NX EX 30`:
- NX: only if not exists
- EX 30: expires in 30s

```python
got = redis.set(f"lock:{job}", node_id, nx=True, ex=30)
if got:
    # I have the lock
```

Watch for: clock drift, network partitions. For correctness: use proper consensus (etcd, ZooKeeper).

## Cluster Topology

When app says `redis.example.com`: usually DNS to primary.
On failover: DNS updates; brief downtime.

ElastiCache: reader and writer endpoints.

## Common Mistakes

- No TTL (memory fills)
- Cache-aside without negative caching
- Hot key (one key serving all reads)
- No monitoring (silent failures)
- Cluster without hash tags (multi-key ops fail)

## Best Practices

- Always set a TTL and an eviction policy (`allkeys-lru` for a pure cache) so memory can't fill and cause write failures.
- Pick the Redis data type that fits the job (Hash for sessions, Sorted Set for leaderboards, counter+EXPIRE for rate limits) instead of stuffing JSON strings.
- Mitigate stampedes with locks, stale-while-revalidate, or probabilistic early refresh; cache negative results (short TTL) to stop penetration.
- Run replicas across AZs with automatic failover, and use the reader/writer endpoints rather than hardcoding a node.
- Choose persistence by purpose: none for a pure cache, AOF/MemoryDB when the data is authoritative.
- Layer caches (in-process L1 → Redis L2 → DB) and monitor hit ratio, evictions, and memory; alert when hit ratio drops or evictions surge.

## Quick Refs

Cache write patterns:

| Pattern | Behavior | Trade-off |
|---|---|---|
| Cache-aside (lazy) | App reads cache, falls back to DB, populates | First read slow; misses hit DB |
| Write-through | Write DB + cache together | Always fresh; slower writes |
| Write-behind | Write cache, async flush to DB | Fast; risk on cache loss |
| Refresh-ahead | Refresh before expiry | Fewer misses; extra work |

Sizing: `memory ≈ avg item × items × ~1.2` (e.g. 1 KB × 1M × 1.2 ≈ 1.2 GB).

Distributed lock (best-effort): `SET lock:job node NX EX 30` — use etcd/ZooKeeper when correctness is required.

Don't cache when: data changes every read, strong consistency is required, or the dataset already fits in DB memory.

## Interview Prep

**Junior**: "Why use a cache?"

**Mid**: "Cache stampede — mitigate."

**Senior**: "Cache invalidation strategy."

**Staff**: "Redis cluster design at 10 TB scale."

## Next Topic

→ [T04 — Data Warehouses](T04-Data-Warehouses.md)
