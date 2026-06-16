# L08/C06/T06 — Redshift, Athena, Glue

## Learning Objectives

- Pick analytics service
- Use Athena on S3

## Redshift

Columnar MPP data warehouse.

Variants:
- **Provisioned**: pick node type + count
- **Serverless**: auto-scale RPU (Redshift Processing Units); pay per use

Nodes:
- ra3.xlplus: 4 vCPU, 32 GB, managed storage
- ra3.4xlarge: 12 vCPU, 96 GB
- ra3.16xlarge: 48 vCPU, 384 GB

## Architecture

- Leader node: query parsing, plan
- Compute nodes: execute slices
- Managed storage (S3-backed; cache locally)

Columnar; compressed; sort key + distribution key.

## Loading Data

```sql
COPY my_table FROM 's3://bucket/data/' 
IAM_ROLE 'arn:aws:iam::123:role/RedshiftRole'
FORMAT AS PARQUET;
```

For bulk: COPY (parallel; fast).
For incremental: streaming ingest (Kinesis Firehose / direct).

## Sort Key + Dist Key

- Sort Key: data sorted on disk; fast range queries
- Dist Key: distribute data; co-locate join keys

Get right: 10× perf. Wrong: scan all nodes.

Typical:
- Sort: timestamp (range queries)
- Dist: customer_id (joins on customer)

## Concurrency Scaling

Spin up read clusters during peak; pay per use.

Auto-add for read concurrency.

## Materialized Views

Pre-computed query results:
```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT date, SUM(amount) FROM orders GROUP BY date;
```

Refresh on schedule or incrementally.

## Spectrum

Query S3 directly from Redshift (federated):
```sql
SELECT * FROM redshift_table r JOIN s3_external_table s ON r.id = s.id;
```

Lake + Warehouse together.

## Performance Tuning

- Sort / dist key choice
- VACUUM (reclaim space, sort)
- ANALYZE (update stats)
- WLM (workload management) queues
- Result cache
- Query Editor v2 for analysis

## Athena

Serverless SQL on S3. No clusters; pay per scan.

```sql
SELECT date, COUNT(*) FROM logs WHERE region = 'us-east-1' GROUP BY date;
```

Underlying: Presto / Trino.

## Pricing

$5 per TB scanned. One badly-written query: $$$.

Mitigate:
- Partition data
- Columnar format (Parquet, ORC)
- Compress
- LIMIT in dev

## Setup

1. Data in S3 (Parquet preferred)
2. Register table via Glue catalog
3. Query via Athena console / CLI / JDBC

```sql
CREATE EXTERNAL TABLE logs (
  timestamp string,
  level string,
  message string
)
PARTITIONED BY (date string)
STORED AS PARQUET
LOCATION 's3://my-bucket/logs/';
```

## Partitions

Hugely important for cost:
```
s3://bucket/logs/date=2024-06-09/file.parquet
s3://bucket/logs/date=2024-06-10/file.parquet
```

Athena scans only partitions matched by WHERE:
```sql
SELECT * FROM logs WHERE date = '2024-06-09';
```

Reduces scan from TB to GB.

## Partition Projection

Avoid Glue catalog metadata overhead:
```sql
CREATE TABLE ... TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.date.type' = 'date',
  'projection.date.range' = '2020-01-01,NOW',
  'projection.date.format' = 'yyyy-MM-dd'
)
```

Athena computes partitions on-the-fly.

## Compression / Format

Parquet > ORC > Avro > JSON > CSV (in compression + perf).

For new data: Parquet always.
GZIP / Snappy compression.

## Glue Catalog

Central metadata for S3 datasets:
- Tables (schemas)
- Partitions
- Database (namespace)

Used by Athena, Redshift Spectrum, EMR.

## Glue ETL

Serverless Spark for ETL:
- Job authoring (Studio / code)
- Pay per DPU-hour
- Triggers (schedule, event-based)
- Crawlers (auto-discover schema)

