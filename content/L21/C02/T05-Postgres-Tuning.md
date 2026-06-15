# L21/C02/T05 — Postgres Performance Tuning

## Learning Objectives

- Tune Postgres
- Find bottlenecks

## Key Parameters

### shared_buffers
Memory for caching:
- 25% of RAM typical
- 8GB on 32GB host

```ini
shared_buffers = 8GB
```

### effective_cache_size
Hint about OS cache:
- 50-75% RAM

```ini
effective_cache_size = 24GB
```

### work_mem
Per-operation memory:
- For sorts, joins
- High = fewer disk writes
- Per-connection, per-operation

```ini
work_mem = 16MB
```

### maintenance_work_mem
VACUUM, CREATE INDEX:
```ini
maintenance_work_mem = 1GB
```

### max_connections
```ini
max_connections = 200
```

Limit; use pooler.

### wal_buffers
```ini
wal_buffers = 16MB
```

### checkpoint settings
```ini
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB
```

Less frequent = larger checkpoints. Trade-off.

### random_page_cost
```ini
random_page_cost = 1.1  # SSD
random_page_cost = 4.0  # HDD (default; old)
```

For SSD: lower so optimizer picks indexes more.

## Tools

### pgbench
```bash
pgbench -i mydb -s 10
pgbench -c 50 -j 4 -T 60 mydb
```

For: benchmark.

### pgtune
Online calculator; suggests config from RAM + workload.

### pg_stat_statements
Top queries:
```sql
CREATE EXTENSION pg_stat_statements;

SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 10;
```

## Query Tuning

EXPLAIN ANALYZE:
```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

Look for:
- Seq scan on large table → add index
- Bad row estimates → ANALYZE
- Sort to disk → increase work_mem
- Loop join on big → hash join

## Indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id_date ON orders(user_id, date DESC);
```

Concurrently:
```sql
CREATE INDEX CONCURRENTLY idx_X ON table(col);
```

No lock; slower but online.

## Index Types

- B-tree (default; range, equality)
- Hash (equality)
- GIN (full text, JSON)
- GiST (geo, full text)
- BRIN (large sorted)

## Partitioning

Large tables:
```sql
CREATE TABLE orders (
  id BIGINT, created_at DATE, ...
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2025_01 PARTITION OF orders
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

For: time-series. Faster scans of recent.

## Connection Pooling

(See T03.)

For: handle 100+ apps with 25 DB conns.

## Vacuum Aggressive

For hot tables:
```sql
ALTER TABLE busy_table SET (autovacuum_vacuum_scale_factor = 0.05);
```

## Statistics

```sql
ANALYZE table;
SET default_statistics_target = 100; -- default; up to 10000
```

For: better query plans.

## Slow Query Log

```ini
log_min_duration_statement = 1000   # ms; log queries > 1s
```

Review log; tune.

## Locks

```sql
SELECT * FROM pg_locks WHERE NOT granted;
```

Find blocking.

## Hot Standbys

For: read scaling.

## Caching

- Postgres internal (shared_buffers)
- OS cache
- App cache (Redis)

Most reads → cache.

## SSD

Crucial:
- High IOPS
- Low latency

NVMe ideal.

## Monitoring

Key metrics:
- Cache hit ratio (> 99%)
- Lock wait
- Buffer / WAL activity
- Slow queries
- Connections

Tools: pgwatch, pgAdmin, Datadog.

## Schema

- Right column types
- Constraints
- Normalize then denormalize where needed

## Best Practices

- shared_buffers 25% RAM
- pg_stat_statements + tune slow
- Indexes on filter/sort
- VACUUM tuned
- Partition huge tables
- Connection pool
- Monitor

## Common Mistakes

- max_connections high (without pool)
- random_page_cost default (SSD)
- No analyze (bad plans)
- No autovacuum tuning
- Missing indexes

## Quick Refs

```sql
-- Slow queries
SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- Explain
EXPLAIN (ANALYZE, BUFFERS) SQL;

-- Cache hit
SELECT sum(blks_hit)*100/sum(blks_hit+blks_read) FROM pg_stat_database;

-- Locks
SELECT * FROM pg_locks WHERE NOT granted;
```

## Interview Prep

**Mid**: "Postgres tuning."

**Senior**: "Slow query analysis."

**Staff**: "Postgres at scale."

## Next Topic

→ [T06 — Transaction Isolation Levels](T06-Isolation-Levels.md)
