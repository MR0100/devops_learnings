# L21/C07 — Database Observability

## Topics

- **T01 Slow Query Logs** — Find expensive queries
- **T02 EXPLAIN ANALYZE Mastery** — Read query plans
- **T03 pg_stat_statements, performance_schema** — Aggregate query stats

## Slow Query Logs

### Postgres
```
log_min_duration_statement = 1000   # log queries > 1s
log_statement = 'mod'               # log DDL + INSERT/UPDATE/DELETE
log_line_prefix = '%t [%p]: db=%d,user=%u,client=%h '
```

Output to `/var/log/postgresql/...`.

Tools to analyze:
- **pgbadger** — generate HTML report from logs
- **pganalyze** — SaaS

### MySQL
```
slow_query_log = 1
long_query_time = 1                 # log queries > 1s
slow_query_log_file = /var/log/mysql/slow.log
log_queries_not_using_indexes = 1
```

Tools:
- **pt-query-digest** (Percona) — analyze
- **mysqldumpslow**

## pg_stat_statements (Postgres)

Aggregated stats per query.

```sql
CREATE EXTENSION pg_stat_statements;

SELECT
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

Top time-consuming queries by aggregate. Different from "slowest single query".

### Reset
```sql
SELECT pg_stat_statements_reset();
```

Often reset weekly to see what's growing.

## performance_schema (MySQL)

```sql
SELECT
  digest_text,
  count_star,
  sum_timer_wait / 1e12 AS sum_seconds,
  avg_timer_wait / 1e9 AS avg_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC
LIMIT 20;
```

Or `sys` schema:
```sql
SELECT * FROM sys.statements_with_runtimes_in_95th_percentile;
SELECT * FROM sys.schema_tables_with_full_table_scans;
```

## EXPLAIN ANALYZE

### Postgres
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT * FROM orders WHERE user_id = 42;
```

Output:
```
Index Scan using orders_user_id_idx on orders  (cost=0.42..8.45 rows=1 width=128) (actual time=0.034..0.035 rows=1 loops=1)
  Index Cond: (user_id = 42)
  Buffers: shared hit=4
Planning Time: 0.123 ms
Execution Time: 0.057 ms
```

What to look for:
- **Seq Scan** on large tables → add index
- High cost vs actual time → planner stats stale (run ANALYZE)
- **Nested Loop** on large outer → may need hash/merge join (collect stats; increase work_mem)
- **Filter: ...** → predicate not pushed down to index; check index quality
- **Buffers**: hit (cache) vs read (disk)

### MySQL
```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
EXPLAIN ANALYZE SELECT ...  -- MySQL 8.0+
EXPLAIN FORMAT=JSON ...
```

## Other Useful Views

### Postgres
```sql
-- Current activity
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity
WHERE state != 'idle';

-- Blocking queries
SELECT pid, query, wait_event_type, wait_event
FROM pg_stat_activity
WHERE wait_event IS NOT NULL;

-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) as size
FROM pg_class
WHERE relkind = 'r'
ORDER BY pg_total_relation_size(oid) DESC
LIMIT 20;

-- Index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;  -- unused indexes
```

### MySQL
```sql
-- Current activity
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS\G

-- Table sizes
SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'mydb'
ORDER BY size_mb DESC;
```

## Metrics to Track

### Postgres
- Active connections (vs max_connections)
- Replication lag
- Buffer cache hit ratio (`blks_hit / (blks_hit + blks_read)` > 99%)
- Tuple rates (inserts, updates, deletes)
- Vacuum activity
- Lock waits

### MySQL
- Threads_connected
- Threads_running
- Replication lag (Seconds_Behind_Master, but unreliable; prefer pt-heartbeat)
- InnoDB buffer pool hit rate
- Slow query count
- Aborted_connects

### Standard
- Disk usage
- IOPS
- CPU
- Memory
- Network

## APM for Databases

### Open Source
- **pgwatch2** — Postgres-focused
- **mysqldash**

### Commercial
- **Datadog DB Monitoring**
- **pganalyze**
- **VividCortex (SolarWinds)**
- **PMM (Percona)**

### What APM Adds
- Auto-tagging queries with execution plans
- Track plan changes over time
- Recommend indexes
- Correlate slow queries with app activity (traces)

## Common Performance Issues

### Missing Index
- Slow query
- EXPLAIN shows Seq Scan
- Add index; re-EXPLAIN

### Wrong Index
- Index exists but not used
- Stale planner stats → `ANALYZE`
- Predicate doesn't match index columns
- Function on column prevents index use (`WHERE lower(name)`) → expression index

### N+1 Queries
- App does query in a loop
- 1 query becomes N
- Fix in app (eager load, JOIN)
- Detect via slow query log (lots of similar queries)

### Lock Contention
- Many sessions waiting on a row
- Long-running transaction holds lock
- Fix: shorter transactions; better locking strategy

### Slow Replication
- Replica can't keep up with primary writes
- Causes:
  - Single-threaded SQL apply (MySQL)
  - Long-running queries blocking replication
  - Network slow
- Fix: parallel replication, faster network, batch on primary

### Bloat (Postgres)
- Autovacuum can't keep up
- Tables and indexes grow
- Fix: tune autovacuum aggressive; periodic VACUUM FULL during low traffic

## Tracing in DB Calls

Modern: trace context propagation into DB.

- Add `SET application_name = 'trace_id_abc'` per session
- OpenTelemetry SQL drivers auto-add comment with trace_id: `/* traceparent='00-...-...' */`
- Read traces in log: which trace caused which slow query?

## Interview Themes

- "Walk through EXPLAIN ANALYZE"
- "pg_stat_statements — what does it show?"
- "Diagnose a slow query"
- "Bloat — what's it and what's the fix?"
- "Replication lag — causes and fixes"
- "Top metrics to monitor on Postgres"
