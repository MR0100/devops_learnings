# L23/C02/T05 — Redis Modules (Bloom, JSON, Search)

## Learning Objectives

- Use Redis modules
- Choose when

## Modules

Extend Redis:
- RedisJSON
- RedisSearch
- RedisBloom
- RedisGraph (deprecated)
- RedisTimeSeries
- RedisAI

## Install

```bash
# Redis Stack (all modules bundled)
docker run -p 6379:6379 redis/redis-stack
```

Or load individually.

## RedisJSON

Document storage:
```
JSON.SET user:1 . '{"name":"alice","age":30,"tags":["a","b"]}'
JSON.GET user:1 .name
JSON.SET user:1 .age 31
JSON.ARRAPPEND user:1 .tags '"c"'
```

For: nested JSON; partial updates.

## RedisSearch

Full-text search + secondary indexes:
```
FT.CREATE idx ON HASH PREFIX 1 user: SCHEMA name TEXT email TEXT age NUMERIC

FT.SEARCH idx "alice"
FT.SEARCH idx "@age:[25 35]"
```

For: search; aggregations.

## RedisBloom

Probabilistic:
```
BF.ADD seen item1
BF.EXISTS seen item1   # true
BF.EXISTS seen unknown  # false

# Bloom variants
CF.ADD / CMS.INCRBY / TOPK
```

For: cache penetration, dedup.

## RedisTimeSeries

Time-series:
```
TS.CREATE sensor:1
TS.ADD sensor:1 * 25.5
TS.RANGE sensor:1 - +
```

For: metrics-like.

## Use Cases

### RedisJSON
- User profiles
- Configurations
- Document store

### RedisSearch
- Product search
- Autocomplete
- Tag queries

### RedisBloom
- Cache penetration filter
- Username availability
- Spam detection

### RedisTimeSeries
- App metrics
- Sensor data
- Trading

## Vs Specialized

| | Redis Module | Specialized |
|---|---|---|
| RedisJSON vs MongoDB | simpler | richer |
| RedisSearch vs Elastic | smaller | full-text richer |
| Bloom vs library | networked | local |
| TimeSeries vs Prometheus | KV-like | true TS |

For: Redis if already using; specialized if scale demands.

## Performance

Native Redis speed:
- < 1 ms latency
- High QPS

## Cost

- Open source
- Enterprise (paid features)

## Best Practices

- Use modules sparingly
- Memory plan
- Persistence configured
- Cluster-aware

## Common Mistakes

- Modules + cluster (some not compatible)
- Memory underestimate (JSON)
- No persistence (lose docs)

## Quick Refs

```
JSON: JSON.SET / GET / DEL / ARRAPPEND
Search: FT.CREATE / FT.SEARCH
Bloom: BF.ADD / BF.EXISTS
TS: TS.CREATE / TS.ADD / TS.RANGE
```

## Interview Prep

**Mid**: "Redis modules."

**Senior**: "RedisJSON vs Mongo."

**Staff**: "Redis as data platform."

## Next Topic

→ Move to [L23/C03 — Memcached](../C03/README.md)
