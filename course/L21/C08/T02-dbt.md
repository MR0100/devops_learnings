# L21/C08/T02 — dbt for Analytics Engineering

## Learning Objectives

- Use dbt
- SQL-driven ETL

## dbt

Data build tool:
- SQL-based transformations
- Run on warehouse (BigQuery, Snowflake, Redshift)
- Version controlled
- Test built-in

For: T in ELT.

## ELT

Old: ETL (transform before load).
New: ELT (load raw, transform in warehouse).

For: more compute available.

## Model

```sql
-- models/clean_users.sql
{{ config(materialized='table') }}

SELECT 
  id,
  LOWER(email) AS email,
  COALESCE(name, 'unknown') AS name
FROM {{ ref('raw_users') }}
WHERE created_at > '2024-01-01'
```

## Materialization

- view: SQL view
- table: full table (rebuild)
- incremental: append/update
- ephemeral: CTE

```sql
{{ config(materialized='incremental', unique_key='id') }}

SELECT * FROM {{ ref('raw_events') }}
{% if is_incremental() %}
WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

For: efficiency.

## ref()

```sql
SELECT * FROM {{ ref('other_model') }}
```

References other model. Generates dependency graph.

## source()

```yaml
# schema.yml
sources:
  - name: raw
    tables:
      - name: users
```

```sql
SELECT * FROM {{ source('raw', 'users') }}
```

## Tests

```yaml
# schema.yml
models:
  - name: clean_users
    columns:
      - name: id
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - not_null
```

```bash
dbt test
```

For: data quality.

## Custom Tests

```sql
-- tests/no_negative_amounts.sql
SELECT * FROM {{ ref('orders') }} WHERE amount < 0
```

If returns rows: fail.

## Documentation

```yaml
models:
  - name: clean_users
    description: Cleaned user data
    columns:
      - name: id
        description: User ID
```

```bash
dbt docs generate
dbt docs serve
```

For: auto-doc data lineage.

## Macros

```sql
-- macros/clean_email.sql
{% macro clean_email(col) %}
  LOWER(TRIM({{ col }}))
{% endmacro %}
```

Use:
```sql
SELECT {{ clean_email('email') }} FROM users
```

## Packages

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.0.0
```

```bash
dbt deps
```

Many community packages.

## Run

```bash
dbt run
dbt test
dbt run --select model_a model_b
dbt run --select +my_model   # upstream
dbt run --select my_model+   # downstream
```

## Orchestration

Run via:
- Airflow / Dagster / Prefect
- dbt Cloud
- GitHub Actions

```yaml
- name: dbt run
  run: |
    dbt deps
    dbt run
    dbt test
```

## Modern Data Stack

```
Source (DB, API, files)
   ↓ Fivetran / Airbyte
Warehouse (BigQuery, Snowflake)
   ↓ dbt
Marts
   ↓ Looker / Tableau / Hex
Dashboards
```

For: SaaS standard.

## When dbt

- Have warehouse (BigQuery / Snowflake)
- SQL-fluent team
- Want versioned transforms
- Need data tests

## Best Practices

- One model per concern
- Tests for keys
- Documentation
- Incremental for huge
- CI/CD

## Common Mistakes

- Monolithic models
- No tests
- No docs
- Full refresh huge (use incremental)

## Quick Refs

```bash
dbt init
dbt run / test / docs generate
dbt run --select +model+
dbt build   # run + test
```

## Interview Prep

**Mid**: "What's dbt."

**Senior**: "dbt + warehouse."

**Staff**: "Modern data stack."

## Next Topic

→ [T03 — CDC (Debezium)](T03-CDC-Debezium.md)
