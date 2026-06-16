# L21/C01/T01 — OLTP vs OLAP

## Learning Objectives

- Distinguish workloads
- Pick right DB

## OLTP

Online Transaction Processing:
- High frequency, small reads/writes
- ACID
- Latency-sensitive
- Examples: e-commerce, banking

## OLAP

Online Analytical Processing:
- Low frequency, large reads
- Aggregations
- Throughput-sensitive
- Examples: business intel, reports

## Characteristics

| | OLTP | OLAP |
|---|---|---|
| Workload | many small queries | few large queries |
| Latency | ms | seconds-minutes OK |
| Consistency | strong | eventual OK |
| Schema | normalized | denormalized |
| Storage | row | column |
| Volume | GB-TB | TB-PB |
| Users | many concurrent | analysts |

## DBs

### OLTP
- PostgreSQL
- MySQL
- Oracle
- SQL Server
- DynamoDB
- Spanner

### OLAP
- BigQuery
- Snowflake
- Redshift
- ClickHouse
- Druid

## Hybrid (HTAP)

- TiDB
- SingleStore
- AlloyDB
- CockroachDB (with analytics)

For: both workloads.

## Patterns

### Separate DBs
OLTP: Postgres.
OLAP: BigQuery / Snowflake.
ETL: Replicate.

For: most.

### Read Replicas
OLTP primary; analytical replicas.

For: simple.

### CQRS
Command Query Responsibility Segregation:
- Writes go to OLTP
- Reads from read-optimized

## ETL / ELT

ETL:
- Extract from OLTP
- Transform
- Load to OLAP

Tools: Airbyte, Fivetran, dbt.

ELT (modern):
- Load raw
- Transform in OLAP (SQL)

## Examples

### Shopify
- OLTP: Postgres (orders)
- OLAP: BigQuery (analytics)

### Stripe
- OLTP: Sharded Postgres
- OLAP: Custom

## When Each

### OLTP
- App backend
- Real-time transactions
- ACID needed
- Single-row reads/writes

### OLAP
- Dashboards
- Reports
- Ad-hoc analytics
- Time-series

## Performance Differences

### OLTP
- Index reads
- Point queries: 1ms
- Concurrent writes
- Locking

### OLAP
- Scan billions of rows
- Aggregations
- Columnar
- Parallel

## Don't Mix

OLTP for analytics:
- Slow (full scans on indexed DB)
- Locks affect transactions
- Bad for everyone

For: separate.

## Read Replica for Light Analytics

```
Primary: writes + light reads
Replica: heavy reads (analytics)
```

For: medium scale.

## Materialized Views

Pre-computed aggregations:
```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT date, SUM(amount) FROM orders GROUP BY date;
```

Refresh periodically.

For: complex queries cached.

## Common Mistakes

- OLAP queries on OLTP (slow)
- No replica (overloaded primary)
- Denormalized OLTP (consistency pain)
- Normalized OLAP (slow joins)

## Best Practices

- Pick by workload
- Separate physically
- ETL/ELT pipeline
- Read replicas for medium
- HTAP for need

## Quick Refs

```
OLTP: rows, ACID, low latency
OLAP: columns, aggregations, high throughput
HTAP: both (TiDB, AlloyDB)

Tools:
- OLTP: Postgres, MySQL, DynamoDB
- OLAP: BigQuery, Snowflake, ClickHouse
- ETL: Airbyte, Fivetran
```

## Interview Prep

**Junior**: "OLTP vs OLAP?" — OLTP is many small, fast read/write transactions touching few rows (orders, profiles) on row stores like Postgres/MySQL. OLAP is fewer huge, mostly-read analytical queries scanning millions of rows on column stores like BigQuery/Snowflake/ClickHouse.

**Mid**: "Pick a database for a use case." — Match access pattern to storage: high-TPS point reads/writes → row-oriented OLTP DB; aggregations over big scans → column-oriented warehouse. Don't run heavy analytics on the OLTP primary — replicate or ETL to a warehouse so reporting doesn't starve transactional traffic.

**Senior**: "When do you use one HTAP system vs separate OLTP + OLAP?" — Separate (OLTP DB + ETL/CDC to a warehouse) is the default: each is optimized for its access pattern and they scale independently. Reach for HTAP (TiDB, SingleStore, AlloyDB, Spanner+analytics) when you need near-real-time analytics on fresh transactional data and the operational simplicity of one system outweighs the cost — but watch resource isolation so analytical queries don't degrade transactional latency.

## Next Topic

→ [T02 — Row vs Column Storage](T02-Row-Column-Storage.md)
