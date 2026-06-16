# L21/C08 — Data Pipelines & ETL

## Topics

- **T01 Airflow, Dagster, Prefect** — Workflow orchestrators
- **T02 dbt for Analytics Engineering** — SQL-driven transformations
- **T03 CDC (Debezium)** — Change Data Capture

## Why Data Pipelines

DevOps engineers increasingly own data pipelines:
- ETL/ELT (Extract, Transform, Load)
- Reporting + analytics
- ML training data
- Real-time streaming
- Event-driven workflows

The tools below are essential.

## Apache Airflow

The dominant workflow orchestrator. Python-based DAGs.

```python
from airflow import DAG
from airflow.decorators import task
from datetime import datetime

with DAG('daily_etl', start_date=datetime(2026, 1, 1), schedule='@daily') as dag:
    
    @task
    def extract():
        # pull from source
        return data
    
    @task
    def transform(data):
        # transform
        return cleaned
    
    @task
    def load(cleaned):
        # write to warehouse
        pass
    
    load(transform(extract()))
```

### Concepts
- **DAG**: directed acyclic graph of tasks
- **Operator**: built-in or custom (BashOperator, PythonOperator, KubernetesPodOperator)
- **Scheduler**: triggers DAG runs based on schedule
- **Executor**: runs tasks (LocalExecutor, CeleryExecutor, KubernetesExecutor)
- **Connection**: external system config (S3, Snowflake, etc.)

### Scaling
- Use KubernetesExecutor — one pod per task
- Avoid Airflow for sub-minute scheduling (overhead too high)
- Avoid Airflow for tight data dependencies between tasks (use Dagster)

### Operations
- Webserver, Scheduler, Triggerer (async tasks), Workers
- Backed by Postgres
- Helm chart for K8s install

## Dagster

Modern competitor. Software-engineering-first.

### Concepts
- **Asset**: data thing (table, file, ML model); declarative dependency
- **Op**: operation
- **Job**: orchestration unit
- **Sensor / Schedule**: triggers

```python
from dagster import asset

@asset
def raw_orders():
    return query_db()

@asset
def cleaned_orders(raw_orders):
    return clean(raw_orders)

@asset
def daily_report(cleaned_orders):
    return summarize(cleaned_orders)
```

Dagster materializes assets and tracks dependencies. Better lineage than Airflow.

### Why Dagster
- Type-aware assets
- Better local dev (no Airflow webserver needed)
- Native support for dbt, pandas, ML frameworks
- Modern API

## Prefect

Another orchestrator. Python-first. Smaller community than Airflow but well-designed.

```python
from prefect import flow, task

@task
def extract(): ...

@task
def transform(data): ...

@flow
def pipeline():
    data = extract()
    return transform(data)
```

## dbt (data build tool)

Transformations as SQL + Jinja, version-controlled, tested.

```sql
-- models/staging/stg_orders.sql
SELECT
  id,
  user_id,
  amount_cents / 100.0 AS amount_dollars,
  status
FROM {{ source('raw', 'orders') }}
WHERE status != 'deleted'
```

```sql
-- models/marts/daily_revenue.sql
SELECT
  DATE(created_at) AS date,
  SUM(amount_dollars) AS revenue
FROM {{ ref('stg_orders') }}
GROUP BY 1
```

Run:
```bash
dbt run
dbt test
dbt docs generate
```

### Why dbt
- Pure SQL (analysts can write)
- Version control + PR review
- Tests as code (`uniqueness`, `not_null`, custom)
- Lineage graph + docs auto-generated
- Modular (refs to other models)
- Incremental models (only process new rows)

### dbt Cloud vs Core
- Core: OSS CLI
- Cloud: SaaS with web IDE, scheduling, alerts

### Architecture
- dbt runs SQL inside the warehouse (BigQuery, Snowflake, Redshift, Postgres)
- No data leaves warehouse
- Each model = a SELECT that creates a table/view

## CDC (Change Data Capture)

Stream changes from operational DB to downstream (warehouse, search, cache).

### Why
- Keep warehouse in near-real-time sync
- Build event streams from DB writes
- Avoid full table dumps

### Debezium
Read DB transaction log (binlog, WAL) → emit Kafka events.

```
[Postgres / MySQL / MongoDB]
   ↓ binlog/WAL/oplog
[Debezium Connector]
   ↓
[Kafka topic per table]
   ↓
[Consumer apps; warehouse loader; cache invalidator]
```

### Postgres CDC
- Logical decoding via `wal2json` or `pgoutput`
- Replication slot per consumer
- Debezium handles the heavy lifting

### Snapshot + Stream
- Initial: full table snapshot
- Then: incremental via WAL/binlog

### Use Cases
- Warehouse ingestion (near-real-time)
- Search index updates (Elasticsearch)
- Cache invalidation (Redis)
- Event-driven downstream services
- Audit log

### Alternatives
- **Maxwell** (MySQL specific)
- **AWS DMS** (managed)
- **GCP Datastream**

## Modern Data Stack

```
Sources (Postgres, MySQL, MongoDB, APIs, files)
   ↓ Extract+Load (Airbyte, Fivetran, Debezium)
Warehouse (Snowflake, BigQuery, Redshift)
   ↓ Transform (dbt)
Marts (cleaned, business-friendly)
   ↓ BI (Looker, Tableau, Metabase)
Dashboards
```

Orchestrator (Airflow / Dagster) controls EL + Transform.

## Streaming Pipelines

For real-time:
- Kafka / Kinesis / Pub/Sub for ingestion
- Flink / Spark Streaming for processing
- Materialize / RisingWave (streaming SQL)
- Sink to OLAP (BigQuery, ClickHouse, Druid)

Lower latency, harder to operate. Use when batch SLAs unacceptable.

## DevOps Concerns

- Schedule reliability (Airflow scheduler crashing)
- Idempotency (re-running shouldn't double-write)
- Backfill capability
- Monitoring (job durations, success rates, freshness of outputs)
- Cost (compute, warehouse query costs)
- Lineage (what depends on what)

## Interview Themes

- "Choose Airflow vs Dagster"
- "What is dbt and why?"
- "CDC — explain via Debezium"
- "Streaming vs batch — when each?"
- "Modern data stack — components"
