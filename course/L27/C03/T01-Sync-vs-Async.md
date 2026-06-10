# L27/C03/T01 — Synchronous vs Asynchronous Replication

## Learning Objectives

- Choose replication type
- Trade-offs

## Sync

Primary waits for replicas:
- Write acknowledged after replica ack
- No data loss
- Slower writes

## Async

Primary doesn't wait:
- Acknowledged immediately
- Replica catches up
- Risk: lag = data loss on failure

## Trade-Off

| | Sync | Async |
|---|---|---|
| RPO | 0 | seconds-minutes |
| Latency (writes) | high | low |
| Throughput | lower | higher |
| Use | critical | general |

## Sync Examples

- Postgres synchronous_commit + standby
- MySQL Group Replication
- Spanner (Paxos)

## Async Examples

- Postgres streaming async
- MySQL async
- DynamoDB Global Tables
- Aurora Global

## Hybrid

Sync to nearby; async to far:
- Sync standby (same region)
- Async (other region)

For: balance.

## Across Regions

Sync cross-region:
- 50-200 ms RTT
- Writes very slow
- Rare

Async cross-region:
- Common
- RPO seconds-minutes

## Quorum

Some replicas:
- N replicas
- W writes ack required
- Read W others

For: tunable.

Cassandra: tunable consistency.

## Network Failures

Sync:
- Lose replicas: writes block
- Choose CP (consistency)

Async:
- Lose replicas: writes continue
- Choose AP (availability)

## Postgres

```ini
synchronous_commit = on
synchronous_standby_names = 'standby1'
```

For sync.

## MySQL

```sql
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
```

Semi-sync: wait for one replica.

## Mongo

Write concern:
```js
db.collection.insertOne({}, {writeConcern: {w: 'majority'}})
```

For: replication ack.

## Replication Lag

Monitor:
```promql
postgres_replication_lag_seconds
mysql_slave_lag
```

Alert on high lag.

## Failover

Sync replica: promote safely.
Async: may lose recent writes.

For: choose carefully.

## Best Practices

- Sync within DC (cheap)
- Async cross-region
- Monitor lag
- Test failover

## Common Mistakes

- Async without lag awareness (lose data)
- Sync cross-region (slow)
- No monitor

## Quick Refs

```
Sync:  RPO=0; slower
Async: RPO=lag; faster

Hybrid: sync local + async remote
Quorum: tunable
```

## Interview Prep

**Mid**: "Sync vs async."

**Senior**: "Pick replication."

**Staff**: "Replication architecture."

## Next Topic

→ [T02 — Cross-Region Replication](T02-Cross-Region-Repl.md)
