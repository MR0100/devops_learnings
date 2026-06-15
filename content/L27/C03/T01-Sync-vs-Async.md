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

- Postgres synchronous_commit + standby (truly synchronous)
- Spanner (Paxos — synchronous quorum commit)
- MySQL Group Replication — **virtually / certification-based** synchronous, not
  truly synchronous: the transaction is certified (conflict-checked) on a
  majority before commit, but each member *applies* the writeset
  asynchronously, so a freshly-committed write may not yet be readable on every
  member. Treat its RPO as ~0 on the certified set, but don't assume a true
  synchronous "all replicas have applied" guarantee.

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

**Junior**: "Synchronous vs asynchronous replication?" — Synchronous: the primary waits for replicas to acknowledge before confirming the write, so RPO is 0 but writes are slower. Asynchronous: the primary acknowledges immediately and replicas catch up, so writes are fast but a failure can lose the un-replicated lag (RPO = lag).

**Mid**: "Why isn't synchronous replication used across regions?" — Synchronous commit waits for a remote ack on every write, so cross-region RTT (50–200 ms) is added to every write's latency. That's usually unacceptable, so the common pattern is synchronous within a region and asynchronous across regions.

**Senior**: "MySQL Group Replication — is it truly synchronous?" — No, it's *virtually*/certification-based synchronous: a transaction is conflict-certified on a majority before commit (so RPO is ~0 on the certified set), but each member applies the writeset asynchronously, so a just-committed write may not yet be readable on every member. Don't assume an 'all replicas have applied' guarantee.

**Staff**: "Design replication for a multi-region system with tight RPO." — Use synchronous (or quorum) replication within the primary region for RPO 0 on local failover, asynchronous cross-region for DR, and monitor replication lag as your real cross-region RPO with alerting. For writes that must survive a full-region loss with zero data loss, you need a globally-synchronous store (Spanner/quorum) and must accept the write-latency cost — otherwise be explicit that cross-region RPO equals the async lag, and design the app to tolerate the small recent-write loss on regional failover.

## Next Topic

→ [T02 — Cross-Region Replication](T02-Cross-Region-Repl.md)
