# L07/C06/T02 — Managed NoSQL (DynamoDB, Firestore, Cosmos DB)

## Learning Objectives

- Pick NoSQL when right
- Use DynamoDB / Firestore correctly

## NoSQL Categories

- **Key-Value**: Redis, DynamoDB, etcd
- **Document**: MongoDB, Firestore, Cosmos DB
- **Column-family**: Cassandra, Bigtable, HBase
- **Graph**: Neptune, Cosmos Graph
- **Time-series**: Timestream, InfluxDB

NoSQL ≠ "no SQL". Means "not only SQL" — often non-relational.

## DynamoDB (AWS)

Fully managed key-value + document. Massive scale; predictable single-digit ms latency.

### Tables
- Primary key: partition key (or partition + sort)
- Items: JSON-like; up to 400 KB
- Attributes: typed (S, N, B, etc.)

### Capacity Modes
- **On-Demand**: pay per request; auto-scale; no planning
- **Provisioned**: set RCU/WCU; cheaper at steady; tune for cost

RCU/WCU: Read/Write Capacity Units.
- 1 WCU = 1 write/sec of up to 1 KB
- 1 RCU = 2 eventually-consistent reads/sec of up to 4 KB

## Access Patterns First

DynamoDB schema design starts with: "What queries will I run?"

Get user by id: PK = user_id.
Get user's orders: PK = user_id, SK = order_id.
Get orders by status: GSI (Global Secondary Index).

Pre-compute every query. No JOINs.

## Indexes

- **LSI**: Local Secondary Index; same PK, different SK
- **GSI**: Global Secondary Index; different PK; eventually consistent

GSI: queries by alternate key. Cost: extra writes (every write to base = write to GSI).

## Transactions

Up to 100 items / 4 MB across tables.
```python
dynamodb.transact_write_items(
    TransactItems=[
        {"Update": {...}},
        {"Put": {...}}
    ]
)
```

Cost: 2× standard ops.

## Streams

Change data capture; 24-hour retention. Trigger Lambda for events. Use for:
- Replicate to other DB
- Trigger workflows
- Aggregate counts
- ES sync

## Global Tables

Multi-region, multi-master. Eventually consistent across regions. Conflict resolution: last-writer-wins. RPO: seconds.

## Backup

PITR (point-in-time): last 35 days; restore to any second.
On-demand backups: persist beyond.

## TTL

Auto-delete expired items:
```
SET ttl = epoch_seconds
```
DynamoDB deletes within 48h of TTL. Free.

## Hot Partitions

If one PK gets disproportionate traffic: that partition throttles.

Solution: spread (random suffix to PK), or design better PK.

## Costs

On-demand: $1.25/M writes; $0.25/M reads. Storage $0.25/GB.
Provisioned: cheaper steady-state.

For Pinterest scale: massive. For startup: cheap.

## Firestore (GCP)

Document DB; auto-scaling; real-time sync to clients.

```
collection users:
  document alice:
    fields: name, email
    sub-collection orders:
      document 1:
        ...
```

Hierarchical. Realtime listeners. Used heavily for mobile apps.

## Cosmos DB (Azure)

Multi-model: document, KV, column, graph in one. Global distribution; tunable consistency (5 levels).

## When NoSQL

- Massive scale (>100k QPS)
- Predictable access patterns
- Variable schema
- Need horizontal scale without thinking
- Single-row low-latency reads

## When NOT NoSQL

- Ad-hoc queries (no SQL)
- Complex joins
- Strong transactional needs across many entities
- Small to medium scale (Postgres simpler)

## DynamoDB Patterns

### Single-Table Design
All entities in one table; PK/SK distinguish:
- PK: USER#alice, SK: PROFILE → user data
- PK: USER#alice, SK: ORDER#1 → order data
- PK: USER#alice, SK: ORDER#2 → order data

Get user + orders in one query.

### Adjacency List
For graph-like:
- PK: USER#alice, SK: FRIEND#bob → alice's friend
- PK: USER#bob, SK: FRIEND#alice → bob's friend

### Sparse Index
GSI on attribute only some items have. Those items in index; others not. Efficient subset queries.

### Time Series
PK: deviceId, SK: timestamp. Range query for time range.

## Consistency

- Eventually consistent (default; cheaper)
- Strongly consistent (1 RCU more, slower, requires same AZ)

Most apps OK with eventual.

## Cost Optimization

- Right capacity mode (provisioned for steady; on-demand for unknown)
- TTL for ephemeral
- Sparse GSI
- Compress large attributes
- Don't store huge blobs (use S3, store URL)

## Migration

From RDBMS to DynamoDB: rethink schema. Not 1:1.

DMS (Database Migration Service) can help; but data model redesign mostly manual.

## DAX (DynamoDB Accelerator)

In-memory cache for DynamoDB. Microsecond reads. Useful for ultra-hot data.

## Local Dev

DynamoDB Local: embedded version for dev/test.
```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

## Common Mistakes

- Choosing NoSQL when SQL would do (most apps)
- Hot partition (bad PK design)
- Over-fetching with Scan (use Query)
- Many small writes (batch)
- Ignoring throttling alerts

## DynamoDB vs RDS Decision

| Factor | DynamoDB | RDS |
|---|---|---|
| Scale | unlimited | vertical |
| Latency | predictable | depends |
| Schema | flexible | strict |
| Queries | predefined | ad-hoc |
| Cost (small) | cheap | cheap |
| Cost (huge) | cheap | very expensive |
| Operations | none | medium |
| Migration to other DB | hard | easy |

Default for new high-scale: DynamoDB.
Default for new traditional: RDS Postgres.

## Best Practices

- Model the table from known access patterns first — design every query up front (single-table design, GSIs); there are no JOINs and no ad-hoc queries.
- Choose a high-cardinality, evenly-distributed partition key to avoid hot partitions; add a random/calculated suffix if traffic skews.
- Use on-demand capacity for unknown/spiky load and provisioned (with auto-scaling) for steady, predictable traffic to cut cost.
- Always `Query`, never `Scan`, for production reads; batch small writes and keep large blobs in S3 (store the URL).
- Enable PITR, use TTL for ephemeral data, and add DAX only for genuinely ultra-hot read paths.
- Default to eventual consistency unless a read truly needs strong consistency; reserve Global Tables for multi-region active-active needs.

## Quick Refs

NoSQL vs relational decision rule:

| Pick NoSQL (DynamoDB) when | Pick RDS when |
|---|---|
| Massive scale / predictable access | Ad-hoc queries, complex JOINs |
| Single-digit ms, single-row reads | Strong multi-entity transactions |
| Variable schema, horizontal scale | Small–medium scale, relational data |

Capacity units: 1 WCU = 1 write/s up to 1 KB · 1 RCU = 2 eventually-consistent (or 1 strong) reads/s up to 4 KB.

Index types: **LSI** = same PK, alternate SK (set at table creation) · **GSI** = different PK, eventually consistent, costs extra writes.

Cost (on-demand): ~$1.25 / 1M writes, ~$0.25 / 1M reads, ~$0.25/GB-mo storage. Provisioned is cheaper at steady state.

```bash
docker run -p 8000:8000 amazon/dynamodb-local   # local dev
```

## Interview Prep

**Mid**: "DynamoDB vs RDS."

**Senior**: "DynamoDB schema for X access patterns."

**Staff**: "Hot partition — diagnose / mitigate."

## Next Topic

→ [T03 — Managed Caches](T03-Managed-Caches.md)
