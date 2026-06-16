# L07/C06 — Database Family

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Managed-Relational.md) | Managed Relational (RDS, Cloud SQL, Azure SQL) | 1 hr |
| [T02](T02-Managed-NoSQL.md) | Managed NoSQL (DynamoDB, Firestore, Cosmos DB) | 1 hr |
| [T03](T03-Managed-Caches.md) | Managed Caches (ElastiCache, Memorystore) | 0.5 hr |
| [T04](T04-Data-Warehouses.md) | Data Warehouses (Redshift, BigQuery, Synapse) | 1 hr |

## Relational Managed Services

### AWS RDS
- Supports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server
- Multi-AZ for HA (sync replication, automatic failover)
- Read replicas (async, cross-region possible)
- Automated backups (PITR up to 35 days)
- Maintenance windows
- Auto minor version upgrade (opt-out for safety)

### AWS Aurora
- MySQL-compatible or PostgreSQL-compatible
- Shared storage layer (6 copies across 3 AZs)
- Compute scales independently
- Aurora Serverless v2 — auto-scale ACU (Aurora Capacity Units)
- Global Database for cross-region replication (<1 sec lag)
- Read replicas can become writers on failover

### GCP Cloud SQL / Spanner
- Cloud SQL: MySQL/Postgres/SQL Server (similar to RDS)
- **Spanner**: globally distributed ACID SQL — unique offering
- AlloyDB (newer, Postgres-compatible, PG-superset)

### Azure SQL Database / Managed Instance
- SQL Database — PaaS
- Managed Instance — closer to on-prem SQL Server semantics
- Hyperscale tier — Aurora-like architecture

### When NOT Managed
- Need plugins/extensions not supported (e.g., specific PostgreSQL extensions)
- Need superuser
- Cost-sensitive at extreme scale
- Lock-in concern

## NoSQL Managed Services

### DynamoDB
- Key-value + document
- Single-digit-ms read/write at any scale
- On-demand or provisioned capacity
- Global Tables (multi-region, multi-active)
- Streams for CDC
- DAX (in-memory cache)
- Design constraint: query patterns drive schema (no joins)

### Cosmos DB (Azure)
- Multi-model: NoSQL, MongoDB, Cassandra, Gremlin, Table
- Multi-region writes
- 5 consistency levels (strong → eventual)
- Pricing via Request Units (RU)

### Firestore / Datastore (GCP)
- Document
- Real-time sync (mobile-focused)
- ACID transactions
- Native + Datastore modes

### Cassandra / Bigtable (GCP)
- Wide-column
- Petabyte-scale
- Tunable consistency

## Managed Caches

### ElastiCache (AWS)
- Redis or Memcached
- Multi-AZ HA
- Cluster mode for Redis (sharding)
- Pub/sub, streams

### Memorystore (GCP)
- Redis or Memcached
- Standard tier = HA

### Azure Cache for Redis
- Tiers: Basic, Standard, Premium, Enterprise

### Considerations
- Eviction policy (allkeys-lru common for caches)
- Persistence (AOF/RDB)
- Networking (in-VPC for private)
- Max memory and node count

## Data Warehouses

### Redshift (AWS)
- Column store
- MPP (massively parallel)
- RA3 nodes separate compute/storage (S3-backed)
- Redshift Serverless (no cluster management)

### BigQuery (GCP)
- Serverless data warehouse
- Pay per query (TB scanned) or flat-rate slots
- Petabyte scale, sub-minute queries
- Auto-scaling, no infra
- Federated queries (S3, Sheets, etc.)

### Snowflake (cloud-agnostic)
- Multi-cloud (AWS, Azure, GCP)
- Separate compute (warehouses) and storage
- Per-second billing
- Massive adoption

### Synapse (Azure)
- Combined data warehouse + Spark + serverless SQL

## Choosing a Database (Cheat Sheet)

| Need | Pick |
|---|---|
| Transactional, relational, < 50TB | Postgres (RDS or Cloud SQL or Aurora) |
| Global ACID SQL | Spanner / CockroachDB |
| Sub-ms KV at scale | DynamoDB / Bigtable |
| Document with sync | Firestore / MongoDB Atlas |
| Wide-column | Cassandra / Bigtable |
| Cache | Redis (ElastiCache / Memorystore) |
| Analytics | BigQuery / Snowflake / Redshift |
| Time series | Timestream / InfluxDB / TimescaleDB |
| Search | Elasticsearch / OpenSearch |
| Graph | Neptune / Cosmos DB Gremlin |

## Production Operations

- Always enable: backups, encryption, multi-AZ
- Right-size memory (most DB tuning is memory and indexes)
- Monitor: connections, slow queries, replication lag, IOPS
- Tune connection pooling (RDS Proxy, PgBouncer)
- Test restores quarterly

## Interview Themes

- "Choose a DB for a use case"
- "Aurora vs RDS — what's different?"
- "When DynamoDB over RDS?"
- "How does Spanner achieve global ACID?"
- "BigQuery vs Redshift vs Snowflake"
