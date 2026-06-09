# L23/C03 — Memcached

## Topics

- **T01 Simplicity vs Redis** — Trade-offs

## Memcached

Pure cache. Created 2003 (Brad Fitzpatrick, LiveJournal).

### Properties
- Multi-threaded (uses all cores)
- Slab allocator (reduces fragmentation)
- No persistence
- No replication
- No data types beyond K=V
- ASCII or binary protocol
- Maximum simplicity

## When Memcached over Redis

| Need | Memcached | Redis |
|---|---|---|
| Pure cache | ✅ | ✅ |
| Multi-threaded | ✅ | (multi-threaded I/O in 6.0+) |
| Simple key-value | ✅ | ✅ |
| Data structures | ❌ | ✅ |
| Persistence | ❌ | ✅ |
| Pub/Sub | ❌ | ✅ |
| Lua scripting | ❌ | ✅ |
| Replication | ❌ | ✅ |
| Memory efficiency | ✅ (slab) | Tunable |

Memcached's pitch: if you ONLY need a cache, it's simpler and uses CPU better.

Modern reality: Redis can do all Memcached's tricks plus more. Most teams default to Redis. Memcached remains for specific high-throughput use cases (Facebook scale).

## Architecture

```
Client → choose server (hash of key) → server
                                       │
                                       └── independent of others
                                       (no coordination)
```

Each server is independent. Client library does sharding (consistent hashing typically).

```python
import memcache
mc = memcache.Client(["host1:11211", "host2:11211", "host3:11211"])
mc.set("key", "value", time=60)
val = mc.get("key")
```

### Consistent Hashing
Add/remove server → only fraction of keys remapped.

## Multi-Threading

Memcached uses all CPU cores natively. Redis (until 6.0) was strictly single-threaded; 6.0+ added I/O threads but core ops still single-threaded.

For very high QPS on a single instance: Memcached can outperform Redis on multi-core.

## AWS ElastiCache for Memcached

Managed Memcached:
- Cluster of up to 40 nodes (each independent)
- Auto-discovery (clients learn cluster topology)
- No replication or failover (lose a node = lose its data)

## When Memcached Today

- Massive scale (Facebook, etc.) where every CPU cycle counts
- Pure cache use case; don't need anything Redis has extra
- Stateless cache where node loss is OK

For 99% of teams: Redis.

## Interview Themes

- "Memcached vs Redis — when each?"
- "Memcached architecture"
- "Why is single-threaded vs multi-threaded relevant?"
- "Consistent hashing in clients"
