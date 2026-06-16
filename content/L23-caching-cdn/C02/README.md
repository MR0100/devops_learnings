# L23/C02 — Redis

## Topics

- **T01 Data Types Deep Dive** — Strings, lists, hashes, sets, sorted sets, streams, bitmaps, HyperLogLog, geospatial
- **T02 Persistence** — RDB, AOF
- **T03 Replication, Sentinel, Cluster** — HA options
- **T04 Lua Scripting** — Atomic multi-op
- **T05 Redis Modules** — Bloom, JSON, Search

## Data Types

### Strings
Most basic. Up to 512 MB.
```
SET key value
SET key value EX 60         # 60s TTL
GET key
INCR counter
DECRBY counter 5
APPEND key "more"
```

### Lists (Doubly-linked)
```
LPUSH mylist a b c          # left push (head)
RPUSH mylist x y            # right push (tail)
LRANGE mylist 0 -1          # get all
LPOP mylist
BLPOP mylist 5              # blocking pop with timeout
```

Use: queues, recent activity.

### Hashes
Object with fields.
```
HSET user:42 name "Alice" email "alice@example.com"
HGET user:42 name
HGETALL user:42
HINCRBY user:42 score 1
```

Use: user profiles, session data.

### Sets (Unordered)
```
SADD tags "kubernetes" "docker"
SMEMBERS tags
SISMEMBER tags "docker"
SINTER tags1 tags2          # intersection
SUNION tags1 tags2          # union
```

Use: tagging, unique tracking.

### Sorted Sets
Sets with scores; sorted by score.
```
ZADD leaderboard 100 "alice" 200 "bob" 150 "carol"
ZRANGE leaderboard 0 -1 WITHSCORES
ZRANGEBYSCORE leaderboard 150 +inf
ZINCRBY leaderboard 10 "alice"
```

Use: leaderboards, time series (score = timestamp), priority queue.

### Streams (5.0+)
Append-only log; Kafka-like within Redis.
```
XADD events * action "login" user "alice"
XREAD COUNT 10 STREAMS events 0
XGROUP CREATE events processing $ MKSTREAM
XREADGROUP GROUP processing consumer1 COUNT 1 STREAMS events >
```

Use: lightweight event bus; replace Kafka for small scale.

### Bitmaps
Bit operations on strings.
```
SETBIT user:42:online 1234 1     # set bit at offset 1234
BITCOUNT user:42:online
BITOP AND result key1 key2
```

Use: daily user activity (1 bit per user).

### HyperLogLog
Probabilistic cardinality count. 12 KB to count billions.
```
PFADD visitors "alice" "bob" "carol"
PFCOUNT visitors                 # approximate count
PFMERGE total visitors1 visitors2
```

Use: unique visitor counts.

### Geospatial
```
GEOADD locations -122.4 37.8 "SF"
GEORADIUS locations -122 37 100 km
```

Use: nearby search.

## Persistence

### RDB (Snapshot)
- Point-in-time snapshot
- `save 900 1` (snapshot after 900s if 1 change)
- Fast restore
- Data loss up to last snapshot

### AOF (Append-Only File)
- Logs every write
- `appendfsync everysec` (default) — at most 1s loss
- Larger files; slower restart
- Most durable

### Both
- AOF for durability + RDB for fast restart
- Recommended for production

## Replication

### Async Replication
- Primary → replicas
- Read scaling
- Default

### Replica Configuration
```
replicaof primary 6379
```

### Promotion
Manual or via Sentinel.

## Redis Sentinel

HA with auto-failover. 3+ sentinels monitor primary; elect new primary on failure.

```
sentinel monitor mymaster primary 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
```

Clients connect to sentinels for discovery.

## Redis Cluster

Sharded; 16384 hash slots distributed across primaries.

- Each shard = primary + N replicas
- Client must understand cluster topology
- Smart clients route by `CRC16(key) mod 16384`
- `MOVED` and `ASK` redirects for resharding

### Hash Tags
Force keys to same shard:
```
SET {user:42}.profile ...
SET {user:42}.orders ...
```
Both share `user:42` slot; can be operated on in a transaction.

## Lua Scripting

Atomic multi-op.
```
EVAL "return redis.call('INCR', KEYS[1])" 1 counter
```

Use for: atomic state updates that need multi-step logic.

### Rate Limiter Example
```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, 60)
end
if current > limit then
    return 0
end
return 1
```

Used as token bucket / sliding window rate limit.

## Pub/Sub

```
PUBLISH chan "hello"
SUBSCRIBE chan
PSUBSCRIBE chan.*
```

No durability; lost messages if no consumer. For durable: use Streams.

## Modules

- **RediSearch** — full-text search
- **RedisJSON** — native JSON
- **RedisBloom** — Bloom filters, Cuckoo filter
- **RedisGraph** — graph queries (sunset 2023)
- **RedisTimeSeries** — time-series operations

Loaded as `.so` plugins or with Redis Stack distribution.

## Eviction

```
maxmemory 4gb
maxmemory-policy allkeys-lru
```

Policies: noeviction, allkeys-lru, allkeys-lfu, allkeys-random, volatile-lru, volatile-lfu, volatile-ttl, volatile-random.

For cache: `allkeys-lru`. For data store (no eviction wanted): `noeviction`.

## Common Issues

- **Single-threaded blocking** — long-running scripts block all clients
- **Memory exhaustion** — eviction or rejected writes
- **Slow queries** — use SLOWLOG
- **Hot keys** — single key dominates traffic; shard or replicate
- **Bandwidth saturation** — large values + high QPS

## Operating

- Monitor: memory, ops/sec, hit rate, replication lag
- AWS ElastiCache or self-host
- Redis Enterprise (commercial) for advanced features
- 3+ Sentinels or 3+ shard Cluster

## Interview Themes

- "Redis data types"
- "Persistence modes"
- "Sentinel vs Cluster"
- "Rate limiter via Lua"
- "Hot key — diagnose and fix"
