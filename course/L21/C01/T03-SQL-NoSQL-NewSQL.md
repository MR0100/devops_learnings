# L21/C01/T03 — SQL vs NoSQL vs NewSQL

## Learning Objectives

- Categorize databases
- Pick by need

## SQL (Relational)

ACID:
- PostgreSQL, MySQL, Oracle
- Strong consistency
- Schemas
- Joins
- Mature

## NoSQL

Various models:
- Document (Mongo, Firestore)
- Key-value (Redis, DynamoDB)
- Wide-column (Cassandra, Bigtable)
- Graph (Neo4j, Neptune)

## NewSQL

Combine SQL + scale:
- Spanner
- CockroachDB
- TiDB
- YugabyteDB

Distributed SQL.

## CAP Theorem

Pick 2 of 3:
- Consistency
- Availability
- Partition tolerance

In distributed systems: partition tolerance required. So: CP or AP.

## CP

- Strong consistency
- Lower availability during partition

E.g.: Spanner (with paxos).

## AP

- High availability
- Eventual consistency

E.g.: Cassandra, DynamoDB.

## When SQL

- Strong consistency
- Complex queries (joins)
- Mature operations
- ACID transactions
- Small-medium scale

For: most apps.

## When NoSQL

### Document
- Flexible schema
- Hierarchical data
- Read-heavy

### Key-Value
- Sessions
- Cache
- Simple lookups

### Wide-Column
- Time-series
- Huge scale
- Write-heavy

### Graph
- Social networks
- Recommendations
- Fraud detection

## When NewSQL

- SQL + horizontal scale
- Global distribution
- Strong consistency at scale

Premium cost.

## Examples

### Postgres
General OLTP. Most apps.

### MySQL
Web, simple.

### DynamoDB
Key-value at scale; AWS.

### Cassandra
Time-series, high write.

### MongoDB
Document; flexible schema.

### Spanner
Global SQL with strong consistency.

### CockroachDB
Open-source Spanner-like.

## Choosing

```
Standard CRUD: Postgres / MySQL
High writes (millions): Cassandra / Bigtable
Document model: Mongo / Firestore / Cosmos
Key-value: DynamoDB / Redis
Global SQL: Spanner / Cockroach
Analytics: BigQuery / Snowflake / Redshift
Graph: Neo4j / Neptune
```

## Schema

### SQL
Defined upfront. Migrations.

### NoSQL
Flexible. Per-document.

### NewSQL
SQL schema; distributed under hood.

## Joins

### SQL / NewSQL
Yes. Powerful.

### NoSQL
Limited. Denormalize.

## ACID

### SQL / NewSQL
Yes.

### Some NoSQL
- DynamoDB: limited transactions
- Mongo: transactions in modern versions
- Cassandra: eventually consistent

## Operations

### SQL
Mature. Many tools.

### NoSQL
Per-product. Some mature (DynamoDB managed).

### NewSQL
Newer; less ops tooling.

## Migration Risk

Schema changes:
- SQL: explicit
- NoSQL: implicit (app-defined)
- NewSQL: SQL-style

For: trade-off.

## Multi-Region

- SQL: difficult (CockroachDB exception)
- NoSQL: many built-in
- NewSQL: built-in

## Cost

- Managed SQL: per instance
- DynamoDB: per request
- Spanner: per node
- BigQuery: per query or slot

Varies.

## Compatibility

Wire protocols:
- Postgres: many tools
- MySQL: huge ecosystem
- DynamoDB: AWS SDK
- Mongo: drivers per language

## Decision Tree

```
Single region + < 10 TB? → Postgres
Need global SQL? → Spanner / Cockroach
Document model? → Mongo / Firestore
Key-value? → DynamoDB / Redis
Time-series? → InfluxDB / TimescaleDB
Analytics? → BigQuery
Cache? → Redis
```

## Hybrid

Often combine:
- Postgres for transactions
- Redis for cache
- BigQuery for analytics
- Elasticsearch for search

## Best Practices

- Pick by access pattern
- Multi-DB OK
- Test at scale
- Operations matter (managed)

## Common Mistakes

- NoSQL for relational data (joins emerge)
- SQL for massive scale (limits)
- Single DB for everything (wrong tool somewhere)

## Quick Refs

```
SQL:    Postgres, MySQL
NoSQL:  
  Doc: Mongo
  KV:  DynamoDB / Redis
  WC:  Cassandra
  Graph: Neo4j
NewSQL: Spanner, Cockroach

CAP: CP or AP
ACID: SQL strong; NoSQL varies
```

## Interview Prep

**Junior**: "SQL vs NoSQL."

**Mid**: "Pick DB."

**Senior**: "NewSQL niche."

## Next Topic

→ Move to [L21/C02 — PostgreSQL for SREs](../C02/README.md)
