# L21/C07/T03 — pg_stat_statements, performance_schema

## Learning Objectives

- Use stat extensions
- Find top queries

## pg_stat_statements

Postgres extension:
- Tracks query execution
- Aggregates by query template

## Enable

```ini
shared_preload_libraries = 'pg_stat_statements'
```

```sql
CREATE EXTENSION pg_stat_statements;
```

Restart.

## Query

```sql
SELECT 
  query,
  calls,
  total_exec_time / 1000 AS total_sec,
  mean_exec_time AS mean_ms,
  rows / NULLIF(calls, 0) AS avg_rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

Top time consumers.

## Reset

```sql
SELECT pg_stat_statements_reset();
```

After tuning; measure improvement.

## Track

Add to dashboards:
- Top 10 by total time
- Top 10 by mean time
- Top 10 by IO

## Identify Patterns

- One slow query called many times: index?
- Quick queries called millions: cache?
- Different queries each call: parameterize?

## MySQL performance_schema

Equivalent:
```sql
SELECT digest_text, count_star, avg_timer_wait/1000000 AS avg_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC
LIMIT 10;
```

## sys schema (MySQL)

Wraps performance_schema:
```sql
SELECT * FROM sys.statement_analysis ORDER BY total_latency DESC LIMIT 10;
```

For: easier.

## Slow + Frequent

```sql
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
WHERE calls > 100
ORDER BY total_exec_time DESC;
```

Both: maximum ROI on fix.

## Correlate with App

Query template:
```
SELECT * FROM users WHERE id = ?
```

App-side: which endpoint sends this?

For: tie to app code.

## With Traces

OTel:
- Span attributes: db.statement
- Tie slow query → app trace

For: holistic.

## Performance Insights

Native cloud:
- AWS RDS Performance Insights
- Azure SQL DB Insights
- GCP Database Insights

For: managed; pre-built.

## ProxySQL Stats

```sql
SELECT * FROM stats_mysql_query_digest ORDER BY sum_time DESC;
```

For: routed view.

## DataDog DBM

Database Monitoring:
- Query-level
- Plan tracking
- Wait events

For: commercial; powerful.

## Metrics

```promql
pg_stat_statements_total_exec_time
pg_stat_statements_calls
pg_stat_statements_mean_exec_time
```

Per-query exposed by exporters.

## Best Practices

- pg_stat_statements always
- Weekly review top 10
- Reset after fixes
- Correlate with traces
- Performance Insights if AWS

## Common Mistakes

- Disable (lose data)
- Top by avg only (miss frequent quick)
- No correlation
- No reset

## Quick Refs

```sql
-- Postgres
SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC;
SELECT pg_stat_statements_reset();

-- MySQL
SELECT * FROM sys.statement_analysis;
SELECT * FROM performance_schema.events_statements_summary_by_digest;
```

## Interview Prep

**Mid**: "pg_stat_statements."

**Senior**: "Find top queries."

**Staff**: "DB observability."

## Next Topic

→ Move to [L21/C08 — Operational Patterns](../C08/README.md) or next major topic
