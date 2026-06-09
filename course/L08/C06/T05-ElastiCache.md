# L08/C06/T05 — ElastiCache (Redis & Memcached)

## Learning Objectives

- Use ElastiCache
- Pick Redis or Memcached

## Engines

| | Redis | Memcached |
|---|---|---|
| Data types | many | strings |
| Replication | yes | no |
| Persistence | optional | no |
| Pub/Sub | yes | no |
| Lua scripting | yes | no |
| Cluster | yes | yes (client-side sharding) |
| Multi-AZ | yes | no |
| Backups | yes | no |
| Threads | mostly single | multi-threaded |

Redis: feature-rich; pick for most.
Memcached: simple cache; multi-threaded for raw KV at scale.

## Redis on ElastiCache

Variants:
- **ElastiCache for Redis**: standard
- **ElastiCache Serverless**: auto-scale; pay per usage
- **MemoryDB for Redis**: durable; for primary DB usage

## Cluster vs Non-Cluster

Non-cluster (legacy):
- 1 primary + replicas
- One shard
- Up to 5 replicas

Cluster mode:
- Multi-shard
- Each shard: primary + replicas
- Scales horizontally
- Slot-based hashing

For >50 GB data: cluster.

## Setup

```bash
aws elasticache create-replication-group \
  --replication-group-id mycache \
  --replication-group-description "my cache" \
  --engine redis \
  --cache-node-type cache.r6g.large \
  --num-cache-clusters 3 \
  --automatic-failover-enabled \
  --multi-az-enabled
```

## Connect

```python
import redis

r = redis.Redis(host="mycache.xxx.cache.amazonaws.com", port=6379, decode_responses=True)
r.set("key", "value")
r.get("key")
```

For cluster:
```python
from rediscluster import RedisCluster
r = RedisCluster(startup_nodes=[{"host": "...", "port": 6379}])
```

## Data Types

```python
# Strings
r.set("user:1", "alice")
r.get("user:1")

# Hashes (object-like)
r.hset("user:1", mapping={"name": "alice", "age": 30})
r.hgetall("user:1")

# Lists
r.rpush("queue", "job1")
r.lpop("queue")

# Sets
r.sadd("tags", "python", "go")
r.smembers("tags")

# Sorted sets (leaderboard)
r.zadd("scores", {"alice": 100, "bob": 85})
r.zrevrange("scores", 0, 9)    # top 10

# Streams (durable log)
r.xadd("events", {"data": "..."})
r.xread({"events": "$"}, block=0)

# HyperLogLog (cardinality)
r.pfadd("uniques", "user1")
r.pfcount("uniques")
```

Use right type:
- Session: Hash
- Recent items: List
- Unique counter: Set / HLL
- Leaderboard: Sorted Set
- Rate limit: counter with EXPIRE
- Distributed lock: SET NX EX

## Persistence

- **RDB**: snapshots; periodic
- **AOF**: append-only log; durable

For cache: usually no persistence (faster, cheaper).
For session / important: AOF.

MemoryDB: AOF mandatory; DB-grade durability.

## Failover

Primary fails → replica promotes → DNS updates (~30s).

Auto-failover enabled: critical for production.

## Encryption

- At rest: KMS
- In transit: TLS (configurable; recommended)

```bash
aws elasticache modify-replication-group --replication-group-id mycache --transit-encryption-enabled
```

## Auth

Redis AUTH command:
```bash
aws elasticache modify-replication-group --replication-group-id mycache --auth-token "..."
```

Or use IAM auth (newer):
```bash
--user-group-id mygroup
```

## Multi-AZ

Replicas across AZs. Auto-failover to replica in surviving AZ.

Cost: more nodes.

## Cluster Sharding

Cluster mode: 16384 slots; each shard owns range.

```
Shard 1: slots 0-5461
Shard 2: slots 5462-10922
Shard 3: slots 10923-16383
```

Key → CRC16 hash → slot → shard.

Multi-key ops on different shards: fail. Use hash tags `{user1}` to force same shard.

## Memory Management

```
maxmemory: amount used before eviction
maxmemory-policy: which to evict
  - noeviction: error on write when full
  - allkeys-lru: evict LRU
  - allkeys-lfu: evict LFU
  - allkeys-random
  - volatile-lru: evict LRU among keys with TTL
  - volatile-ttl: evict shortest TTL
  - ...
```

