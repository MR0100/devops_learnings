# L28/C04/T10 — Design a Key-Value / Cache Store

## Learning Objectives

- Design a distributed key-value / cache store (Redis/DynamoDB-class)
- Derive node count from working-set size and QPS
- Reason about consistency, eviction, and the failure modes of caching

## Requirements

### Functional
- `GET(key)`, `SET(key, value, ttl?)`, `DELETE(key)`
- TTL-based expiry; LRU/LFU eviction when full
- Horizontal scale by adding nodes
- Optional persistence (cache vs system-of-record mode)

### Non-Functional
- p99 read < 1 ms (in-memory)
- ~1M ops/s, read-heavy (say 90:10 read:write)
- Highly available; tolerate single-node loss
- Tunable durability: pure cache (lossy OK) vs KV store (durable)

State the mode up front: a **cache** can lose data (rebuild from source of truth); a **KV store** cannot. This single choice drives replication and persistence decisions.

## Estimation (back-of-envelope, derived)

Working set, not total data, sets memory:
```
items           = 1B keys
avg_value       = 1 KB
key+overhead    ≈ 100 B
raw_data        = 1B × (1KB + 100B) ≈ 1.1 TB
```
Memory per node is the constraint — pick a node size and divide:
```
usable_per_node ≈ 64 GB (leave headroom for fragmentation/replication)
data_nodes      = 1.1 TB / 64 GB ≈ 18 → ~20 primary shards
```
Now check QPS independently (memory and throughput are separate limits):
```
per_node_qps    ≈ 100k ops/s
qps_nodes       = 1M / 100k = 10
```
Memory needs ~20 shards, QPS needs ~10 — **memory dominates here**, so 20 shards. With replication factor 2 (one replica each): ~40 nodes total. Deriving both and taking the max is the point.

## High-Level Design

```
Client (smart SDK: hashes key → shard)
   │  consistent-hash ring
   ▼
[Shard 1: primary + replica]  [Shard 2 ...]  ... [Shard 20 ...]
   │ writes → primary, async/sync → replica
   │ reads  → primary (strong) or replica (cheap, maybe stale)
   ▼
(optional) AOF / snapshot to disk for durability
   ▼
Source of truth (DB) — for cache-aside refill on miss
```

- **Consistent hashing** maps keys to shards so adding/removing a node remaps only ~1/N of keys (not everything). Use **virtual nodes** to smooth distribution.
- Each shard = **primary + replica(s)** for availability and read scaling.
- Client-side smart routing avoids a proxy hop; a proxy (e.g. Envoy/twemproxy) is the alternative when you want dumb clients.

## Deep Dive: Caching Patterns

```
cache-aside (lazy):  app reads cache; miss → read DB → populate cache
write-through:       write to cache and DB together (read-fresh, slower write)
write-back:          write cache now, flush to DB async (fast, risk loss on crash)
read-through:        cache library owns the DB read on miss
```
**Cache-aside** is the default for read-heavy workloads. The two famous hazards:
- **Thundering herd / cache stampede**: a hot key expires and thousands of requests hit the DB at once. Mitigate with a per-key lock (one rebuilder), `SET NX` lease, or probabilistic early refresh.
- **Cache penetration**: requests for keys that don't exist bypass the cache every time. Mitigate by caching negative results (short TTL) or a Bloom filter front.

Invalidation: prefer **TTL + explicit delete on write** over trying to keep cache and DB perfectly in sync — "there are only two hard things…".

## Deep Dive: Consistency & Replication

- **Async replication** (Redis default): fast writes, but a primary crash can lose the un-replicated tail → acceptable for a cache, risky for a KV store.
- **Sync / quorum** (Dynamo-style `W + R > N`): tunable. `W=2, R=2, N=3` gives read-your-writes without full sync cost.
- **Leaderless + conflict resolution**: Dynamo uses vector clocks / last-write-wins; the app may see siblings. This is the AP corner of CAP (see C02/T04) — available under partition, eventually consistent.

For a strict KV store choose quorum and persistence; for a cache, async + best-effort is usually right. Make this an explicit decision, not a default.

## Deep Dive: Eviction

When memory fills, the policy decides what dies:
- **LRU** — evict least-recently-used; good general default.
- **LFU** — evict least-frequently-used; better when popularity is stable.
- **TTL/volatile-lru** — only evict keys with a TTL.
Real implementations (Redis) use **approximate LRU/LFU** (sample K keys, evict the worst) because exact LRU needs O(1) bookkeeping that costs memory.

