# L21/C01/T02 — Row vs Column Storage

## Learning Objectives

- Understand storage layouts
- Pick by access pattern

## Row Storage

Records stored as rows:
```
Row 1: id=1, name="alice", age=30
Row 2: id=2, name="bob", age=25
Row 3: id=3, name="carol", age=35
```

Disk:
```
| id=1 | name=alice | age=30 | id=2 | name=bob | age=25 | ...
```

For: full-row reads.

## Column Storage

Records stored per column:
```
Column id: 1, 2, 3
Column name: alice, bob, carol
Column age: 30, 25, 35
```

Disk:
```
ids: | 1 | 2 | 3 |
names: | alice | bob | carol |
ages: | 30 | 25 | 35 |
```

For: column aggregations.

## Why Different

### Row
- Read 1 row: fast
- Sum ages: read all data (every row)

### Column
- Read 1 row: slow (assemble from columns)
- Sum ages: read only `age` column

## OLTP Uses Row

App reads:
```sql
SELECT * FROM users WHERE id = 1
```

Row layout: 1 disk read.

## OLAP Uses Column

Analyst:
```sql
SELECT AVG(age) FROM users
```

Column layout: read only `age` column. Faster.

## Compression

Column: same data type contiguous.

```
ages: 30, 25, 35, 30, 28, 30
```

Compress (run-length, dictionary):
```
30:3, 25:1, 35:1, 28:1, 30:1
```

Much smaller. Higher throughput.

For: 5-10× compression typical.

## Vectorized Execution

Column store:
- Process column in batch
- SIMD instructions
- Fast

Row store: tuple-at-a-time.

## Cache

Column: each query reads less data.
Better CPU cache usage.

For: speed.

## Examples

### Row
- Postgres
- MySQL
- Oracle
- SQL Server (default)
- DynamoDB

### Column
- BigQuery
- Redshift
- Snowflake
- ClickHouse
- Parquet (file format)
- Vertica

### Hybrid
- AlloyDB Columnar Engine
- Postgres with cstore_fdw
- TiDB TiFlash

## Cardinality Impact

Column store:
- Low cardinality (status: active, inactive): great compression
- High cardinality (user_id): less benefit

## Inserts

Row:
- Fast (append row)

Column:
- Slow (per-column write)
- Batch inserts much better

For: column = bulk loads.

## Updates

Row:
- Update one row in place

Column:
- Often immutable (new file)
- Compaction later

For: column not great for frequent updates.

## Parquet

File format:
- Column store
- Compressed
- Statistics per chunk

For: data lake.

## ORC

Similar to Parquet:
- Apache project
- Hive-friendly

## Apache Iceberg / Delta Lake

Table formats over Parquet:
- ACID
- Time travel
- Schema evolution

For: data lake → lakehouse.

## Hybrid Workloads

- Recent data: row (frequent updates)
- Old data: column (analytics)

TiDB TiFlash: row primary + column secondary.

## Examples Big

### Clickhouse
Column store; massive scale.

### BigQuery
Column store under hood; serverless.

### Redshift
Column store.

## Best Practices

- OLTP → row
- OLAP → column
- Hybrid (HTAP): TiDB
- Bulk insert column
- Compression awareness

## Common Mistakes

- Single-row queries on column store (slow)
- Frequent updates on column (compaction storm)
- No compression awareness

## Quick Refs

```
Row:    OLTP, single-row, updates
Column: OLAP, aggregations, compression
Parquet: column file format
Iceberg: table format

Compression: 5-10× for column
SIMD:      column wins
```

## Interview Prep

**Junior**: "Row vs column."

**Mid**: "When each."

**Senior**: "Hybrid storage."

## Next Topic

→ [T03 — SQL vs NoSQL vs NewSQL](T03-SQL-NoSQL-NewSQL.md)
