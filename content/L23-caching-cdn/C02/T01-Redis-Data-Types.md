# L23/C02/T01 — Redis Data Types Deep Dive

## Learning Objectives

- Use Redis types
- Pick for use case

## Strings

Basic:
```
SET key value
GET key
INCR counter
EXPIRE key 60
```

For: cache, counters, simple state.

## Hashes

Key with fields:
```
HSET user:1 name "alice" email "a@b.com"
HGET user:1 name
HGETALL user:1
HINCRBY user:1 logins 1
```

For: object storage; per-field update.

## Lists

Ordered:
```
LPUSH queue task1
RPUSH queue task2
LPOP queue
LRANGE queue 0 -1
```

For: queues; recent items.

## Sets

Unique members:
```
SADD tags "redis" "cache"
SMEMBERS tags
SINTER tags1 tags2
```

For: unique tracking; intersect.

## Sorted Sets

Score + member:
```
ZADD leaderboard 100 "alice" 200 "bob"
ZRANGE leaderboard 0 9 REV WITHSCORES
ZINCRBY leaderboard 5 "alice"
```

For: ranking, time-series.

## Streams

Append log:
```
XADD events * type "login" user "alice"
XREAD STREAMS events 0
XLEN events
```

For: event log; consumer groups.

## Bitmaps

Bit operations on strings:
```
SETBIT logins:2026-01-01 user_id 1
BITCOUNT logins:2026-01-01
```

For: presence, dau.

## HyperLogLog

Approximate unique count:
```
PFADD users "alice" "bob" "carol"
PFCOUNT users    # approximate
```

Tiny memory (12 KB) for millions.

For: uniques.

## Geo

```
GEOADD locations 13.40 52.51 "Berlin"
GEORADIUS locations 13.40 52.51 100 km
```

For: nearest, distance.

## Pub/Sub

```
PUBLISH channel "message"
SUBSCRIBE channel
```

For: real-time notify.

## JSON (Module)

```
JSON.SET user:1 . '{"name":"alice","age":30}'
JSON.GET user:1 .name
```

For: document storage.

## Search (Module)

Full-text search:
```
FT.CREATE idx ON HASH PREFIX 1 user: SCHEMA name TEXT
FT.SEARCH idx "alice"
```

For: search w/ Redis.

## Bloom (Module)

```
BF.ADD seen item
BF.EXISTS seen item   # approximate
```

For: cache penetration prevention.

## TTL

```
EXPIRE key 60
TTL key
PERSIST key
```

## Use Case Examples

### Session Store
Hash with TTL.

### Cache
String with TTL.

### Rate Limiting
Sorted set (timestamps).

### Leaderboard
Sorted set.

### Queue
List or Stream.

### Real-time Counter
INCR.

### Unique Visitor
HyperLogLog.

### Geofencing
Geo commands.

## Atomic

All single commands atomic.

Multi-command:
```
MULTI
SET k1 v1
INCR counter
EXEC
```

Transaction.

## Lua

```
EVAL "return redis.call('GET', KEYS[1])" 1 mykey
```

Atomic multi-op.

## Memory

Per key:
- String: ~50 bytes overhead + value
- Hash: efficient < 100 fields
- Big keys: bad for ops

## Best Practices

- Right type per use
- TTL for cache keys
- HyperLogLog for uniques
- Streams for events
- Bloom for filter

## Common Mistakes

- Strings for everything
- No TTL (memory fills)
- Big keys (slow ops)
- Pub/sub for durable (not)

## Quick Refs

```
String: SET / GET / INCR
Hash: HSET / HGET
List: LPUSH / RPUSH / LPOP
Set: SADD / SMEMBERS
ZSet: ZADD / ZRANGE
Stream: XADD / XREAD
Bitmap: SETBIT
HLL: PFADD / PFCOUNT
Geo: GEOADD / GEORADIUS
Pub: PUBLISH / SUBSCRIBE
```

## Interview Prep

**Mid**: "Redis types."

**Senior**: "Pick for use case."

**Staff**: "Redis as data platform."

## Next Topic

→ [T02 — Persistence (RDB, AOF)](T02-Persistence.md)
