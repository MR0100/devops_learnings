# L09/C04/T03 — Database Equivalents

## Learning Objectives

- Map DB services
- Choose by workload

## Relational

| Service | AWS | GCP | Azure |
|---|---|---|---|
| Managed Postgres | RDS Postgres | Cloud SQL Postgres | Azure DB for Postgres |
| Managed MySQL | RDS MySQL | Cloud SQL MySQL | Azure DB for MySQL |
| Managed SQL Server | RDS SQL Server | Cloud SQL SQL Server | Azure SQL Database |
| Managed Oracle | RDS Oracle | Cloud SQL (limited) | Oracle in Azure |
| Distributed SQL | Aurora | AlloyDB / Spanner | Cosmos DB for Postgres |
| HTAP | Aurora | AlloyDB | Cosmos DB |

## Distributed SQL (Cloud-Native)

### AWS Aurora
- Postgres / MySQL compatible
- Separate compute/storage
- Up to 128 TB
- Read replicas across AZs
- Note: Aurora is **distributed-storage, single-region** (one writer, storage spread across AZs) — not a NewSQL distributed-SQL engine with multi-region horizontal write scale like Spanner. (Aurora Global Database adds cross-region read replicas + fast failover, still single primary region.)

### GCP Spanner
- Globally distributed
- SQL + horizontal scale
- Strong consistency
- Pricey but unique

### GCP AlloyDB
- Postgres-compatible
- Analytical workloads accelerated
- HTAP

### Azure Cosmos DB for Postgres
- Citus extension
- Distributed Postgres

## NoSQL

| Service | AWS | GCP | Azure |
|---|---|---|---|
| Key-Value | DynamoDB | Cloud Bigtable / Datastore | Cosmos DB Tables |
| Document | DocumentDB / DynamoDB | Firestore | Cosmos DB SQL |
| Wide Column | DynamoDB / Keyspaces | Bigtable | Cosmos DB Cassandra |
| Graph | Neptune | (no native) | Cosmos DB Gremlin |
| Cassandra | Keyspaces | Cassandra-compatible Bigtable | Cosmos DB Cassandra |
| MongoDB | DocumentDB | Atlas / Firestore | Cosmos DB Mongo |

Note: DocumentDB is an AWS **MongoDB-API-compatible fork** (emulates the wire protocol, not actual MongoDB code) — feature/version parity lags, so verify your MongoDB version/features are supported before migrating.

## In-Memory

| | AWS | GCP | Azure |
|---|---|---|---|
| Redis | ElastiCache / MemoryDB | Memorystore Redis | Azure Cache for Redis |
| Memcached | ElastiCache Memcached | Memorystore Memcached | Azure Cache (Redis only direct) |
| Persistent | MemoryDB | (no direct) | Redis Enterprise |

## Search

| | AWS | GCP | Azure |
|---|---|---|---|
| Elasticsearch | OpenSearch | Elastic on Marketplace | Elastic on Marketplace |
| Native | OpenSearch | Cloud Search | AI Search |

