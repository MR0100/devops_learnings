# L21/C02/T07 — Indexing Strategies

## Learning Objectives

- Choose the right index type: B-tree vs hash vs GIN vs GiST vs BRIN
- Design composite and covering indexes and reason about column order
- Understand index-only scans and when they kick in
- Weigh the write-amplification and space cost of every index you add

## What an Index Buys You

An index is a secondary data structure that turns a full-table scan (O(n)) into a targeted lookup (typically O(log n) for B-tree). It speeds **reads** that filter, sort, or join on the indexed columns — at the cost of **slower writes** (every INSERT/UPDATE/DELETE must maintain the index) and **extra storage**. Indexing is a deliberate trade, not a free win.

The query planner *chooses* whether to use an index based on cost estimates and statistics (`ANALYZE`). An index can exist and still be ignored if a sequential scan is cheaper (e.g. the predicate matches most rows).

## Index Types

### B-tree (default)
Balanced tree, sorted. The workhorse — supports equality **and** range (`=, <, <=, >, >=, BETWEEN`), `ORDER BY`, and prefix `LIKE 'abc%'`. Default in Postgres and the only general-purpose index in InnoDB.

```sql
CREATE INDEX idx_orders_created ON orders(created_at);
```

### Hash
Equality only (`=`), no ranges, no ordering. Postgres hash indexes are crash-safe and WAL-logged since PG 10, but B-tree usually wins because it also handles ranges — hash is niche (very large keys, equality-only).

### GIN (Generalized Inverted Index)
For values that contain **multiple keys**: full-text search (`tsvector`), `jsonb`, arrays. Inverted index maps each element → rows.

```sql
CREATE INDEX idx_doc_fts ON docs USING GIN (to_tsvector('english', body));
CREATE INDEX idx_attrs   ON items USING GIN (attributes);   -- jsonb containment @>
```
Fast lookups, but slower/heavier to update (mitigated by the `fastupdate` pending list).

### GiST (Generalized Search Tree)
Extensible tree for **overlap/nearest** problems: geometric/spatial (PostGIS), ranges (`int4range`, exclusion constraints), nearest-neighbor (`ORDER BY geom <-> point`). Lossy but flexible.

### BRIN (Block Range Index)
Stores min/max per block range — tiny on disk. Great when the column is **naturally correlated with physical order** (append-only `created_at`, time-series, log tables). A multi-GB table may need only a few KB of BRIN to skip irrelevant blocks. Useless if data isn't physically ordered by the column.

```sql
CREATE INDEX idx_events_time_brin ON events USING BRIN (created_at);
```

| Type | Best for | Supports |
|---|---|---|
| B-tree | general | =, ranges, sort, prefix LIKE |
| Hash | equality-only, big keys | = |
| GIN | fts, jsonb, arrays | containment, multi-value |
| GiST | spatial, ranges, KNN | overlap, nearest |
| BRIN | huge, physically-ordered | block-range skipping (tiny) |

## Composite Indexes & Column Order

A composite index covers multiple columns; **order matters**. An index on `(a, b, c)` can serve predicates on a leading prefix: `a`, `a,b`, `a,b,c` — but **not** `b` alone or `c` alone.

```sql
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
-- Serves: WHERE user_id = 42
--         WHERE user_id = 42 ORDER BY created_at DESC
-- Does NOT serve: WHERE created_at > '2026-01-01'   (created_at is not a prefix)
```

Rule of thumb: put **equality columns first, range/sort columns last**. A range on a leading column stops the index from using later columns for filtering.

## Covering Indexes & Index-Only Scans

If an index contains **every column a query needs**, the database answers from the index alone — never touching the heap. This is an **index-only scan** and it's a major win for hot queries.

```sql
-- Postgres: INCLUDE carries extra columns in the leaf without indexing them
CREATE INDEX idx_orders_cover ON orders(user_id) INCLUDE (status, total);

-- Query reads status,total straight from the index:
SELECT status, total FROM orders WHERE user_id = 42;
```

Postgres caveat: index-only scans also consult the **visibility map**; a table with many recently-modified (not-yet-vacuumed) rows may still hit the heap. Keep such tables well-vacuumed. In InnoDB, every secondary index implicitly "covers" the **primary key** (secondary leaves store the PK), so `SELECT pk_col WHERE secondary = x` is already covering.

## Write Amplification & Other Trade-offs

Every index multiplies write cost and storage:

