# L21/C03/T01 — MySQL InnoDB Internals

## Learning Objectives

- Understand InnoDB
- Tune for prod

## InnoDB

MySQL default engine:
- ACID
- Row-level locking
- Crash recovery
- MVCC

## Storage

```
data files (.ibd per table or shared)
redo log (ib_logfile0, ib_logfile1)
undo logs
```

## Buffer Pool

Memory cache:
- Pages
- Adaptive hash
- LRU

```ini
innodb_buffer_pool_size = 16G   # 70-80% of RAM
```

## Redo Log

```ini
innodb_log_file_size = 2G
innodb_log_files_in_group = 2
```

Crash recovery.

## Doublewrite Buffer

Protects against torn pages.

```ini
innodb_doublewrite = ON  # default
```

## MVCC

Like Postgres:
- Multi-version
- Readers don't block writers
- Undo log holds old versions

## Isolation & Locking

InnoDB's **default isolation level is REPEATABLE READ** (Postgres defaults to READ COMMITTED). A transaction takes a consistent snapshot at its first read, so plain `SELECT`s see the same data for the whole transaction.

To stop phantom rows under REPEATABLE READ, InnoDB locks more than just matched rows:

- **Record locks** — lock an index record.
- **Gap locks** — lock the *gap* between index records, so no other transaction can insert into that range.
- **Next-key locks** — record lock + the gap before it; this is the default for index scans and is what blocks phantoms.

```sql
SELECT @@transaction_isolation;            -- REPEATABLE-READ by default
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;  -- per-session/transaction

-- Locking reads take next-key/gap locks under RR:
SELECT * FROM orders WHERE user_id = 42 FOR UPDATE;
```

Implications:
- Gap locks can block inserts into a range and are a common source of **deadlocks** on secondary indexes.
- Switching to **READ COMMITTED** disables most gap locking (locks only matched rows) — useful for high-concurrency workloads that tolerate phantoms, at the cost of replication needing `binlog_format=ROW`.
- `SELECT ... FOR UPDATE` / `FOR SHARE` are locking reads; plain `SELECT` is a non-locking snapshot read.

## Indexes

- Clustered (primary key; data in leaves)
- Secondary (lookup → primary key)

Clustered = primary key access fast.
Secondary = double-lookup.

## Innodb Cluster

For HA:
- 3+ MySQL with Group Replication
- MySQL Router

For: replication + auto-failover.

## File Format

```ini
innodb_file_per_table = ON   # default; recommended
```

Each table own file. Better for TRUNCATE.

## Compression

```sql
CREATE TABLE x (...) ROW_FORMAT=COMPRESSED;
```

For: storage savings.

## ACID Tuning

```ini
# Fully ACID (slow)
innodb_flush_log_at_trx_commit = 1
sync_binlog = 1

# Less durable (faster)
innodb_flush_log_at_trx_commit = 2
sync_binlog = 0
```

Trade-off.

## Performance

- Buffer pool 70-80% RAM
- Redo log 1-4 GB
- File per table
- SSD

## Best Practices

- 5.7+ or 8.x
- InnoDB only
- File-per-table
- Tune buffer pool
- Monitor undo log

## Common Mistakes

- MyISAM (legacy; no ACID)
- Small buffer pool
- No file-per-table
- Wrong flush settings

## Quick Refs

```ini
innodb_buffer_pool_size = 16G
innodb_log_file_size = 2G
innodb_file_per_table = ON
innodb_flush_log_at_trx_commit = 1
```

```sql
SHOW ENGINE INNODB STATUS;
```

## Interview Prep

**Mid**: "What is InnoDB?" — MySQL's default storage engine: ACID, row-level locking, MVCC (old versions in the undo log), crash recovery via the redo log, and a clustered index on the primary key. It replaced MyISAM, which had no transactions and only table locks.

**Senior**: "What is the buffer pool and how do you size it?" — The in-memory cache of data and index pages (plus the adaptive hash index), managed with an LRU. It's the single biggest performance knob — set `innodb_buffer_pool_size` to ~70-80% of RAM on a dedicated host so the working set stays in memory and reads avoid disk.

**Staff**: "InnoDB defaults to REPEATABLE READ — what are the operational consequences?" — Each transaction reads from a snapshot taken at its first read, and InnoDB prevents phantoms with **next-key/gap locks** on scanned index ranges. Those gap locks block inserts into a range and are a frequent deadlock source, especially on secondary indexes. For high-concurrency workloads that tolerate phantoms, switch to READ COMMITTED (disables most gap locking, but requires `binlog_format=ROW`). Pair with short transactions and the right durability settings (`innodb_flush_log_at_trx_commit`, `sync_binlog`) for the workload.

## Next Topic

→ [T02 — Replication](T02-MySQL-Replication.md)
