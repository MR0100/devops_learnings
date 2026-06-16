# L21 — Databases & Data Management for DevOps

## Overview

Databases are the highest-risk part of any system. DevOps engineers operate them in production. This lecture covers operations, replication, backup/recovery, and migrations.

**8 chapters, 29 topics.**

## Chapter Map

### [C01](C01/) — Database Categories
- T01 OLTP vs OLAP
- T02 Row vs Column Storage
- T03 SQL vs NoSQL vs NewSQL

### [C02](C02/) — PostgreSQL for SREs
- T01 MVCC, Vacuum, Autovacuum
- T02 Replication (Streaming, Logical)
- T03 Connection Pooling (PgBouncer)
- T04 Backup (pg_dump, pg_basebackup, WAL-G)
- T05 Performance Tuning
- T06 Transaction Isolation Levels
- T07 Indexing Strategies

### [C03](C03/) — MySQL for SREs
- T01 InnoDB Internals
- T02 Replication (Async, Semi-Sync, Group)
- T03 ProxySQL
- T04 Backup (mysqldump, Percona XtraBackup)

### [C04](C04/) — NoSQL Operations
- T01 DynamoDB Operations
- T02 MongoDB (Replica Sets, Sharding)
- T03 Cassandra (Tunable Consistency)
- T04 Redis (Sentinel, Cluster)

### [C05](C05/) — Database Migrations
- T01 Schema Migration Tools (Flyway, Liquibase, Atlas)
- T02 Online Schema Changes (gh-ost, pt-online-schema-change)
- T03 Zero-Downtime Migration Patterns

### [C06](C06/) — Backups & DR
- T01 RPO & RTO for Databases
- T02 Point-in-Time Recovery
- T03 Cross-Region Replication
- T04 Restoring Without Crying

### [C07](C07/) — Database Observability
- T01 Slow Query Logs
- T02 EXPLAIN ANALYZE Mastery
- T03 pg_stat_statements, performance_schema

### [C08](C08/) — Data Pipelines & ETL
- T01 Airflow, Dagster, Prefect
- T02 dbt for Analytics Engineering
- T03 CDC (Debezium)

## Database Selection

| Workload | Pick |
|---|---|
| Transactional, relational | PostgreSQL > MySQL |
| High-write key-value | DynamoDB / Cassandra |
| Hierarchical / document | MongoDB / DynamoDB |
| Wide-column, big data | Cassandra / Bigtable |
| Time series | TimescaleDB / InfluxDB |
| Cache | Redis / Memcached |
| Graph | Neo4j / DGraph |
| Search | Elasticsearch / OpenSearch |
| Analytics | Snowflake / BigQuery / Redshift / ClickHouse |
| Global ACID SQL | Spanner / CockroachDB |

## PostgreSQL Production Knobs

```
shared_buffers = 25% of RAM
effective_cache_size = 75% of RAM
maintenance_work_mem = 256MB to 2GB
work_mem = 4MB to 64MB (per operation, careful)
wal_compression = on
max_connections = small (use pooler)
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
autovacuum_naptime = 10s (under high write load)
log_min_duration_statement = 1000  # log queries > 1s
```

## Zero-Downtime Schema Migration

Standard playbook (expand-contract):

1. **Expand** — add new column nullable
2. Deploy app that reads both old + new, writes both
3. Backfill new column
4. Deploy app that reads new, writes both
5. Deploy app that reads new, writes new only
6. **Contract** — drop old column

## RPO / RTO

- **RPO** (Recovery Point Objective): how much data can you lose
- **RTO** (Recovery Time Objective): how long to restore

For Postgres with WAL-G archiving to S3:
- RPO: ~1 minute (archive interval)
- RTO: minutes to hours (depending on database size)

## Connection Pooling

DBs handle limited concurrent connections. App → pooler → DB:
- Postgres: PgBouncer (transaction or statement pooling)
- MySQL: ProxySQL
- Cloud: RDS Proxy, AWS DataAPI for Aurora Serverless

## Recommended Reading

- *Designing Data-Intensive Applications* — Martin Kleppmann (mandatory)
- *Database Reliability Engineering* — Campbell & Majors
- *PostgreSQL High Performance* — Smith
- *MySQL High Availability* — Henrik Ingo

## Interview Themes

- "Walk me through Postgres MVCC"
- "Zero-downtime schema change — how?"
- "RPO/RTO for a critical database"
- "When DynamoDB over Postgres?"
- "Connection pooling — what problem does it solve?"

## Next

→ [L22 — Message Queues & Event Streaming](../L22-messaging-streaming/README.md)
