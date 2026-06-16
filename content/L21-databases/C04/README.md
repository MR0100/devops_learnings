# L21/C04 — NoSQL Operations

## Topics

- **T01 DynamoDB Operations** — Tables, partitions, indexes
- **T02 MongoDB** — Replica sets, sharding
- **T03 Cassandra** — Tunable consistency
- **T04 Redis** — Sentinel, Cluster

## DynamoDB

### Key Concepts
- **Table**: collection of items
- **Item**: row (max 400 KB)
- **Primary Key**: Partition key (HASH) or composite (PK + Sort Key)
- **Attribute**: column (no fixed schema)

### Partition Strategy
DynamoDB hashes partition key → assigns to a physical partition.
- Each partition: ~3000 RCU + 1000 WCU + 10 GB
- Bad partition keys → hot partitions → throttling

#### Good PK
- High cardinality (millions of unique values)
- Uniform access (no skew)
- Examples: `user_id`, `tenant_id#user_id`

#### Bad PK
- `status` (few values: "active", "pending", "inactive")
- `country` (some countries dominate)
- `date` (recent date is hot)

### Capacity Modes

**Provisioned**:
- Set RCU/WCU
- Auto-scaling supported
- Cheaper if predictable

**On-Demand**:
- Pay per request
- Burst-friendly
- 5-10× more expensive per request

### Indexes

**Local Secondary Index (LSI)**:
- Same PK, different sort key
- Created with table only
- Max 5 per table

**Global Secondary Index (GSI)**:
- Different PK
- Created any time
- Max 20 per table
- Eventually consistent
- Separate capacity

### DAX (DynamoDB Accelerator)
In-memory cache. ms → μs.

### Streams
Change data capture. 24h retention.
- Trigger Lambdas on changes
- Replicate to other systems

### Global Tables
Multi-region multi-active (via streams + replication).
- Last-writer-wins (timestamp-based)

### Operations
- Don't think "relational"; think "single-table design"
- Plan access patterns up front; design PK/SK around them
- Monitor: ConsumedCapacity, ThrottledRequests
- Backups: continuous (point-in-time recovery) or on-demand

## MongoDB

### Replica Set
- 3 nodes minimum
- Primary + secondaries
- Auto-failover (~10s)
- Read preference: primary, secondary, nearest

### Sharding
- Horizontal partition by shard key
- Shard key choice critical (like DynamoDB PK)
- Bad: monotonically-increasing (e.g., ObjectId based on time) → hot shard
- Good: hashed shard key (distributes uniformly)

### Architecture
```
mongos (router) — multiple, stateless
   ↓
config servers (3-node replica set; holds metadata)
   ↓
shards (each is a replica set)
```

### Consistency
- Strong by default (primary read)
- Eventually consistent for secondary reads
- Write concerns: `w: 1` (primary ack) vs `w: majority`
- Read concerns: local, available, majority, linearizable

### Backup
- mongodump (logical)
- File-system snapshot of dbPath
- MongoDB Cloud Backup (Atlas)

## Cassandra

Wide-column store. Tunable consistency. Multi-DC native.

### Architecture
- Peer-to-peer (no primary)
- Each node responsible for some token range
- Gossip protocol
- Tunable consistency (CL=ONE, QUORUM, ALL, LOCAL_QUORUM, etc.)

### Tunable Consistency
```
Write CL=QUORUM (>50% nodes confirm) + Read CL=QUORUM = strong consistency
Write CL=ONE + Read CL=ONE = fast, eventually consistent
```

### Use Cases
- Time-series (write-heavy)
- IoT
- Recommendation systems
- Multi-DC active-active

### Operating
- Compaction strategies (SizeTiered, Leveled, TimeWindow)
- Repair (nodetool repair) regularly
- Don't over-shard
- Monitor: heap, GC, latency p99

## Redis

Covered in detail in L23 (Caching). Here briefly:

### Modes
- **Standalone**: single node
- **Sentinel**: HA with auto-failover (1 primary + N replicas; sentinels elect new primary)
- **Cluster**: sharded; 16384 hash slots distributed across primaries
- **Enterprise**: commercial; multi-AZ, multi-region, conflict-free types

### Cluster
- Sharded; each key hashed to a slot, slot to a node
- Primary + replicas per shard
- Client must understand cluster topology

### Persistence
- **RDB**: periodic snapshot
- **AOF**: append-only log of writes (more durable)
- Both: best for production

### Operations
- Eviction policy (allkeys-lru common for caches)
- Memory monitoring (Redis is single-threaded; memory is the limit)
- Replication lag (sync vs async)

## Cross-NoSQL Choices

| Need | Pick |
|---|---|
| Sub-ms KV at scale | DynamoDB / Bigtable |
| Document with rich queries | MongoDB / Firestore |
| Multi-DC time-series | Cassandra / ScyllaDB |
| Sub-ms cache | Redis |
| Search | Elasticsearch / OpenSearch |
| Graph | Neo4j / Neptune |

## Interview Themes

- "DynamoDB partition key choice"
- "MongoDB shard key — what makes it good?"
- "Cassandra tunable consistency"
- "Redis Sentinel vs Cluster"
- "NoSQL vs SQL — when each?"
- "Hot partition diagnosis"