## Bottlenecks & Failure Modes

- **Hot key** (celebrity key): one shard saturates. Mitigate with client-side L1 cache, key replication across shards with a random read suffix, or a dedicated tier. (See C02/T04 / the hot-key playbook.)
- **Resharding storm**: naive `hash % N` remaps almost all keys when N changes → use consistent hashing + virtual nodes so only ~1/N move.
- **Cold cache after restart**: hit rate craters, DB gets hammered → warm from a snapshot or shadow-replay before taking traffic.
- **Replication lag**: replica reads return stale data → route consistency-sensitive reads to the primary.
- **Memory fragmentation**: usable RAM < physical RAM → leave 20–30% headroom (already in the estimation).
- **Big keys / big values**: one huge key blocks the event loop and skews a shard → cap value size, split large structures.

## Trade-Offs

- **Cache vs KV store**: lossy + fast vs durable + costlier (replication + persistence).
- **Strong vs eventual consistency**: primary reads + sync replication vs replica reads + async (CAP, C02/T04).
- **Client-side routing vs proxy**: no extra hop but fat clients, vs simple clients but a proxy tier to run.
- **Memory cost vs hit rate**: bigger cache → higher hit rate with diminishing returns; size to the working set (80/20), not the whole dataset.

## Real Examples

- **Redis Cluster**: 16,384 hash slots across shards, primary+replica, async replication, approximate LRU/LFU.
- **Memcached**: pure cache, client-side consistent hashing, no persistence.
- **DynamoDB**: leaderless, consistent-hash partitioning, tunable consistency, durable.
- **Amazon Dynamo (paper)**: the canonical AP design — vector clocks, sloppy quorum, hinted handoff.

## Best Practices

- Size to the working set (hot 20%), not the full dataset
- Consistent hashing + virtual nodes for smooth rebalancing
- Cache-aside + TTL + delete-on-write for invalidation
- Guard hot keys (L1) and stampedes (lease/lock); cache negatives for penetration
- Decide cache-vs-store up front; it drives persistence & replication

## Common Mistakes

- `hash % N` routing (full remap on scale events)
- No stampede protection (one expiry floods the DB)
- Treating an async-replicated cache as durable
- Caching the whole dataset (wasteful) instead of the working set
- Replica reads where read-your-writes is required

## Quick Refs

```
nodes = max(data/usable_per_node, qps/per_node_qps)
working set = hot 20% (not total)

Patterns: cache-aside (default) / write-through / write-back
Hazards: stampede (lease/lock), penetration (negative cache/Bloom)
Routing: consistent hash + vnodes
Eviction: (approx) LRU / LFU / TTL
Consistency: async (cache) vs quorum W+R>N (store)
```

## Interview Prep

**Mid**: "How do you populate and invalidate the cache?" — Cache-aside: on a miss the app reads the DB and writes the value back with a TTL; on a write it updates the DB and deletes the key so the next read refills. TTL bounds staleness and delete-on-write keeps it from drifting — I avoid trying to keep cache and DB perfectly in lockstep.

**Senior**: "A hot key just expired and the database fell over — what happened and how do you fix it?" — A cache stampede: thousands of concurrent misses for the same key all hit the DB at once. Fix it with a per-key rebuild lease (`SET NX`) so exactly one request refills while the rest wait or serve stale, plus probabilistic early refresh so the key is renewed before it expires. For a genuinely celebrity key, add a client-side L1 cache and replicate the key across shards.

**Staff**: "You need to add capacity to a live cache cluster without nuking your hit rate." — Don't use `hash % N` — adding a node would remap almost every key and cold-start the cluster. Consistent hashing with virtual nodes moves only ~1/N of keys; I'd add shards gradually, warm new nodes from snapshots or shadow traffic before they take reads, and watch hit rate and DB load as the leading indicators. The whole move is a controlled rebalance, not a flush.

**Principal**: "Design the storage as a durable KV store, not just a cache — what changes?" — The cache-vs-store decision flips every default: async replication becomes quorum (`W+R>N`, e.g. 2/2/3) for read-your-writes, I add persistence (AOF/snapshot or a log-structured store) so an acked write survives a node loss, and I handle conflict resolution (vector clocks or LWW) since leaderless writes can produce siblings. That puts me in the AP/tunable corner of CAP — available and eventually consistent — with durability and bounded staleness as explicit, costed choices rather than best-effort.

## Next Topic

→ Move to [L28/C05 — Platform Engineering](../C05/README.md)