For complex ETL: Glue or EMR (more flexibility).

## Crawler

Auto-discovers S3 schema:
- Scans S3 prefix
- Infers schema
- Creates / updates Glue table

Run on schedule for evolving data.

## Athena vs Redshift

| | Athena | Redshift |
|---|---|---|
| Setup | None | Cluster |
| Cost | Per query | Hourly |
| Latency | Seconds-minutes | Sub-second to seconds |
| Concurrency | Limited | Better |
| Workload | Ad-hoc | BI dashboards |
| Cost (heavy) | Expensive | Cheaper |
| Cost (light) | Cheap | Wasted |

Heuristic:
- Sporadic queries: Athena
- Steady BI workload: Redshift

Many use both.

## EMR

Managed Hadoop / Spark:
- For: big data ETL, ML training, custom processing
- Cluster of EC2; charge instance hours

For Spark: EMR (or Glue for simpler).

For new: prefer Glue serverless or EMR Serverless.

## OpenSearch

Managed Elasticsearch for log search.

For:
- Log search
- Real-time search
- Aggregations

Costs: cluster hours.

## Kinesis Family

- Data Streams: stream of records; sub-sec; partitioned
- Firehose: deliver to S3 / Redshift / OpenSearch; managed
- Analytics: SQL on streams (legacy; superseded)
- Video Streams

For real-time ingestion to lake:
```
App → Kinesis Firehose → S3 → Athena/Redshift
```

Firehose batches; Parquet conversion; partitions by date.

## MSK (Kafka)

Managed Apache Kafka. For event-driven, high-throughput streaming.

## Quicksight

BI dashboards. Connects to Redshift / Athena / RDS. Self-service viz.

Cost: per session / per user.

## Lake Formation

Permissions + governance over data lake:
- Tag-based access
- Cell-level filtering
- Audit
- Cross-account

For data sharing at scale.

## When Each

### Athena
- Ad-hoc analytics
- Log analysis
- One-off queries
- Schema-on-read

### Redshift
- Steady BI dashboards
- Materialized views
- Complex joins frequently

### Glue
- Scheduled ETL
- Spark / Python jobs
- Schema discovery

### EMR
- Custom Spark / Hadoop
- ML pipelines

### OpenSearch
- Log search
- Full-text search

### Kinesis / Firehose
- Streaming ingestion

## Lake Architecture

```
Apps → Kinesis Firehose → S3 (Parquet, partitioned by date)
                              ↓
                        Glue Catalog
                              ↓
              Athena (ad-hoc) + Redshift Spectrum (BI)
                              ↓
                          QuickSight
```

## Common Mistakes

- `SELECT *` on huge table
- No partitions (full scan)
- CSV instead of Parquet
- Athena for real-time (it's not)
- Redshift for ad-hoc only (overkill)
- No data quality

## Best Practices

- Parquet everywhere
- Partition by date / commonly-filtered
- Compress (Snappy)
- Materialize for repeated queries
- Lifecycle for cold data
- Catalog with Glue
- Monitor cost per query

## Cost Optimization

- Partitions for selectivity
- Parquet
- Limit columns (`SELECT name, age` not `*`)
- Athena workgroups (query limits)
- Redshift reserved instances
- Right-size cluster

## Quick Refs

```bash
# Athena query
aws athena start-query-execution \
  --query-string "SELECT * FROM logs WHERE date='2024-06-09'" \
  --result-configuration "OutputLocation=s3://results/"

# Glue crawler
aws glue start-crawler --name my-crawler

# Redshift cluster
aws redshift create-cluster --cluster-identifier mycluster --node-type ra3.xlplus --number-of-nodes 2 --master-username admin --master-user-password '...'
```

## Interview Prep

**Mid**: "Athena vs Redshift."

**Senior**: "Cost-optimize $10k/mo Athena."

**Staff**: "Lakehouse architecture."

## Next Topic

→ Move to [L08/C07 — Messaging Services](../C07/README.md)
