# L21/C04/T03 — Cassandra (Tunable Consistency)

## Learning Objectives

- Operate Cassandra
- Tune consistency

## Cassandra

Wide-column NoSQL:
- Massive scale
- High write throughput
- Eventually consistent (tunable)
- No SPOF

## Architecture

- All nodes equal (ring)
- Data distributed by token
- Replication factor (RF)
- Gossip for membership

## Data Model

```cql
CREATE KEYSPACE mykey WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'datacenter1': 3
};

CREATE TABLE mykey.events (
  user_id text,
  event_time timeuuid,
  data text,
  PRIMARY KEY (user_id, event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);
```

PK:
- Partition key (user_id): distributes
- Clustering key (event_time): sorts within partition

## Replication

Per keyspace:
- SimpleStrategy (dev)
- NetworkTopologyStrategy (prod; per-DC)

RF=3: 3 copies.

## Tunable Consistency

Per query:
- ONE
- TWO / THREE
- QUORUM (majority RF)
- ALL
- LOCAL_QUORUM (within DC)
- EACH_QUORUM (per-DC)

## Examples

Consistency is **not** part of the `SELECT` statement in CQL3. In `cqlsh`, set it as a session-level command that applies to subsequent statements:

```cql
CONSISTENCY QUORUM;
SELECT * FROM events WHERE user_id = 'X';
```

(`USING CONSISTENCY QUORUM` appended to a SELECT was CQL2 syntax and is invalid in CQL3.) In application code you set it on the statement/driver instead:

```python
from cassandra import ConsistencyLevel
stmt = SimpleStatement(
    "SELECT * FROM events WHERE user_id = %s",
    consistency_level=ConsistencyLevel.QUORUM,
)
session.execute(stmt, ['X'])
```

QUORUM = (RF / 2) + 1.

For RF=3: QUORUM=2.

## Strong Consistency

R + W > RF.

For RF=3:
- W=2 + R=2 (QUORUM both): strong.
- W=ALL + R=ONE: strong.
- W=1 + R=1: weak.

## Replication Factor

```cql
ALTER KEYSPACE mykey WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'us-east': 3,
  'us-west': 3
};
```

For: multi-DC.

## Compaction

Background:
- Merges SSTables
- Removes deleted

Strategies:
- SizeTieredCompactionStrategy (default; writes-heavy)
- LeveledCompactionStrategy (read-heavy)
- TimeWindowCompactionStrategy (time-series)

## Repair

```bash
nodetool repair
```

Anti-entropy. Sync inconsistencies.

Run periodically.

## Tools

- nodetool: admin
- cqlsh: CQL client

```bash
nodetool status
nodetool info
nodetool tablestats
```

## Performance

- Writes: very fast (append)
- Reads: depend on partition size
- Avoid: large partitions (> 100 MB)
- Avoid: TOMBSTONE accumulation

## Tombstones

Deletes = tombstone:
- Eventually compacted
- Too many: slow reads

For: avoid frequent deletes.

## Cassandra vs Bigtable

| | Cassandra | Bigtable |
|---|---|---|
| Open source | yes | proprietary |
| Cloud | self / DataStax | GCP managed |
| Model | similar | similar |

## ScyllaDB

C++ rewrite of Cassandra:
- Same protocol
- 10× perf
- Lower latency

For: cost-effective alternative.

## When Cassandra

- Time-series
- Massive write throughput
- Multi-region
- Eventual OK

## When Not

- Strong consistency required
- Complex queries
- Joins
- Small data

## Best Practices

- Partition size < 100 MB
- Avoid hot partitions
- Tune consistency per query
- Repair regularly
- Multi-DC NetworkTopology

## Common Mistakes

- Single-key partition (millions of rows in one)
- Tombstone overload
- No repair
- Wrong consistency (data loss)

## Quick Refs

```bash
nodetool status / info / repair / cleanup / compact

cqlsh
USE keyspace;
CONSISTENCY QUORUM;    -- session-level; applies to following statements
SELECT ...;
```

## Interview Prep

**Mid**: "What is Cassandra and when would you use it?" — A masterless, wide-column NoSQL store: every node is equal (ring), data is distributed by token, and it favors availability and high write throughput (AP). Use it for time-series, logs, and multi-region write-heavy workloads where eventual consistency is acceptable.

**Senior**: "Explain tunable consistency." — Consistency is set per query, not per cluster (`CONSISTENCY QUORUM;` in cqlsh, or on the statement in a driver). QUORUM = (RF/2)+1; you get strong consistency when R + W > RF (e.g. RF=3, W=2, R=2). LOCAL_QUORUM keeps it within one DC to avoid cross-region latency. It's a per-operation latency-vs-consistency dial.

**Staff**: "What breaks Cassandra at scale and how do you operate around it?" — Data-modeling first: partitions must stay under ~100 MB and avoid hot partitions, because the partition key dictates everything. Tombstone buildup from frequent deletes slows reads, so design to avoid delete-heavy patterns and tune compaction (STCS write-heavy, LCS read-heavy, TWCS time-series). Run repairs to fix entropy, use NetworkTopologyStrategy + LOCAL_QUORUM for multi-DC, and consider ScyllaDB when the JVM/GC overhead becomes the bottleneck.

## Next Topic

→ [T04 — Redis (Sentinel, Cluster)](T04-Redis.md)
