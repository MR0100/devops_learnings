# L21/C08/T01 — Airflow, Dagster, Prefect

## Learning Objectives

- Use workflow orchestrators
- Choose tool

## Why

Data pipelines:
- Extract from sources
- Transform
- Load to target

Need: scheduling, retries, monitoring.

## Airflow

Apache; most popular:
- DAG-based
- Python
- Web UI
- Mature

## DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG('my_dag', start_date=datetime(2026,1,1), schedule='@daily') as dag:
    extract = PythonOperator(task_id='extract', python_callable=extract_fn)
    transform = PythonOperator(task_id='transform', python_callable=transform_fn)
    load = PythonOperator(task_id='load', python_callable=load_fn)
    
    extract >> transform >> load
```

## Components

- Scheduler
- Workers (Celery, K8s)
- Webserver
- Metadata DB

## Operators

- PythonOperator
- BashOperator
- SQLOperator
- S3, GCS, Snowflake, BigQuery
- Hundreds

## Executor

- LocalExecutor (single host)
- CeleryExecutor (worker pool)
- KubernetesExecutor (pod per task)

For K8s: native.

## Dagster

Modern; asset-centric:
```python
from dagster import asset

@asset
def raw_users():
    return fetch_users()

@asset
def clean_users(raw_users):
    return process(raw_users)
```

For: data-centric thinking.

Pros:
- Type checking
- Asset materializations
- Better testing

## Prefect

Cloud-native:
```python
from prefect import flow, task

@task
def extract(): return ...

@flow
def my_flow():
    data = extract()
```

Pros:
- Simpler API
- Hybrid execution (cloud orchestration, on-prem workers)

## Compared

| | Airflow | Dagster | Prefect |
|---|---|---|---|
| Origin | Airbnb (2014) | Elementl (2018) | Prefect (2019) |
| Model | DAG | Asset | Flow |
| Maturity | high | growing | growing |
| Cloud | self / managed | self / managed | Cloud + agents |

## Managed Options

- AWS MWAA (Airflow)
- GCP Cloud Composer (Airflow)
- Astronomer (Airflow)
- Dagster Cloud
- Prefect Cloud

For: avoid ops.

## Common Tasks

- ETL nightly
- ML training pipelines
- Report generation
- Data quality checks

## Best Practices

- Idempotent tasks
- Retries
- Alerts on failure
- Catchup awareness (Airflow)
- Backfill capability
- Test in dev

## Common Mistakes

- Non-idempotent (rerun breaks)
- Long-running tasks (timeouts)
- Tight coupling (one fail blocks all)

## Migration

Many migrating Airflow → Dagster / Prefect for better DX.

## Quick Refs

```bash
# Airflow
airflow dags list
airflow tasks test DAG_ID TASK_ID DATE
airflow webserver / scheduler

# Dagster
dagster dev
dagster job execute -j JOB

# Prefect
prefect deployment build
prefect agent start
```

## Interview Prep

**Mid**: "Workflow orchestrator."

**Senior**: "Airflow vs Dagster."

**Staff**: "Data platform."

## Next Topic

→ [T02 — dbt](T02-dbt.md)
