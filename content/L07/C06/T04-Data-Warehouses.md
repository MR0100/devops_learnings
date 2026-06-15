# L07/C06/T04 — Data Warehouses (Redshift, BigQuery, Synapse)

## Learning Objectives

- Understand DWH role
- Pick the right service

## OLTP vs OLAP

| | OLTP | OLAP |
|---|---|---|
| Online Transaction Processing | Online Analytical Processing |
| Use | App data: orders, users | Analytics: trends, reports |
| Workload | Many small transactions | Few huge scans |
| Latency target | ms | seconds-minutes |
| Schema | Normalized | Denormalized (star/snowflake) |
| Example | Postgres, MySQL | Redshift, BigQuery |

Data warehouse = OLAP DB optimized for analytics.

## Columnar Storage

DWHs store columnwise (not rowwise):
```
Row store:    [id, name, age], [id, name, age], ...
Column store: [id, id, id, ...], [name, name, ...], [age, age, ...]
```

Why: analytics query few columns from many rows. Skip irrelevant columns; better compression.

## Redshift (AWS)

Columnar; MPP (Massively Parallel Processing). Cluster of nodes.

Variants:
- Provisioned: pick node type + count
- Serverless: auto-scale; pay per RPU-second

Integrations: S3 (COPY/UNLOAD), Glue, QuickSight, Lambda UDFs.

Sort key + distribution key crucial for perf.

## BigQuery (GCP)

Serverless DWH. No cluster management.
- Storage and compute separated; scale independently
- Pricing: $5/TB scanned (on-demand) or flat-rate slot pricing
- SQL standard; UDFs in SQL/JavaScript
- Streams, MV, partitions, clustering, BI Engine

Pay per query (scan); careful with `SELECT *`.

## Synapse Analytics (Azure)

Combines DWH + Spark + data integration. SQL pools (dedicated MPP) + serverless.

## Snowflake

Multi-cloud DWH (third party):
- Storage / compute separation
- Time travel (90-day rewind)
- Zero-copy cloning
- Data sharing across accounts
- Premium pricing

Heavy in enterprise; competitive vs Redshift/BigQuery.

## Lakehouse

Trend: store data in lake (S3 with parquet/iceberg/delta); query with multiple engines (Spark, Trino, Athena).

- Athena (AWS): serverless SQL on S3
- BigLake (GCP): same idea
- Lakehouse Engine (Databricks)
- Iceberg / Delta Lake / Hudi: table formats

ACID on lake; combines warehouse + lake benefits.

## Schema Patterns

### Star
- Fact table (transactions) at center
- Dimension tables (user, product, time, location) around

```
   dim_user      dim_product
       \             /
        fact_sales
       /             \
   dim_time      dim_location
```

Queries: join fact to dims; aggregate.

### Snowflake (Schema)
Normalized dimensions; less denormalization than star.

### Wide
For NoSQL DWHs / column stores; super wide rows; sparse.

## Ingestion

- Batch: nightly ETL
- Streaming: Kinesis / Pub/Sub / Kafka → DWH
- CDC: change data capture from OLTP

Tools: Fivetran, Stitch, Airbyte, Debezium.

## ETL vs ELT

**ETL**: transform before load. Older; needs separate compute.

**ELT**: load raw; transform in DWH. Modern; DWH is the compute.

ELT enabled by cheap DWH compute.

## DBT

Data Build Tool: SQL-based transformations in DWH. Models, tests, docs.

```sql
-- models/marts/customer_metrics.sql
{{ config(materialized='table') }}

SELECT
    customer_id,
    COUNT(order_id) AS orders,
    SUM(amount) AS revenue
FROM {{ ref('orders') }}
GROUP BY customer_id
```

```bash
dbt run
dbt test
```

Standard for analytics engineering.

## Performance Levers

- Partition (by date typically)
- Cluster (multiple keys for filtering)
- Materialized views (precompute)
- Result cache
- Query plan analysis
- Sort key (Redshift)
- Distribution (Redshift: ALL, EVEN, KEY)
- Compression

## Cost Pitfalls

- `SELECT *` on big tables
- No partition filter (full scan)
- Many small files in S3 (overhead)
- Idle clusters running
- Storage > compute waste

BigQuery on-demand: $5/TB scanned. One bad query: $$$.

Mitigations:
- Quotas per user
- Limited bytes per query
- Slot reservations (predictable cost)

## Visualization

- Tableau, PowerBI, Looker, QuickSight, Metabase, Superset
- All connect to DWH via SQL

## Real-Time vs Batch

DWH traditionally batch (T+1). For real-time:
- Snowflake: micro-batches (minutes)
- BigQuery: streaming inserts
- Redshift: streaming ingest
- Druid / Pinot / ClickHouse: sub-second analytics
- Materialize / RisingWave: streaming SQL

## Choosing

| Need | Pick |
|---|---|
| AWS shop, mature | Redshift |
| GCP shop, modern | BigQuery |
| Multi-cloud, premium | Snowflake |
| Azure | Synapse |
| Lakehouse | Databricks / Athena+Iceberg |
| Real-time | ClickHouse / Druid / Pinot |

## Data Mesh

Org pattern: domain teams own their data products; central platform.
- Decentralized
- Treat data as product (with SLA, docs, etc.)

Hot topic; takes years to implement.

## Common Mistakes

- DWH for OLTP (slow inserts)
- OLTP for analytics (kills prod DB)
- No partition/cluster strategy
- One huge ETL job; failure restarts all
- No data quality tests
- Schema drift; queries break silently

## Observability

- Query history
- Cost per query
- Slow queries
- Storage growth
- Schema changes audit

## Best Practices

- Keep OLTP and OLAP separate — never run heavy analytics against the production transactional DB, and never use a DWH as an OLTP store.
- Partition by date and cluster/sort by common filter columns so queries prune data instead of full-scanning.
- Select only needed columns (columnar storage rewards this); avoid `SELECT *` on large tables.
- Prefer ELT (load raw, transform in the DWH) with a tool like dbt for tested, versioned, documented models.
- Control cost with per-user quotas, max-bytes-per-query limits, and slot/RPU reservations for predictable spend; cache results where possible.
- Add data-quality tests and schema-change monitoring so drift doesn't silently break downstream queries.

## Quick Refs

DWH selector:

| Need | Pick |
|---|---|
| AWS, mature MPP | Redshift |
| GCP, serverless, pay-per-scan | BigQuery |
| Multi-cloud, premium features | Snowflake |
| Azure | Synapse |
| Lakehouse (S3 + open table format) | Athena/Iceberg, Databricks |
| Sub-second real-time analytics | ClickHouse / Druid / Pinot |

OLTP vs OLAP: OLTP = many small transactions, normalized, ms latency (Postgres/MySQL); OLAP = few huge scans, denormalized star/snowflake, columnar, seconds (Redshift/BigQuery).

Cost guardrails: BigQuery on-demand is **$5/TB scanned** — partition-filter every query, set per-user byte limits, and reserve slots/RPUs for steady workloads. `SELECT *` with no partition filter is the classic budget killer.

## Interview Prep

**Mid**: "OLAP vs OLTP."

**Senior**: "Design DWH ingestion."

**Staff**: "BigQuery cost runaway — investigate."

## Next Topic

→ Move to [L07/C07 — Cloud Networking Primitives](../C07/README.md)
