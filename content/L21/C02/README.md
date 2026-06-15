# L21/C02 — PostgreSQL for SREs

## Topics

- **T01 MVCC, Vacuum, Autovacuum** — Concurrency model
- **T02 Replication** — Streaming, logical
- **T03 Connection Pooling** — PgBouncer
- **T04 Backup** — pg_dump, pg_basebackup, WAL-G
- **T05 Performance Tuning** — Key knobs
- **T06 Transaction Isolation Levels** — Anomalies, defaults, SSI
- **T07 Indexing Strategies** — B-tree/GIN/GiST/BRIN, composite, covering

## MVCC (Multi-Version Concurrency Control)

Postgres holds multiple versions of each row. Readers never block writers; writers never block readers.

### How
- Every row has `xmin` (creator transaction) + `xmax` (deleter transaction)
- Transaction sees rows visible at its snapshot
- Old versions stay until cleaned

### Implications
- Excellent concurrency
- But dead tuples accumulate
- **Bloat** = unused space in tables/indexes
- **Vacuum** removes dead tuples
- **Autovacuum** does it automatically

## Autovacuum

Background process cleans dead tuples. Triggers when:
- Updates/deletes > threshold
- Time since last vacuum > interval

Tuning:
```
autovacuum_naptime = 10s              # check interval
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.1  # 10% of table
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.05
```

On high-write tables: tune more aggressive (lower scale_factor).

### Manual Vacuum
```sql
VACUUM ANALYZE my_table;
VACUUM FULL my_table;        -- locks table; rebuilds from scratch
```

`VACUUM FULL` reclaims space (rewrites table) but takes exclusive lock. Use sparingly.

### Monitoring Bloat
```sql
SELECT relname, n_dead_tup, n_live_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

## Replication

### Streaming Replication (physical)
- WAL (Write-Ahead Log) shipped from primary to replicas
- Replicas replay WAL
- Sync or async
- Read replicas

```
# postgresql.conf on primary
wal_level = replica
max_wal_senders = 5
max_replication_slots = 5
```

### Logical Replication
- Per-table or per-database
- Can replicate to different versions
- Used for: migrations, partial replication, CDC (Debezium)

```sql
-- On primary
CREATE PUBLICATION pub FOR ALL TABLES;
-- On replica
CREATE SUBSCRIPTION sub CONNECTION 'host=primary ...' PUBLICATION pub;
```

### Synchronous Replication
```
synchronous_standby_names = 'replica1'
synchronous_commit = on
```

Commits wait for replica ack. Safety > throughput.

### Async vs Sync Tradeoff
- Sync: zero data loss on failover; slower writes
- Async: faster writes; up to few seconds RPO

## Connection Pooling

Postgres connection is expensive (~5-10MB memory). At 1000 connections, you're using 5-10 GB.

### PgBouncer
- Lightweight (C)
- Modes:
  - **session**: full session (compatible with all features)
  - **transaction**: per-transaction (most common; some features incompat: prepared statements, advisory locks)
  - **statement**: per-statement (most aggressive)
- Reduces Postgres connections by 100×

```ini
# pgbouncer.ini
[databases]
mydb = host=postgres port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
```

### AWS RDS Proxy
- Managed pooling
- IAM auth integration
- Failover support

## Backups

### pg_dump (logical)
```bash
pg_dump -Fc mydb > mydb.dump
pg_restore -d mydb mydb.dump
```

- Per-table or full DB
- Version-portable
- Restore time linear with data size
- Bad for very large DBs (TBs)

### pg_basebackup (physical)
```bash
pg_basebackup -D /backup -Ft -z -P
```

- Full base backup (snapshot of data dir)
- Used to bootstrap replicas

### WAL Archiving + WAL-G
Continuous archive of WAL to S3 → point-in-time recovery.

```bash
# postgresql.conf
archive_mode = on
archive_command = 'wal-g wal-push %p'
```

Backup:
```bash
wal-g backup-push /var/lib/postgresql/data
```

Restore to any point in time:
```bash
wal-g backup-fetch /restore LATEST
echo "restore_command = 'wal-g wal-fetch %f %p'" >> recovery.conf
echo "recovery_target_time = '2026-06-09 12:00:00'" >> recovery.conf
```

### Test Restores
Backups are useless until tested. Quarterly restore drill.

## Performance Tuning

```
shared_buffers = 25% of RAM            # default 128MB; raise to 8 GB for 32GB
effective_cache_size = 75% of RAM      # for query planner
work_mem = 16MB                        # per-operation; careful — multiplies
maintenance_work_mem = 256MB           # for VACUUM, CREATE INDEX
wal_buffers = 16MB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
max_connections = 100                  # keep low; use pooler
random_page_cost = 1.1                 # SSD (default 4.0 for HDD)
effective_io_concurrency = 200         # NVMe; default 1
log_min_duration_statement = 1000      # log queries > 1s
```

### EXPLAIN ANALYZE
```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE user_id = 42;
```

Read the plan:
- Look for Seq Scan on large tables → add index
- Look for high cost vs actual time
- Look for nested loops on large sets

### pg_stat_statements
```sql
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

Top time-consuming queries → optimize.

## Schema Migrations

### Tools
- Flyway, Liquibase, Atlas (declarative), Alembic (SQLAlchemy), golang-migrate
- DB-side: pg_dump diffs

### Online Migrations
- Adding NULLable column: fast (metadata)
- Adding NOT NULL column with default: rewrites entire table (slow on big tables)
- Use `ALTER TABLE ... ADD COLUMN x INT;` then UPDATE in batches; then set NOT NULL

### Tools for Online Changes
- pg_repack
- pg_squeeze
- citus-data has online schema change tooling

## High Availability

### Patroni
- Manages Postgres HA
- Auto-failover
- DCS: etcd / Consul / ZooKeeper
- Used widely in K8s (operators: Zalando, CrunchyData)

### Cloud
- RDS Multi-AZ
- Aurora (storage-decoupled)
- Cloud SQL HA
- Azure Flexible Server HA

## Common Production Issues

- **Bloat** → autovacuum tuning
- **Lock contention** → use pg_locks view; consider explicit locking strategy
- **Connection storms** → use pooler
- **Slow queries** → EXPLAIN, indexes, query rewrite
- **Replication lag** → check sync_state, check network, check tx volume
- **WAL piling up** → archive_command failing; disk fills; DB stops

## Interview Themes

- "MVCC — explain"
- "Autovacuum — what does it do?"
- "Replication options"
- "PgBouncer pooling modes"
- "Tune Postgres for X workload"
- "Backup + PITR strategy"
