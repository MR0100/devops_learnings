# L21/C07/T01 — Slow Query Logs

## Learning Objectives

- Enable slow logs
- Find bottlenecks

## Why

Slow queries:
- Impact user
- Saturate DB
- Pile up

For: find + fix.

## Postgres

```ini
# postgresql.conf
log_min_duration_statement = 1000   # ms
log_statement = 'mod'              # log writes
log_line_prefix = '%t [%p] %u@%d '
```

Logs queries > 1 sec.

## MySQL

```ini
slow_query_log = ON
long_query_time = 1.0
slow_query_log_file = /var/log/mysql/slow.log
log_queries_not_using_indexes = ON
```

## Mongo

```js
db.setProfilingLevel(1, {slowms: 100})
```

Profile slow.

## Parse Postgres Log

```bash
pgbadger /var/log/postgresql/postgresql.log -o report.html
```

For: HTML report.

## Parse MySQL

```bash
pt-query-digest /var/log/mysql/slow.log
```

## Auto-Analyze

Centralize:
- Loki / ELK
- Datadog
- Splunk

Alert on:
- Spike in slow queries
- New slow query types

## Top Slow

```sql
-- Postgres pg_stat_statements
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Common Causes

- Missing index
- Bad plan (stale stats)
- Lock contention
- Hot rows
- Cartesian product
- Network slow

## Investigate

```sql
EXPLAIN (ANALYZE, BUFFERS) <query>;
```

See plan; cost.

## Add Index

If seq scan:
```sql
CREATE INDEX idx_X ON users(email);
```

Test impact.

## Stats

```sql
ANALYZE table;
```

For: optimizer.

## Killing

If query stuck:
```sql
-- Postgres
SELECT pg_cancel_backend(pid);
SELECT pg_terminate_backend(pid);

-- MySQL
KILL QUERY thread_id;
```

## Apps

Some queries from app:
- N+1
- Inefficient ORM
- Bad pagination

Fix in app.

## Cost

Slow log overhead: minimal (% of queries).

For: always enabled in prod.

## Sample Rate

For very high QPS:
```sql
auto_explain.log_min_duration = 1000
auto_explain.log_analyze = on
auto_explain.sample_rate = 0.01
```

Sample 1%.

## Best Practices

- Threshold: 1-3 sec
- Tools (pgbadger, pt-query-digest)
- Top 10 weekly review
- pg_stat_statements
- Fix top consistently

## Common Mistakes

- Disable (lose visibility)
- Too low threshold (noise)
- No review (logs ignored)
- No action on findings

## Quick Refs

```ini
# Postgres
log_min_duration_statement = 1000

# MySQL
slow_query_log = ON
long_query_time = 1.0

# Mongo
db.setProfilingLevel(1, {slowms: 100})
```

```bash
pgbadger log → report
pt-query-digest log
```

## Interview Prep

**Mid**: "Slow query log."

**Senior**: "Investigate slow."

**Staff**: "Query performance ops."

## Next Topic

→ [T02 — EXPLAIN ANALYZE Mastery](T02-EXPLAIN-ANALYZE.md)
