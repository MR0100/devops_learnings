# L21/C02/T01 — Postgres MVCC, Vacuum, Autovacuum

## Learning Objectives

- Understand MVCC
- Tune autovacuum

## MVCC

Multi-Version Concurrency Control:
- Readers don't block writers
- Writers don't block readers
- Each transaction sees snapshot

For: concurrency.

## How

Each row has:
- xmin: created by tx
- xmax: deleted by tx

Tx N reads rows with xmin < N AND (xmax IS NULL OR xmax > N).

## Dead Tuples

Updates / deletes:
- Don't remove
- Set xmax
- New version inserted

Dead tuples accumulate.

## VACUUM

Reclaims:
- Removes dead tuples
- Frees space (within file)
- Updates statistics

```sql
VACUUM ANALYZE my_table;
```

## VACUUM FULL

Rewrites table:
- Compacts
- Returns space to OS
- LOCKS table (blocking)

For: rare; during maintenance.

## Autovacuum

Background process:
- Triggers on dead tuple %
- Runs VACUUM ANALYZE
- Default: every 1 min check

For: don't disable.

## Triggers

Default:
```
autovacuum_vacuum_scale_factor = 0.2   # 20% dead
autovacuum_vacuum_threshold = 50
```

Table N rows: trigger when (0.2 × N + 50) dead.

For 1M rows: 200,050 dead → trigger.

## Per-Table Override

```sql
ALTER TABLE big_table SET (
  autovacuum_vacuum_scale_factor = 0.05,
  autovacuum_vacuum_threshold = 1000
);
```

For: aggressive tables.

## Bloat

Dead tuples not vacuumed:
- Slower queries
- More disk
- Performance pain

## Detect Bloat

```sql
SELECT relname, n_live_tup, n_dead_tup,
       n_dead_tup::float / NULLIF(n_live_tup, 0) AS ratio
FROM pg_stat_user_tables
ORDER BY ratio DESC NULLS LAST
LIMIT 10;
```

For: identify.

## Tools

- pg_bloat_check
- pgstattuple

## VACUUM Strategy

- Frequent (small) > rare (huge)
- Don't VACUUM FULL prod (locking)
- pg_repack: online VACUUM FULL

## pg_repack

```sql
pg_repack -d mydb -t my_table
```

Rebuild without locking. Slower but online.

## Long-Running Transactions

Hold dead tuples:
- VACUUM can't remove
- Bloat grows

Find:
```sql
SELECT pid, query, state, age(backend_xid)
FROM pg_stat_activity
ORDER BY age(backend_xid) DESC NULLS LAST
LIMIT 10;
```

Kill if needed:
```sql
SELECT pg_cancel_backend(PID);
```

## Replication Slots

Unused replication slot:
- Holds WAL
- Disk fills

```sql
SELECT slot_name, active, restart_lsn
FROM pg_replication_slots;
```

Drop unused:
```sql
SELECT pg_drop_replication_slot('slot_name');
```

## Hot Standby

Replicas:
- Read-only
- Lag from primary

Long queries on standby:
- Can delay vacuum on primary
- `hot_standby_feedback = on` helps

## Settings

```ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 5
autovacuum_naptime = 1min
autovacuum_vacuum_cost_delay = 2ms
autovacuum_vacuum_cost_limit = 200
```

Tune for:
- More workers (parallel)
- Less delay (more I/O)
- Higher cost limit

## Monitor

```promql
pg_stat_user_tables_n_dead_tup
pg_stat_user_tables_last_autovacuum
```

## Cost Limit

Pages per cycle:
- Higher: more I/O
- Lower: less impact on transactions

For: balance.

## Best Practices

- Autovacuum ON
- Tune per-table for hot
- Monitor bloat
- pg_repack for online clean
- Watch replication slots
- Hot standby feedback if standby query

## Common Mistakes

- Disable autovacuum (death)
- VACUUM FULL in business hours
- Ignore bloat warnings
- Unused replication slots
- Long transactions

## Quick Refs

```sql
-- Manual
VACUUM ANALYZE table;
VACUUM FULL table;   -- locking

-- Stats
SELECT * FROM pg_stat_user_tables;

-- Bloat
SELECT relname, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;

-- Long tx
SELECT pid, query, age(backend_xid) FROM pg_stat_activity;

-- Online repack
pg_repack -t table
```

## Interview Prep

**Mid**: "What is MVCC?" — Multi-Version Concurrency Control: Postgres keeps multiple versions of each row (tagged with `xmin`/`xmax`), so a transaction reads a consistent snapshot without blocking writers, and writers don't block readers. The cost is dead tuples that accumulate and must be cleaned up.

**Senior**: "How do you tune autovacuum?" — Autovacuum removes dead tuples when updates/deletes pass a threshold (`scale_factor` × table size + `threshold`). On high-write tables the default 20% scale factor lets bloat pile up, so lower `autovacuum_vacuum_scale_factor` per table (e.g. 0.05), raise `maintenance_work_mem`, and increase worker count/cost limits. Monitor `n_dead_tup` and table/index bloat.

**Staff**: "What MVCC failure modes bite you at scale?" — Long-running transactions hold back the xmin horizon so autovacuum can't reclaim dead tuples anywhere — bloat grows and plans degrade; kill or bound long transactions. Watch for **transaction ID wraparound**: if vacuum falls behind, Postgres forces aggressive anti-wraparound vacuums and can ultimately refuse writes. Operate with per-table autovacuum tuning, `pg_repack` for online de-bloat, and alerting on dead-tuple ratio and oldest-xmin age.

## Next Topic

→ [T02 — Replication (Streaming, Logical)](T02-Replication.md)
