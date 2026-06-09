# L08/C06 — Databases on AWS

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-RDS.md) | RDS (MySQL, PostgreSQL, Oracle, SQL Server) | 1 hr |
| [T02](T02-Aurora.md) | Aurora Architecture (Storage Layer, Global DB) | 1.5 hr |
| [T03](T03-DynamoDB.md) | DynamoDB Deep Dive (Partition Keys, GSI, LSI) | 2 hr |
| [T04](T04-DynamoDB-Streams.md) | DynamoDB Streams & Single-Table Design | 1 hr |
| [T05](T05-ElastiCache.md) | ElastiCache (Redis & Memcached) | 1 hr |
| [T06](T06-Redshift-Athena-Glue.md) | Redshift, Athena, Glue | 1 hr |

## RDS

### Engines
MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, plus Aurora (separate).

### Features
- Automated backups (1-35 day retention)
- Point-in-time recovery (PITR) to any second
- Maintenance windows
- Auto minor version upgrade
- Multi-AZ (synchronous standby for HA)
- Read replicas (async, up to 5; cross-region possible)
- Performance Insights
- IAM database auth (no static passwords)
- Encryption at rest (KMS)
- Encryption in transit (SSL/TLS)

### Multi-AZ vs Read Replicas

| Multi-AZ | Read Replica |
|---|---|
| Sync replication | Async |
| For HA (failover ~60 sec) | For read scale + DR |
| Standby is hidden | Replica is queryable |
| Same region | Same or different region |
| One per primary | Up to 5 per primary |

A common production setup: Multi-AZ primary + 2-3 read replicas in same region + 1 cross-region.

### IAM DB Auth
- Generate short-lived auth token via STS
- 15-minute validity
- Eliminates password rotation
- Lower throughput than password auth (use connection pooler)

### RDS Proxy
Connection pooler managed by AWS:
- Reduces failover time
- Multiplexes connections
- IAM auth integration
- Especially useful for Lambda (avoid connection storms)

## Aurora

AWS-native engine, MySQL- and PostgreSQL-compatible.

### Architecture

```
[Writer]   [Reader]   [Reader]
   │          │          │
   └──────────┴──────────┘
              │
   [Shared Storage Volume]
        6 copies across 3 AZs
        (each AZ has 2 copies)
```

- Storage is decoupled from compute
- Storage auto-grows (up to 128 TB)
- Six 10-GB segments per AZ; 4-of-6 quorum for writes, 3-of-6 for reads
- Backup continuously to S3 (no backup window)
- Self-healing (replaces lost segments)

### Features
- Up to 15 read replicas (vs 5 for RDS)
- Failover ~30 sec (vs ~60 for RDS Multi-AZ)
- Global Database — cross-region replication < 1 sec
- Aurora Serverless v2 — auto-scaling ACU
- Backtrack (rewind in time, MySQL only)
- Clone (fast cow-based copy for testing)

### Aurora Global Database
```
Primary region (writer)
   └── async replication (~1 sec)
       ├── Secondary region 1 (readers, can promote)
       └── Secondary region 2 (readers, can promote)
```

Failover to secondary in minutes.

## DynamoDB Deep Dive

Single-digit-ms NoSQL at any scale.

### Concepts
- **Table**: collection of items
- **Item**: row (max 400 KB)
- **Attribute**: column (no fixed schema)
- **Primary key**: Partition key (HASH) or Partition+Sort key (composite)

### Partition Key Design
Partition key determines physical placement. Bad keys → hot partitions:
- ❌ `status` with values "active"/"inactive" (10 active : 1 inactive)
- ✅ `user_id` (uniform distribution)
- ✅ `tenant_id#user_id` (multi-tenant)

### Reads
- **Eventually Consistent** — default, cheaper, faster
- **Strongly Consistent** — 2× cost, 2× latency
- **Transactional** — ACID, 2-4× cost

### Indexes

**Local Secondary Index (LSI)**:
- Same partition key, different sort key
- Created with table only
- 5 max per table
- Counts against table's 10GB per partition limit

**Global Secondary Index (GSI)**:
- Different partition key
- Created any time
- 20 max per table
- Separate provisioned capacity (or on-demand)
- Eventually consistent only

### Capacity Modes

**On-Demand**:
- Pay per request
- Auto-scales
- No planning needed
- 5-10× more expensive per request than well-tuned provisioned

**Provisioned**:
- Set RCU/WCU
- Auto-scaling based on utilization
- Cheaper if predictable
- Provisioned capacity is per partition: total ÷ partitions

### DAX (DynamoDB Accelerator)
- In-memory cache for DynamoDB
- ms → μs response
- Cache-aside automatic
- For read-heavy workloads

## DynamoDB Streams

CDC for DynamoDB. Each item change emits a record (24h retention).

Use cases:
- Trigger Lambda on change
- Replicate to other systems (search index, data warehouse)
- Cross-region replication (Global Tables uses streams)

## Single-Table Design

Counter-intuitive but performant: store many entity types in one DynamoDB table.

```
PK              SK              ...
USER#42         PROFILE         {name, email, ...}
USER#42         ORDER#100       {amount, status, ...}
USER#42         ORDER#101       {amount, status, ...}
ORDER#100       ITEM#A          {product, qty, ...}
```

One query gets a user and their orders. Multiple queries become one. Saves cost and latency.

Heavy upfront design; rigid afterwards. Read Alex DeBrie's *The DynamoDB Book*.

## ElastiCache

### Redis
- Single-node or Cluster mode (sharded)
- Persistence: RDB snapshots + AOF
- Multi-AZ with automatic failover (Sentinel-like)
- Up to 250 shards / 500 GB per shard
- Pub/sub, streams, Lua

### Memcached
- Pure cache (no persistence)
- Simpler, no clustering
- Cross-AZ replication minimal
- Use only for stateless cache

**Rule of thumb**: Redis unless you have a specific reason.

### Serverless ElastiCache (2023+)
- Auto-scaling capacity
- Per-second billing
- No node management
- For variable workloads

## Analytics Stack

### Redshift
- Column-store data warehouse
- Up to 100s of TB on RA3 nodes (separates compute/storage)
- Redshift Spectrum (query S3 from Redshift)
- Redshift Serverless (no cluster mgmt)

### Athena
- Serverless SQL on S3
- Per-query pricing ($5/TB scanned)
- Glue Data Catalog for metadata
- Workgroups for cost/access control
- Great for ad-hoc analysis of logs (CUR, ALB, CloudTrail)

### Glue
- ETL service
- Crawlers populate Data Catalog from S3
- Jobs in Python/Scala/Spark
- Used by Athena, Redshift Spectrum, EMR

## Interview Themes

- "Aurora vs RDS — what's the architecture difference?"
- "DynamoDB partition key design — pick a good one"
- "Single-table design — explain"
- "When DynamoDB vs RDS?"
- "Athena vs Redshift"
- "How does Aurora Global Database work?"
