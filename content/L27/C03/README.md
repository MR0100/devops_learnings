# L27/C03 — Data Replication

## Topics

- **T01 Synchronous vs Asynchronous** — Tradeoff
- **T02 Cross-Region Replication** — At scale
- **T03 Conflict Resolution** — When both sides write

## Synchronous Replication

Primary waits for replica ack before reporting success.

```
Client → Primary → write → wait for replica ack → respond to client
```

### Pros
- Zero data loss on primary failure (if replica caught up)
- Strong consistency

### Cons
- Latency = primary commit time + replica commit time
- Cross-region sync = 100ms+ per write (unacceptable for many apps)
- Replica unavailable → writes blocked

### Used In
- Postgres synchronous_standby_names (same-region typically)
- MySQL semi-sync
- Spanner / CockroachDB (distributed consensus)

## Asynchronous Replication

Primary acks; replica catches up after.

```
Client → Primary → write + respond
                ↓ (async background)
                Replica
```

### Pros
- Low latency (no remote wait)
- Replica can be far (cross-region)
- Replica unavailable doesn't block writes

### Cons
- Replication lag (seconds typically; minutes possible under load)
- Data loss possible on primary failure (transactions not yet replicated)
- Eventual consistency (read replica may show stale data)

### Used In
- Postgres streaming (default)
- MySQL async (default)
- MongoDB replica sets
- DynamoDB Global Tables
- S3 Cross-Region Replication

## Semi-Synchronous

Primary waits for AT LEAST ONE replica ack (not all).

- Better latency than full sync
- Some durability guarantee
- MySQL semi-sync; Postgres `synchronous_standby_names = 'ANY 1 (replica1, replica2)'`

## Cross-Region Replication

Async almost always. Latency is the constraint.

### Patterns

#### Single-Master
- One region writes
- Other regions read-only replicas
- On primary failure: promote a replica

#### Multi-Master
- All regions write
- Conflicts possible
- Resolution needed

#### Per-Key Sharding
- Each key has a "home" region
- Other regions forward writes
- Simpler than multi-master globally

## Conflict Resolution

### Last Writer Wins (LWW)
- Timestamp on each write
- Higher timestamp wins
- Simple; loses concurrent writes
- DynamoDB Global Tables default

### Custom Merge Function
- App-defined merge logic
- Example: shopping cart = union of items

### Vector Clocks
- Causal ordering
- Detect concurrent writes
- Apps decide how to merge
- Used by Riak, Cassandra (older), Akka cluster

### CRDTs (Conflict-Free Replicated Data Types)
- Mathematically commutative
- Concurrent writes always converge
- Examples: counter, set, map
- Built into Redis Enterprise, some Cassandra

## Replication Lag

### Causes
- Network bandwidth/latency between primary and replica
- Replica CPU/IO saturated (apply queue grows)
- Single-threaded apply (MySQL trad)
- Large transactions
- Schema changes

### Monitoring
- Postgres: `pg_stat_replication`, `pg_last_wal_receive_lsn`
- MySQL: `Seconds_Behind_Master` (unreliable); pt-heartbeat (reliable)
- DynamoDB: ReplicationLatency CloudWatch metric

### Mitigations
- Parallel apply (MySQL parallel SQL workers; Postgres logical workers)
- Faster network
- Smaller transactions on primary
- Adequate IOPS on replicas

## Read-Your-Writes Consistency

User writes; immediately reads. Sees stale data on replica? Bad UX.

### Solutions
- Route reads to primary for current session (sticky)
- Read from primary for N seconds after write
- Use causal tokens (LSN) to ensure replica has caught up
- Conditional reads with min-lag check

## Cross-Region Replication Throughput

A few rules of thumb:
- TCP windowing limits throughput
- BDP (Bandwidth-Delay Product) matters
- Need to tune TCP for high-BDP paths
- Compression helps (gzip / zstd)

## Storage-Level Replication

Some systems replicate at storage level (not DB-aware):
- AWS RDS storage replication (Multi-AZ)
- Aurora storage layer (6 copies across 3 AZs)
- Block storage replication (EBS snapshots, GCP PD regional)

Faster, more reliable; but app can't take advantage of replicas as readers.

## DynamoDB Global Tables

Multi-region multi-active.
- Last-writer-wins
- Sub-second replication
- Conflict detection (timestamp-based)
- Excellent for active-active patterns

## DNS-Based Read Routing

Geo-DNS routes user to nearest replica region:
- Reads served locally (low latency)
- Writes can go to local OR centralized
- Local writes = need replication strategy

## Replication Tools Summary

| | Replication Style |
|---|---|
| Postgres streaming | Async (sync optional) |
| Aurora | Storage-level (effectively sync; 4-of-6 quorum) |
| MySQL async | Async |
| MySQL Group Replication | Sync (multi-master) |
| DynamoDB Global | Async multi-active |
| MongoDB | Async (majority commit option) |
| Cassandra | Tunable per request |
| Spanner | Sync (Paxos) |
| Kafka | Sync ISR (configurable) |
| S3 CRR | Async |

## Interview Themes

- "Sync vs async — tradeoffs"
- "Conflict resolution strategies"
- "Replication lag — causes and mitigation"
- "Read-your-writes — solve"
- "DynamoDB Global Tables vs Spanner"
