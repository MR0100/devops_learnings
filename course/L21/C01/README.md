# L21/C01 — Database Categories

## Topics

- **T01 OLTP vs OLAP** — Transactional vs analytical workloads
- **T02 Row vs Column Storage** — Physical layout impact
- **T03 SQL vs NoSQL vs NewSQL** — When each fits

## OLTP vs OLAP

### OLTP (Online Transaction Processing)
- Many small fast transactions (10K-100K TPS)
- Read + write
- Rows touched: few per query
- Examples: e-commerce orders, user profiles, banking
- Databases: PostgreSQL, MySQL, DynamoDB, Spanner, MongoDB

### OLAP (Online Analytical Processing)
- Fewer huge queries
- Mostly read (writes are batch loads)
- Rows scanned: millions+
- Examples: business intelligence, reporting, ad-hoc analysis
- Databases: Redshift, BigQuery, Snowflake, ClickHouse, Druid

### HTAP (Hybrid Transactional/Analytical)
- One DB serves both workloads
- Examples: SingleStore (MemSQL), TiDB, Spanner+BigQuery integration

Used to be "separate ETL to warehouse"; now sometimes "same DB" or near-real-time replication.

## Row vs Column

### Row Storage
```
[id=1, name=Alice, email=a@x, age=30] ← row 1
[id=2, name=Bob,   email=b@x, age=25] ← row 2
...
```

Read a row: cheap (one disk read).
Read a column across rows: expensive (read every row).
Good for: OLTP (read/write specific records).

### Column Storage
```
ids:    [1, 2, 3, 4, 5, ...]
names:  [Alice, Bob, Carol, ...]
emails: [a@x, b@x, c@x, ...]
ages:   [30, 25, 28, ...]
```

Read a column: cheap (sequential).
Read a row: expensive (assemble from columns).
Good for: OLAP (aggregations over few columns).

### Compression
Columns of similar data compress 5-10×. Dramatic storage savings for analytics.

### Examples
- Row: PostgreSQL, MySQL, MongoDB
- Column: Redshift, BigQuery, Snowflake, ClickHouse, Apache Parquet
- Hybrid: SQL Server columnstore indexes; PostgreSQL via Citus

## SQL vs NoSQL vs NewSQL

### SQL (Relational)
- Strong consistency by default
- ACID transactions
- Schema enforced
- Joins, ad-hoc queries
- Examples: PostgreSQL, MySQL, Oracle, SQL Server

Pros: mature, structured, well-understood.
Cons: harder to scale horizontally; rigid schema.

### NoSQL
Multiple sub-categories:

#### Key-Value
- Simple K=V; fast
- DynamoDB, Redis, Riak
- Use: caching, session store, simple lookups

#### Document
- JSON / BSON docs; nested structure
- MongoDB, Firestore, Cosmos DB
- Use: flexible schemas, semi-structured data

#### Wide-Column
- Family of columns per row; sparse
- Cassandra, Bigtable, HBase
- Use: time-series, logs, very large datasets

#### Graph
- Nodes + edges
- Neo4j, Neptune, Dgraph
- Use: social, knowledge graphs

#### Time-Series
- Optimized for timestamps + sequential writes
- InfluxDB, TimescaleDB, Prometheus TSDB
- Use: metrics, IoT, monitoring

### NewSQL
- ACID + horizontal scale
- Distributed SQL
- Examples: Spanner, CockroachDB, YugabyteDB, TiDB
- Use: global ACID needs that traditional SQL can't scale to

## Choosing

| Need | Pick |
|---|---|
| General app DB, < 100GB | PostgreSQL |
| Lots of small reads/writes; key-value | DynamoDB / Redis |
| Document with flexible schema | MongoDB / Firestore |
| Wide-column at scale | Cassandra / Bigtable |
| Graph queries | Neo4j |
| Time-series | TimescaleDB / Influx |
| Search | Elasticsearch / OpenSearch |
| Analytics warehouse | BigQuery / Snowflake |
| Global ACID SQL | Spanner / CockroachDB |
| Cache | Redis |

## CAP Theorem

In a distributed system, you can pick 2 of:
- **C**onsistency: all nodes see same data
- **A**vailability: every request gets a response
- **P**artition tolerance: works despite network failures

In practice: P is non-negotiable (networks fail). So you pick CP or AP.

- CP: Spanner, etcd, ZooKeeper, HBase, MongoDB (default)
- AP: DynamoDB (eventual), Cassandra, CouchDB

## PACELC (refinement of CAP)

If partitioned (P): pick A or C.
Else (E): pick L (latency) or C (consistency).

- PC/EC: Spanner — always consistent, sometimes slow
- PA/EL: DynamoDB eventually — always available, low latency, eventually consistent

## Consistency Models

- **Strong**: read returns latest write
- **Eventual**: reads converge eventually
- **Causal**: ordering preserved per causal chain
- **Read-your-writes**: you see your own writes (typical for sessions)
- **Bounded staleness**: at most N seconds stale

DynamoDB defaults to eventual reads (cheaper); strong reads available (2× cost).

## When to Switch DB

Don't fall in love with your DB. Switch when:
- Scale outgrows it (relational at 50 TB → consider migration)
- Pattern doesn't fit (deeply nested data on relational → document)
- Cost exceeds value (NoSQL for high write rate)

Migration is hard; plan for it.

## Interview Themes

- "Choose a DB for X workload"
- "Row vs column — explain"
- "CAP theorem — apply"
- "When DynamoDB over Postgres?"
- "OLTP and OLAP in one or separate?"