- **Write amplification** — N indexes ≈ N extra structures to update per write. A table with 8 indexes can be several times slower to insert into than one with 2.
- **Space** — indexes are often 20-50%+ of table size combined; they compete for buffer-pool/`shared_buffers` cache.
- **HOT updates (Postgres)** — an UPDATE that doesn't touch any indexed column can do a Heap-Only Tuple update and skip index maintenance. Indexing a frequently-updated column kills this optimization.
- **Maintenance** — B-trees fragment/bloat; rebuild with `REINDEX CONCURRENTLY` (PG) when bloated.

Don't index speculatively. Add indexes for queries you can see in `pg_stat_statements`/slow logs, drop ones `pg_stat_user_indexes` shows as never scanned.

## Building Indexes Safely

```sql
-- Postgres: build without an exclusive lock (slower, but online)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Partial index: only the rows you query
CREATE INDEX idx_active ON users(email) WHERE active;

-- Expression index: index the computed value you filter on
CREATE INDEX idx_lower_email ON users(lower(email));
```

`CONCURRENTLY` can leave an INVALID index if it fails — check and `DROP`/rebuild. InnoDB online DDL (`ALGORITHM=INPLACE`) covers most secondary-index adds without blocking writes; for huge tables use gh-ost/pt-osc (see C05).

## Common Mistakes

- Indexing every column "to be safe" — cripples writes, bloats storage, and the planner ignores most of them.
- Wrong composite order — putting a range/low-selectivity column first so the prefix rule can't help later columns.
- Indexing a low-cardinality column (e.g. boolean `status` with 2 values) and expecting a speedup — a seq scan is often cheaper; use a **partial** index instead.
- Expecting `WHERE lower(email) = ...` or `WHERE col + 1 = ...` to use a plain `col` index — it won't; you need an **expression index**.
- Forgetting `ANALYZE` after bulk loads — stale stats make the planner skip good indexes.
- Leaving unused/redundant indexes (e.g. `(a)` when `(a,b)` exists) consuming write budget.

## Best Practices

- Index for the queries you actually run; verify with `EXPLAIN (ANALYZE, BUFFERS)` that the index is used.
- Equality-first, range/sort-last in composite indexes; match the index to the query's WHERE + ORDER BY.
- Use covering/`INCLUDE` indexes for hot read paths to get index-only scans.
- Reach for partial indexes on skewed predicates and expression indexes for computed filters.
- Pick the type to the data: B-tree by default, GIN for jsonb/fts, GiST for spatial, BRIN for huge append-only time-series.
- Build big indexes with `CREATE INDEX CONCURRENTLY`; audit `pg_stat_user_indexes` and drop dead weight.

## Quick Refs

```sql
-- Build
CREATE INDEX CONCURRENTLY idx ON t(col);
CREATE INDEX idx ON t(a, b);                 -- composite (prefix rule)
CREATE INDEX idx ON t(user_id) INCLUDE (total);  -- covering
CREATE INDEX idx ON t(email) WHERE active;   -- partial
CREATE INDEX idx ON t USING GIN (jsonb_col); -- jsonb / fts / arrays
CREATE INDEX idx ON big USING BRIN (created_at);

-- Diagnose
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;       -- is the index used?
SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan;  -- find unused
REINDEX INDEX CONCURRENTLY idx;              -- de-bloat
```

## Interview Prep

**Junior**: "What's an index and what does it cost?" — A sorted secondary structure that turns a table scan into a log-n lookup for filters/sorts/joins. It speeds reads but slows writes (every write maintains it) and uses extra space, so you add them deliberately.

**Mid**: "Index on `(a, b, c)` — which queries can use it?" — Any leading prefix: `a`, `a,b`, `a,b,c`. Not `b` alone or `c` alone. Put equality columns first and range/sort columns last, because a range on a leading column stops later columns from being used for filtering.

**Senior**: "When would you use GIN, GiST, or BRIN over B-tree?" — GIN for multi-valued columns (jsonb, arrays, full-text). GiST for overlap/nearest problems (spatial, ranges, KNN). BRIN for huge tables physically ordered by the column (append-only time-series) — tiny on disk, skips block ranges. B-tree stays the default for equality + range + ordering.

**Staff**: "A write-heavy table is slowing down after we added indexes — how do you reason about it?" — Each index adds write amplification and competes for cache, and indexing a frequently-updated column disables Postgres HOT updates (forcing index maintenance per UPDATE). Audit `pg_stat_user_indexes` for unused/redundant indexes and drop them, prefer covering indexes only on genuine hot read paths, consider partial indexes to shrink maintenance, and accept that the right index count balances read latency against write throughput — not "more is better."

## Next Topic

→ Move to [L21/C03 — MySQL for SREs](../C03/README.md)
