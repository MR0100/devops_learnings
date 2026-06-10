# L21/C04/T04 — Redis (Sentinel, Cluster)

## Learning Objectives

- Operate Redis
- Choose Sentinel or Cluster

## Redis

In-memory KV:
- Microsecond latency
- Lists, sets, hashes, streams
- Pub/sub
- Lua scripts

## Persistence

### RDB
Snapshot to disk:
- Periodic
- Compact

```
save 900 1
save 300 10
save 60 10000
```

### AOF
Append-only log:
- Every write
- Replay on restart

```
appendonly yes
appendfsync everysec
```

## Modes

### Standalone
Single instance. SPOF.

### Sentinel
Master + replicas + sentinels:
- Auto-failover
- Single key namespace
- Up to ~10k ops/sec

### Cluster
Sharded:
- 16384 slots
- 3+ masters + replicas
- Scale horizontally

## Sentinel Setup

```
# sentinel.conf
sentinel monitor mymaster 192.168.1.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
```

3+ sentinels typical.

## Cluster Setup

```bash
redis-cli --cluster create \
  m1:6379 m2:6379 m3:6379 \
  s1:6379 s2:6379 s3:6379 \
  --cluster-replicas 1
```

3 masters + 3 replicas.

## Cluster Slots

Keys hashed → slot.
Slot → master.

```
SET key value
```

Routed automatically (with cluster-aware client).

## Hash Tags

```
{user:1}:profile
{user:1}:settings
```

Same slot. For: multi-key ops (transactions).

## Eviction

When memory full:
```
maxmemory 8gb
maxmemory-policy allkeys-lru
```

Policies:
- noeviction (error)
- allkeys-lru
- volatile-lru
- allkeys-random
- volatile-ttl

For cache: allkeys-lru.
For state: noeviction.

## TTL

```
EXPIRE key 3600
SET key val EX 3600
```

For: cache.

## Pub/Sub

```
SUBSCRIBE channel
PUBLISH channel message
```

Realtime msgs.

## Streams

```
XADD stream * key value
XREAD GROUP groupname consumer COUNT 10 STREAMS stream >
```

Kafka-lite.

## Lua

```
EVAL "return redis.call('GET', KEYS[1])" 1 mykey
```

Atomic multi-op.

## Performance

- 100k+ ops/sec single instance
- < 1 ms latency
- Memory-bound

## ElastiCache / MemoryDB

AWS managed:
- ElastiCache: cache (transient)
- MemoryDB: durable (multi-AZ)

For: managed.

## Best Practices

- Sentinel for HA single shard
- Cluster for scale-out
- Persistence enabled
- Eviction policy set
- Monitor memory

## Common Mistakes

- noeviction + cache (OOM)
- No persistence (lose state)
- Hash tag missed (cross-slot fail)
- Single instance prod

## Quick Refs

```
redis-cli
CLUSTER INFO
CLUSTER NODES
INFO replication
INFO memory

EXPIRE / TTL
EVAL Lua
XADD / XREAD streams
```

## Interview Prep

**Mid**: "Redis modes."

**Senior**: "Cluster vs Sentinel."

**Staff**: "Redis at scale."

## Next Topic

→ Move to [L21/C05 — Database Migrations](../C05/README.md)
