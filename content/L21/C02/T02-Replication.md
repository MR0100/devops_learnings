# L21/C02/T02 — Postgres Replication

## Learning Objectives

- Set up replication
- Understand modes

## Streaming Replication

Physical:
- Primary → standby
- WAL streamed
- Standby = identical

For: HA, read scaling.

## Setup

Primary:
```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB

# pg_hba.conf
host replication replicator standby_ip/32 md5
```

```sql
CREATE ROLE replicator REPLICATION LOGIN PASSWORD '...';
```

Standby:
```bash
pg_basebackup -h primary -D /var/lib/postgresql/data -U replicator -P -R
```

`-R`: create standby.signal.

## Modes

### Async (default)
Primary doesn't wait.
- Fast
- Data loss possible

### Sync
Wait for standby confirmation.
- Slower
- No loss

```ini
synchronous_commit = on
synchronous_standby_names = 'standby1'
```

## Quorum Sync

```ini
synchronous_standby_names = '2 (s1, s2, s3)'
```

Wait for 2 of 3.

## Monitor Lag

```sql
SELECT pid, application_name, state, sync_state, replay_lag
FROM pg_stat_replication;
```

`replay_lag`: how far behind.

## Failover

Manual:
```bash
pg_ctl promote -D /var/lib/postgresql/data
```

Standby → primary.

## Auto-Failover

Tools:
- Patroni
- repmgr
- pglookout

For: HA without manual.

## Patroni

Distributed:
- Etcd/Consul for state
- Auto-promotes on primary failure

```yaml
# patroni.yml
scope: postgres
etcd:
  hosts: etcd-1:2379,etcd-2:2379
bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
```

## Replication Slots

Track WAL needed by standby:
- Primary keeps WAL until standby caught up
- Avoid premature deletion

```sql
SELECT pg_create_physical_replication_slot('standby1');
```

Risk: standby down → WAL piles up → disk full.

Monitor:
```sql
SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
```

## Cascading

```
Primary → Standby1 → Standby2 (cascading)
                  → Standby3
```

Reduces primary load.

## Logical Replication

Different:
- Row-level
- Cross-version
- Subset of tables
- Different schema

For: migrations, analytics.

## Setup Logical

Primary:
```sql
ALTER SYSTEM SET wal_level = logical;
-- restart

CREATE PUBLICATION mypub FOR TABLE users, orders;
```

Subscriber:
```sql
CREATE SUBSCRIPTION mysub
CONNECTION 'host=primary dbname=mydb user=repl'
PUBLICATION mypub;
```

## Use Cases

### Migration
Postgres 13 → 16.

### Analytics Replica
Subset of tables to OLAP.

### Multi-Region
Logical replication to remote.

## Conflicts

If subscriber has same data:
- Errors
- Use `with (copy_data=false)` if pre-populated

## Performance

Logical:
- Higher overhead than physical
- Per-row processing
- Slower for huge

For physical when possible.

## Sync Modes

- Streaming async
- Streaming sync
- Logical async
- Logical sync (rare)

## Backups Use Replication

WAL-G / pgbackrest:
- Continuous WAL archiving
- Restore to point-in-time

## Read Scaling

Multiple read replicas:
- Distribute reads
- PgBouncer / proxy in front

## HA Pattern

```
Primary
  └─ Standby1 (sync)
  └─ Standby2 (sync)
  └─ Standby3 (async)
```

Lose primary: promote standby1.

## Cross-Region

```
us-east-1: Primary + 2 standbys
us-west-2: Standby (async; large lag)
```

For: DR.

## Best Practices

- Monitor lag
- Replication slots cleanup
- Patroni for auto-failover
- Test failover
- Backup verification

## Common Mistakes

- No monitoring (silent lag)
- Stale slots (disk fills)
- No failover test
- Manual failover at 3am

## Quick Refs

```sql
-- Replication status
SELECT * FROM pg_stat_replication;
SELECT * FROM pg_replication_slots;

-- Create slot
SELECT pg_create_physical_replication_slot('name');

-- Logical
CREATE PUBLICATION / SUBSCRIPTION
```

```bash
# Basebackup
pg_basebackup -h primary -D /data -U repl

# Failover
pg_ctl promote
```

## Interview Prep

**Mid**: "Postgres replication."

**Senior**: "Sync vs async."

**Staff**: "HA pattern."

## Next Topic

→ [T03 — Connection Pooling (PgBouncer)](T03-PgBouncer.md)
