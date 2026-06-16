# L23/C02/T02 — Redis Persistence (RDB, AOF)

## Learning Objectives

- Configure persistence
- Trade-offs

## RDB

Snapshot at intervals:
```
save 900 1      # save if 1 change in 900 sec
save 300 10
save 60 10000
```

Background fork; child writes; parent serves.

For: backup-style; fast restart.

## AOF

Append-only log:
- Every write logged
- Replay on restart

```
appendonly yes
appendfsync everysec   # vs always vs no
```

For: durability.

## fsync Options

### always
Every write. Slow but safe.

### everysec
Once per second. Default. Lose at most 1 sec.

### no
OS decides. Fastest; least safe.

## AOF Rewrite

Compacts log:
- Background
- Equivalent commands to current state

```
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

## RDB + AOF

Both:
- RDB for fast restore
- AOF for durability

On restart: AOF if exists (more recent).

For: prod recommended.

## Performance

- AOF always: slow
- AOF everysec: minimal impact
- AOF no: fast
- RDB: minimal impact (fork)

## Sizing

AOF: typically larger than RDB.

Both: significant disk for large.

## Backup

RDB snapshot:
```bash
cp /var/lib/redis/dump.rdb /backup/
```

Or:
```bash
redis-cli BGSAVE
```

For: regular backup.

## Cloud Native

- ElastiCache: automatic snapshots
- MemoryDB: continuous log (durable)
- Cloud-native handles persistence

## Trade-Off

| | RDB | AOF |
|---|---|---|
| Restart speed | fast | slower |
| Data loss | up to last save | up to last fsync |
| Disk size | smaller | larger |
| Performance | minimal | varies |

## Modes

### Cache Mode
RDB only or no persist:
- Lose data on restart OK
- Just refill from origin

### State Mode
AOF + RDB:
- Can't lose state
- Sessions, queues

## Best Practices

- AOF + RDB for state
- RDB for cache
- everysec fsync
- Backup RDB
- Test restore

## Common Mistakes

- No persist (lose on restart)
- always fsync (slow)
- AOF without rewrite (huge file)
- No backup test

## Quick Refs

```ini
save 900 1
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100

# Disable persistence (cache)
save ""
appendonly no
```

```bash
redis-cli BGSAVE / BGREWRITEAOF
redis-cli LASTSAVE
```

## Interview Prep

**Mid**: "Redis persistence."

**Senior**: "RDB vs AOF."

**Staff**: "State Redis design."

## Next Topic

→ [T03 — Replication, Sentinel, Cluster](T03-Replication-Sentinel-Cluster.md)
