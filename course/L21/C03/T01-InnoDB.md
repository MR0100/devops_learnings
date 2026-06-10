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

**Mid**: "What's InnoDB."

**Senior**: "Buffer pool."

## Next Topic

→ [T02 — Replication](T02-MySQL-Replication.md)