`allkeys-lru` common for cache.

Monitor BytesUsedForCache vs Max.

## Backup

Daily snapshot configurable (Redis):
```bash
aws elasticache modify-replication-group --snapshot-retention-limit 7 --snapshot-window "03:00-05:00"
```

Manual snapshot on demand.

## Memcached

Simpler:
```bash
aws elasticache create-cache-cluster --cache-cluster-id mymem --engine memcached --cache-node-type cache.m6g.large --num-cache-nodes 3
```

Client-side sharding (no server cluster awareness).

No HA: node fail = data on that node lost.

For: stateless cache; high RPS.

## Patterns

### Cache-Aside (Lazy Loading)
```python
def get_user(id):
    user = r.get(f"user:{id}")
    if user:
        return json.loads(user)
    user = db.query(...)
    r.set(f"user:{id}", json.dumps(user), ex=3600)
    return user
```

### Write-Through
```python
def save_user(user):
    db.save(user)
    r.set(f"user:{user.id}", json.dumps(user))
```

### Session Store
```python
r.hset(f"session:{token}", mapping={"user_id": "...", "expires": "..."})
r.expire(f"session:{token}", 86400)
```

### Rate Limit
```python
key = f"rate:{user_id}:{minute}"
count = r.incr(key)
if count == 1:
    r.expire(key, 60)
if count > 100:
    raise RateLimited
```

### Distributed Lock
```python
got = r.set(f"lock:{job}", node_id, nx=True, ex=30)
if got:
    # do work
    r.delete(f"lock:{job}")
```

For correctness: RedLock or proper consensus.

## Cluster Endpoints

Configuration endpoint: discovers nodes; client smart-routes.
Primary endpoint: writes.
Reader endpoint: distributes reads.

## ElastiCache Serverless

- Pay per usage (no instance hours)
- Auto-scales 0.1 GB to 5 TB
- Multi-AZ
- No node management

For: variable, dev, microservices with sporadic use.

## MemoryDB

Primary DB use case:
- Strong consistency
- Durable (Multi-AZ log)
- Microsecond reads
- Up to 100s of TB

Cost: higher than ElastiCache.

For: real-time apps where data must survive node failures (chat, leaderboards).

## Monitoring

- CPUUtilization
- DatabaseMemoryUsagePercentage
- CurrConnections
- CacheHits / CacheMisses
- Evictions
- ReplicationLag

Hit ratio < 60%: cache not useful.
Evictions surging: memory pressure.

## Failure Modes

### Cache Stampede
TTL expires; many clients fetch from DB at once.

Mitigations:
- Probabilistic early refresh
- Lock first client; others wait
- Stale-while-revalidate

### Cache Penetration
Many requests for non-existent → DB hit every time.

Mitigation: cache negative result (shorter TTL).

### Hot Key
One key serves disproportionate reads.

Mitigation: replicate (multi-key), use replicas, app-level cache.

## Cost

cache.r6g.large: ~$140/mo per node.
3-node cluster: ~$420/mo.

For Redis-as-DB (MemoryDB): more.

## Common Mistakes

- No TTL (memory fills)
- Cache-aside without negative caching
- Single node (SPOF)
- No monitoring
- Hot key
- Cluster mode multi-key ops without hash tags

## Best Practices

- Always TTL (unless durable)
- Multi-AZ for HA
- Multi-shard cluster for >50 GB
- Connection pool
- Monitor hit ratio
- Encrypt
- VPC private subnets

## Local Dev

```bash
docker run -p 6379:6379 redis:7
```

App configures host = localhost.

## Quick Refs

```bash
# Create
aws elasticache create-replication-group --replication-group-id mycache --engine redis --cache-node-type cache.r6g.large --num-cache-clusters 3 --automatic-failover-enabled

# Modify
aws elasticache modify-replication-group --replication-group-id mycache --cache-node-type cache.r6g.xlarge --apply-immediately
```

## Interview Prep

**Junior**: "When use cache?"

**Mid**: "Redis vs Memcached."

**Senior**: "Cache stampede mitigation."

**Staff**: "Cache architecture for 10 TB hot data."

## Next Topic

→ [T06 — Redshift, Athena, Glue](T06-Redshift-Athena-Glue.md)
