# L21/C07/T02 — EXPLAIN ANALYZE Mastery

## Learning Objectives

- Read EXPLAIN output
- Optimize queries

## EXPLAIN

Shows plan without executing:
```sql
EXPLAIN SELECT * FROM users WHERE email = 'a@b.com';
```

## EXPLAIN ANALYZE

Executes; shows actual:
```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE email = 'a@b.com';
```

Better data.

## Output

```
Seq Scan on users  (cost=0.00..1850.00 rows=100 width=200) (actual time=0.020..15.000 rows=1 loops=1)
  Filter: (email = 'a@b.com')
  Rows Removed by Filter: 99999
  Buffers: shared hit=850
Planning Time: 0.100 ms
Execution Time: 15.050 ms
```

## Read

### Cost
Estimated. Compare options.

### Rows
Estimated. Compare actual.

### Width
Bytes per row.

### Actual Time
Real timing.

### Rows (actual)
Compare estimated to actual; if off, ANALYZE.

### Buffers
Shared hit (cache), read (disk).

## Operators

### Seq Scan
Full table read.
Bad for large filtered.

### Index Scan
Use index; lookup.
Good for selective.

### Index Only Scan
Index has all needed columns. No table read.

### Bitmap Scan
Bitmap index; multiple indexes combined.

### Hash Join
In-memory hash; medium tables.

### Merge Join
Both sides sorted; large tables.

### Nested Loop
Inner table per outer row; small inner.

## When Each Join

### Hash
Medium-large tables; one fits in memory.

### Merge
Both sorted; can be huge.

### Nested Loop
Inner indexed; small to medium.

## Optimizer Choices

PG chooses based on stats. Wrong stats = wrong choice.

```sql
ANALYZE users;
```

For: refresh.

## Common Findings

### Seq Scan on Big
Missing index.
```sql
CREATE INDEX idx ON users(email);
```

### Estimated vs Actual Way Off
Stats stale.
```sql
ANALYZE table;
```

### Sort to Disk
work_mem too low:
```sql
SET work_mem = '64MB';
```

### Hash Spill
Same.

### Nested Loop on Big
Hash join better.
Force:
```sql
SET enable_nestloop = off;
```

(Don't permanently disable.)

## EXPLAIN Options

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) <query>;
```

- ANALYZE: actually run
- BUFFERS: buffer stats
- VERBOSE: more detail
- FORMAT: text, json, xml, yaml

## Visualize

Tools:
- depesz.com (paste; visualize)
- pgMustard
- pev (PG explain visualizer)

For: easier reading.

## Sub-Plans

Subqueries:
- May be evaluated once
- Or per outer row (bad)

Look for "InitPlan" (once) vs "SubPlan" (per).

## CTE

Postgres 12+:
- Inlines (default; optimizer choice)
- AS MATERIALIZED to force materialize

## Window Functions

Often:
- WindowAgg node
- Costly for big partitions
- Index on PARTITION BY

## Aggregations

```
HashAggregate or GroupAggregate
```

GroupAggregate: sorted input.
HashAggregate: builds hash.

For: depends on input.

## Stats

```sql
SELECT relname, n_live_tup, last_analyze FROM pg_stat_user_tables ORDER BY last_analyze DESC;
```

Stale stats → bad plans.

## Specific Optimizations

### Pagination
```sql
-- Bad
SELECT * FROM events ORDER BY id LIMIT 20 OFFSET 100000;

-- Better
SELECT * FROM events WHERE id > LAST_ID ORDER BY id LIMIT 20;
```

Keyset pagination.

### Count
```sql
SELECT COUNT(*) FROM big_table;
```

Slow. Approximate:
```sql
SELECT reltuples::bigint FROM pg_class WHERE relname='big_table';
```

### LIKE
```sql
WHERE name LIKE 'al%'   -- can use index
WHERE name LIKE '%al%'  -- can't
```

Trigram index for substring:
```sql
CREATE INDEX idx ON users USING gin(name gin_trgm_ops);
```

## Best Practices

- EXPLAIN ANALYZE before optimizing
- Compare estimated to actual
- ANALYZE after changes
- Visual tools
- Index for filters and joins
- work_mem appropriate

## Common Mistakes

- EXPLAIN without ANALYZE (no actuals)
- Trust optimizer with stale stats
- Force plans (brittle)
- Skip BUFFERS (miss IO)

## Quick Refs

```sql
EXPLAIN (ANALYZE, BUFFERS) <query>;
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) <query>;

-- Stats
ANALYZE table;
SELECT * FROM pg_stat_user_tables;
```

## Interview Prep

**Mid**: "Read EXPLAIN."

**Senior**: "Optimize query."

**Staff**: "Performance analysis."

## Next Topic

→ [T03 — pg_stat_statements, performance_schema](T03-pg-stat-statements.md)
