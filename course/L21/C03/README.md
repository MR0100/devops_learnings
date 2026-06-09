# L21/C03 — MySQL for SREs

## Topics

- **T01 InnoDB Internals** — Default storage engine
- **T02 Replication** — Async, semi-sync, group
- **T03 ProxySQL** — Pooling + routing
- **T04 Backup** — mysqldump, Percona XtraBackup

## InnoDB

The default storage engine since MySQL 5.5.

### Properties
- ACID transactions
- Row-level locking
- MVCC
- Clustered index on primary key
- Foreign key support
- Crash recovery via redo log

### Buffer Pool
The in-memory cache of data + indexes. Set to 70-80% of RAM for dedicated DB host.

```
innodb_buffer_pool_size = 32G
innodb_buffer_pool_instances = 8    # split into N pools (1 per 1GB recommended)
```

### Redo Log
Write-ahead log; durability mechanism.

```
innodb_log_file_size = 1G           # large = faster writes, longer recovery
innodb_log_files_in_group = 2
innodb_flush_log_at_trx_commit = 1  # 1 = full durability; 2 = lose 1s on crash; 0 = lose 1s on MySQL crash
innodb_flush_method = O_DIRECT      # avoid double caching
```

### Clustered Index
Primary key determines physical row order. Secondary indexes hold the PK, not row pointer.
- Choose small PK (smaller = less storage in every index)
- Sequential PK avoids page splits
- Common: BIGINT AUTO_INCREMENT

## Replication

### Async (Default)
- Source writes binlog
- Replica IO thread fetches binlog
- Replica SQL thread applies
- Lag possible

### Semi-Synchronous (Plugin)
- Source waits for at least one replica ack before reporting commit success
- Bounded data loss on failover

### Group Replication (MGR)
- Synchronous multi-master with conflict detection
- Underpins InnoDB Cluster (with MySQL Router)
- Strong consistency
- Limit: 9 nodes

### Replication Format
- **STATEMENT**: replicates SQL statements (smaller binlog; non-deterministic queries problematic)
- **ROW**: replicates row changes (larger binlog; safer)
- **MIXED**: ROW for non-determinstic, otherwise STATEMENT

Recommendation: ROW.

### GTID
Global Transaction Identifiers. Track each transaction uniquely across cluster. Simplifies failover.

```
gtid_mode = ON
enforce_gtid_consistency = ON
```

## ProxySQL

Connection pooler + query router.

### Features
- Connection multiplexing (reduce backend connections)
- Read/write split (route SELECTs to replicas; writes to primary)
- Query rules (rewrite, mirror, cache)
- Failover detection
- Per-query firewall

```sql
INSERT INTO mysql_servers (hostgroup_id, hostname, port)
VALUES (10, 'primary', 3306), (20, 'replica1', 3306);

INSERT INTO mysql_query_rules (rule_id, active, match_pattern, destination_hostgroup, apply)
VALUES (1, 1, '^SELECT.*', 20, 1);
```

## Backups

### mysqldump (logical)
```bash
mysqldump --single-transaction --quick --routines --triggers --all-databases > backup.sql
mysql < backup.sql
```

`--single-transaction` for InnoDB; gives consistent snapshot.

For terabyte DBs: too slow for restore. Use XtraBackup.

### Percona XtraBackup (physical, hot)
```bash
xtrabackup --backup --target-dir=/backup
xtrabackup --prepare --target-dir=/backup
# Then start MySQL pointing at /backup
```

- Doesn't lock InnoDB
- Backup is a file-level snapshot of data dir
- Fast restore (no SQL replay)
- Continuous incremental possible

### Binary Log + PITR
Combine XtraBackup + binlogs for point-in-time recovery:
1. Restore base XtraBackup
2. Apply binlogs up to desired time

### MySQL Enterprise Backup
Oracle's commercial; similar to XtraBackup.

## Performance Tuning

```
innodb_buffer_pool_size = 70-80% of RAM
innodb_log_file_size = 1G+
innodb_io_capacity = 2000           # for SSD
innodb_io_capacity_max = 4000
innodb_flush_neighbors = 0          # SSD
max_connections = 1000              # high; pool via ProxySQL
thread_cache_size = 100
table_open_cache = 4000
slow_query_log = 1
long_query_time = 1                 # log queries > 1s
```

### EXPLAIN
```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
EXPLAIN FORMAT=JSON SELECT ...;
```

### Performance Schema
```sql
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC
LIMIT 10;
```

Top resource-consuming queries.

### sys schema
Pre-built views on performance_schema:
```sql
SELECT * FROM sys.statements_with_runtimes_in_95th_percentile;
SELECT * FROM sys.schema_tables_with_full_table_scans;
```

## Online Schema Changes

Adding a column to a billion-row table without locking:

### gh-ost (GitHub)
- Triggerless
- Replication-based
- Throttles based on replication lag
- Cancellable

```bash
gh-ost --alter "ADD COLUMN foo INT" --table=orders --execute
```

### pt-online-schema-change (Percona)
- Trigger-based
- More mature
- Used at many companies

## HA Tools

- **Orchestrator** — failover orchestration
- **MHA** (deprecated)
- **InnoDB Cluster + MySQL Router** — official
- **Vitess** — sharding + HA (YouTube origin; CNCF)

### Vitess
- Sharded MySQL
- Query routing
- Online schema changes
- Used by Slack, GitHub, Square

## Cloud

- **AWS RDS MySQL** — managed, Multi-AZ
- **AWS Aurora MySQL** — shared storage, faster
- **GCP Cloud SQL MySQL**
- **Azure Database for MySQL**

## Common Issues

- **Replication lag** — slow replica disk, big transactions, single-threaded apply (use parallel SQL workers)
- **Full table scans** — missing indexes
- **Deadlocks** — long transactions; reorder operations
- **Connection exhaustion** — no pooler
- **Binlog disk full** — purge old binlogs

## Interview Themes

- "InnoDB buffer pool — what is it?"
- "MySQL replication modes"
- "ProxySQL — read/write split"
- "Online schema change on a huge table"
- "XtraBackup vs mysqldump"
- "Vitess — what does it solve?"
