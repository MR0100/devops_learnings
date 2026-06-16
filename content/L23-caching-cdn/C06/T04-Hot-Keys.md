# L23/C06/T04 — Hot Keys

## Learning Objectives

- Recognize when a single key dominates cache traffic and why it breaks sharding
- Detect hot keys in Redis/Memcached before they cause an outage
- Apply mitigations: client-side caching, key replication, read replicas, dedicated tiers

## What Is a Hot Key

Sharded caches assume traffic spreads evenly across keys (and therefore shards). A **hot key** violates that assumption: one key receives a disproportionate share of all requests.

```
99% of GET traffic → /api/featured-product (one popular item)
                     ↓ hashes to a single shard
Shard owning that key: 100% CPU / NIC saturated
Other shards:          idle
```

Sharding does not help, because every request for the hot key lands on the **same** node. You can add 100 shards and the hot key is still served by one of them. This is a load-distribution problem, not a capacity problem.

### Common Sources

- A viral product, post, or tweet ("celebrity problem")
- A global config / feature-flag blob fetched on every request
- A single tenant in a multi-tenant system generating most load
- A counter or leaderboard everyone reads

## Symptoms

- One Redis shard pinned at 100% CPU or network while peers sit idle
- p99 latency spikes for that key (and queueing affects co-located keys)
- `INFO commandstats` shows one node dominating
- Network egress on one instance hits the NIC ceiling (large values amplify this)

## Detection

```bash
# Redis 4.0+ — samples keys, needs an LFU/LRU maxmemory-policy
redis-cli --hotkeys

# Sample live traffic for hot keys / large values
redis-cli --bigkeys

# Watch live command stream (sample briefly; MONITOR is expensive)
redis-cli MONITOR | head -n 1000

# Per-node command + network stats
redis-cli INFO commandstats
redis-cli INFO stats | grep instantaneous
```

In a proxy/mesh (Envoy, Twemproxy), emit per-key request counts and alert when one key exceeds N% of total traffic.

## Mitigations

### 1. Client-Side (Near) Caching

Keep the hot item in an in-process L1 cache (sub-microsecond access). The hottest reads never reach Redis at all.

```python
# L1 in-process cache with a short TTL bounds staleness
local = TTLCache(maxsize=1000, ttl=5)

def get(key):
    if (v := local.get(key)) is not None:
        return v
    v = redis.get(key)
    local[key] = v
    return v
```

Redis 6+ supports **client-side caching with invalidation** (`CLIENT TRACKING`) so the server pushes invalidations instead of relying on TTL alone.

### 2. Key Replication (Sharding the Key)

Write the same value under N suffixed keys; readers pick one at random. The load spreads across N keys — and potentially N shards.

```python
N = 10

def set_hot(key, val, ttl=300):
    for i in range(N):
        redis.set(f"{key}:{i}", val, ex=ttl)

def get_hot(key):
    i = random.randrange(N)        # spread reads across replicas
    return redis.get(f"{key}:{i}")
```

Trade-off: N× write amplification and N× memory for that key, plus a small consistency window across replicas. Worth it for read-dominant hot keys.

### 3. Read Replicas

Route reads for the hot key to Redis replicas (`READONLY` clients, or a replica-aware client). Spreads read load across the replica set while writes still go to the primary.

### 4. Dedicated Tier

Move the hot key to its own isolated cache instance so its traffic can't starve unrelated keys. Common for global config blobs.

### 5. Shrink the Value

A hot key with a 1 MB value saturates the NIC far faster than a 1 KB one. Cache only the fields actually read; compress; split large blobs.

## Common Mistakes

- Adding shards to fix a hot key (does nothing — same key, same node)
- No detection in place; the first signal is an outage
- Replicating the key but reading from a fixed suffix (defeats the spread)
- Ignoring write amplification when replicating a write-heavy key
- Caching a huge value and saturating the network instead of CPU

## Best Practices

- Run `--hotkeys` periodically and alert on per-key traffic skew
- Default hot, read-mostly items (featured product, global config) to an L1 cache
- Bound L1 staleness with a short TTL or server-push invalidation
- Pre-identify likely hot keys (launches, promos) and pre-warm + replicate ahead of traffic
- Keep 30% network headroom on cache nodes; watch NIC, not just CPU

## Quick Refs

```bash
redis-cli --hotkeys            # detect hot keys (needs LFU/LRU policy)
redis-cli --bigkeys           # detect large values
redis-cli INFO commandstats   # per-node command distribution
CLIENT TRACKING ON            # Redis 6+ client-side cache invalidation
```

```python
# Spread reads across N replica keys
redis.get(f"{key}:{random.randrange(N)}")
```

## Interview Prep

**Junior**: "What is a hot key?" — One key takes a disproportionate share of cache traffic, overloading the single shard that owns it.

**Mid**: "Why doesn't adding shards help?" — The key always hashes to the same node; more shards don't move the hot key off that node.

**Senior**: "How do you mitigate a hot key?" — L1/client-side caching for read-mostly items, key replication with random read suffix to spread across shards, read replicas, or a dedicated tier; shrink the value to ease network pressure.

**Staff**: "Design a system resilient to celebrity hot keys." — Multi-tier (L1 in-process + L2 Redis), automatic hot-key detection feeding dynamic replication, replica read routing, value-size limits, and pre-warm playbooks for known launch events; treat it as a load-distribution problem with feedback, not a capacity add.

## Next Topic

→ Move to [L24 — Production Networking](../../L24-production-networking/README.md)