Note: OpenSearch is an AWS **API-compatible fork of Elasticsearch** (forked from the Apache-2.0 7.10 line after Elastic's license change) — compatible up to that point, then diverging; newer Elasticsearch features and clients aren't guaranteed.

## Time-Series

| | AWS | GCP | Azure |
|---|---|---|---|
| Native | Timestream | Bigtable (DIY) | Azure Data Explorer (kusto) |
| InfluxDB | Self-hosted | Self-hosted | Self-hosted |
| Prometheus | AMP | GMP | Azure Monitor |

## Data Warehouse

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Redshift | BigQuery | Synapse |
| Federated | yes | yes (Omni cross-cloud) | yes |
| Serverless | Redshift Serverless | BigQuery (always) | Synapse Serverless |

For analytics: BigQuery often best per workload.

## Streaming / Event

| | AWS | GCP | Azure |
|---|---|---|---|
| Pub/Sub | SNS / EventBridge | Pub/Sub | Event Grid |
| Stream | Kinesis Data Streams | Pub/Sub + Lite | Event Hubs |
| Kafka | MSK | Managed Kafka | Event Hubs (Kafka API) / HDInsight |

## ETL / Data Pipeline

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Glue, EMR | Dataflow, Dataproc | Data Factory, Synapse Pipelines |
| Beam | yes | native (Dataflow) | self-hosted |
| Spark | EMR, Glue | Dataproc | Synapse, HDInsight |

## Aurora Internals

```
Aurora compute (writer + readers)
       ↓
Aurora storage (separate; 6 copies across 3 AZs)
```

Compute scales independently. Storage redundant.

For: high availability + scale.

## Spanner Internals

```
SQL → Tablet (data range)
     → Replicas across regions
     → Paxos for consistency
```

Global ACID transactions; strong consistency.

For: globally distributed SQL.

## Cosmos DB

Multi-model:
- SQL API (document)
- MongoDB API
- Cassandra API
- Gremlin (graph)
- Tables

Globally distributed.

For: many models in one service.

## Performance

### DynamoDB
- Single-digit ms
- Massive scale
- Eventually or strongly consistent

### Spanner
- Few-ms reads (local)
- Strong global consistency
- Premium pricing

### Bigtable
- ms read/write
- Petabyte scale
- Sorted keys

### Redis
- Sub-ms
- In-memory
- Persistence optional

## Cost Models

- DynamoDB: on-demand (per request) or provisioned (RCU/WCU)
- Bigtable: per node-hour + storage
- Spanner: per node + storage
- Redis: per VM hour
- RDS: per VM hour + storage
- BigQuery: per query (on-demand) or slot reservation

## Choosing

### OLTP small
RDS / Cloud SQL / Azure DB.

### OLTP large
Aurora / AlloyDB / Cosmos for Postgres.

### Global OLTP
Spanner.

### NoSQL KV
DynamoDB / Bigtable / Cosmos.

### Document
DynamoDB / Firestore / Cosmos.

### Analytics
Redshift / BigQuery / Synapse.

### Time-series
Timestream / Bigtable / ADX.

### Search
OpenSearch / Elastic / AI Search.

### Cache
ElastiCache / Memorystore / Azure Cache.

## Migration

### To Cloud
- DMS (AWS) / DMS (GCP) / Azure DMS
- Heterogeneous (Oracle → Postgres)

### Cross-Cloud
- Logical replication
- Snapshot + restore
- Bespoke ETL

## HA

| | AWS | GCP | Azure |
|---|---|---|---|
| Multi-AZ | yes (Multi-AZ deploy) | yes (HA config) | yes (Zone-redundant) |
| Multi-region | Aurora Global, DynamoDB Global | Spanner, Bigtable | Cosmos, Hyperscale |
| Read replicas | yes | yes | yes |

## Backup

All: automated backups + point-in-time recovery.
Cross-region: usually opt-in.

For RPO=0: ongoing replication.

## Best Practices

- Right-size DB (autoscale where possible)
- Read replicas for analytics off OLTP
- Backup tested
- Multi-AZ for prod
- Encryption with CMK if regulated
- Connection pooling

## Common Mistakes

- Cross-cloud DB (latency + egress)
- Self-hosted DB on cloud VM when managed available
- No read replicas (hot OLTP master)
- No backup test (untested = no backup)
- Public DB endpoints (use VPC)

## Quick Refs

```
OLTP: RDS / Cloud SQL / Azure DB
Distributed OLTP: Aurora / Spanner / Cosmos
NoSQL: DynamoDB / Bigtable / Cosmos
Cache: ElastiCache / Memorystore / Azure Cache
Search: OpenSearch / Elastic / AI Search
DW: Redshift / BigQuery / Synapse
```

## Interview Prep

**Junior**: "Map DBs."

**Mid**: "When each type."

**Senior**: "Distributed SQL options."

**Staff**: "Multi-region DB strategy."

## Next Topic

→ [T04 — Networking Equivalents](T04-Networking-Equivalents.md)
