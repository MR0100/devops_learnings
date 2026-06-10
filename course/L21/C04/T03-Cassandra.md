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

```cql
SELECT * FROM events WHERE user_id = 'X' USING CONSISTENCY QUORUM;
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
SELECT ... USING CONSISTENCY QUORUM;
```

## Interview Prep

**Mid**: "Cassandra."

**Senior**: "Tunable consistency."

**Staff**: "Cassandra at scale."

## Next Topic

→ [T04 — Redis (Sentinel, Cluster)](T04-Redis.md)
