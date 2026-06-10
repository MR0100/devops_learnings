# L21/C06/T03 — Cross-Region Replication

## Learning Objectives

- Replicate cross-region
- Plan DR

## Why

- DR
- Read locality
- Compliance

## Patterns

### Active-Passive
Primary in region A; standby in B.

Failover during disaster.

### Active-Active
Both regions writable.

Conflict resolution needed.

### Read Replicas
Primary writes one region; reads in others.

## Postgres

Async streaming replica:
```bash
pg_basebackup -h primary-us-east -D /data -U repl

# In primary postgresql.conf
wal_level = replica
max_wal_senders = 10
```

Cross-region lag: depends on bandwidth, distance.

## MySQL

Async or semi-sync:
```sql
CHANGE MASTER TO MASTER_HOST='primary-us-east', ...;
```

## Logical Replication

Postgres / MySQL: subset.

For: smaller bandwidth.

## Lag

Cross-region:
- 50-200 ms RTT
- Replicate lag in ms-seconds

## Conflict Resolution

Active-active:
- Last-writer-wins
- App-level
- DB-specific (Spanner, Cosmos)

Hard.

## Cloud Native

- Aurora Global: 1-sec cross-region
- Spanner Multi-Region: built-in
- Cosmos DB: multi-region
- DynamoDB Global Tables: active-active

## Aurora Global

```bash
aws rds create-global-cluster --global-cluster-identifier global \
  --source-db-cluster-identifier primary-cluster
```

For: low RPO cross-region.

## Bandwidth

Replicate 100 GB/day:
- ~10 Mbps avg
- Spikes higher

Plan inter-region bandwidth.

## Cost

- Inter-region transfer: $0.02/GB
- For 1 TB/month: $20

Plus compute, storage.

## Failover

Promote replica:
```sql
SELECT pg_promote();
```

DNS / connection string update.

## Practice

Quarterly DR drill:
- Failover to remote region
- Verify
- Failback

For: confidence.

## App Considerations

- Connection retries
- Multiple DSNs
- Write to primary; read from local

## Sharded Cross-Region

Per-region shard:
- US data → US shard
- EU data → EU shard

For: compliance (data residency).

## Disaster Definition

- Region-level outage
- AWS region down
- Network partition

For: < 1/year typically.

## RPO Cross-Region

Async:
- RPO = lag (seconds-minutes)
- Sync impractical (latency)

For: accept RPO > 0.

## Best Practices

- Async cross-region for DR
- Multi-AZ in primary for HA
- Test failover regularly
- Monitor lag
- Use cloud-native if possible

## Common Mistakes

- Sync cross-region (slow writes)
- No failover test
- Manual process
- Single region (no DR)

## Quick Refs

```
Aurora Global: built-in
Spanner: multi-region native
DynamoDB Global Tables: active-active
Postgres / MySQL: async streaming
```

## Interview Prep

**Mid**: "Cross-region."

**Senior**: "Active-active vs passive."

**Staff**: "Multi-region DB."

## Next Topic

→ [T04 — Restoring Without Crying](T04-Restoring.md)
