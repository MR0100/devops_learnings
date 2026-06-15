# L28/C02 — Scalability Patterns

## Topics

- **T01 Horizontal vs Vertical** — Add machines or bigger machines
- **T02 Sharding & Partitioning** — Split data
- **T03 Replication Patterns** — Multiple copies
- **T04 CAP & PACELC** — Distributed tradeoffs

## Vertical vs Horizontal

### Vertical (Scale Up)
- Bigger machine
- Limits: max VM size, max IOPS, max network
- Simpler (no distribution)
- Expensive past a point

### Horizontal (Scale Out)
- More machines
- Linear scaling possible
- Requires distributed coordination
- More complex but unbounded

Modern systems: horizontal by default; vertical for components like primary DB until necessary to shard.

## Sharding / Partitioning

Split data across machines.

### Hash Sharding
- `hash(key) mod N` → assigns to shard
- Uniform distribution
- Resharding painful (key→shard mapping changes)

### Range Sharding
- e.g., user_id 1-1M → shard A; 1M-2M → shard B
- Hot ranges possible (recent data)
- Easier to add shards (split a range)

### Geo Sharding
- By region
- Per-user shard based on location
- Data residency benefits

### Composite
- Shard by tenant + range within tenant
- Avoids cross-tenant queries

## Choosing Shard Key

Critical decision. Bad keys → hot shards.

- High cardinality (millions of values)
- Uniform access (no skew)
- Aligns with most common queries (avoid scatter-gather)

Examples:
- ✅ user_id (uniform)
- ✅ tenant_id#user_id (multi-tenant)
- ❌ status (few values, skewed)
- ❌ created_at (recent data hot)

## Resharding

Painful. Strategies:
- **Consistent hashing**: minimize remapping
- **Virtual shards**: many virtual; few physical; redistribute virtual
- **Double-write**: write to old + new; backfill; cut over
- **Pre-sharded at scale**: anticipate growth (256 shards even at small scale)

## Replication Patterns

### Single-Leader
- One leader; many followers
- Writes go to leader; reads can fan out
- Simple consistency model
- Leader is bottleneck

### Multi-Leader
- Multiple leaders accept writes
- Replicate among each other
- Higher write throughput
- Conflict resolution needed (LWW, CRDTs)

### Leaderless
- All replicas equal
- Writes go to N; reads from N; quorum
- DynamoDB-style; Cassandra-style

## CAP Theorem

In a partition, choose **C** or **A**:

- **CP**: Strong consistency; refuse writes if can't replicate (Spanner, etcd, ZooKeeper)
- **AP**: Serve writes; reconcile later (DynamoDB eventual, Cassandra)
- **CA**: only without partition (single-node systems)

## PACELC

Refinement: even without partition, choose **L**atency or **C**onsistency.

- **PC/EC**: consistent always (Spanner; sometimes slow)
- **PA/EL**: available always, eventual reads (DynamoDB eventual; fast)

## Consistency Models

- **Strong**: read returns latest write
- **Eventual**: reads converge over time
- **Causal**: ordering per causal chain preserved
- **Read-your-writes**: see your own writes
- **Monotonic reads**: never see older version after seeing newer
- **Bounded staleness**: at most N seconds stale

Different ops in same system can have different consistency requirements.

## Scaling Patterns by Layer

### Stateless
Easy: more pods, more instances. Auto-scale.

### Caching
- Local in-process (cheapest, per-instance)
- Distributed (Redis cluster)
- CDN at edge

### Relational DB
- Vertical scaling first (more RAM)
- Read replicas (read-heavy workloads)
- Sharding (when single primary insufficient)
- Move to distributed SQL (Spanner, Cockroach) for true horizontal

### NoSQL
- Built for horizontal scale (DynamoDB, Cassandra, Bigtable)
- Partition by key; spread automatically

### Messaging
- Partition (Kafka)
- Multiple consumer groups for fanout

## Stateless First

Make as much of the stack stateless as possible:
- Stateless app servers (state in DB/cache)
- Stateless workers
- Stateless serverless functions

Stateful tier = small, isolated, hardened.

## Capacity Headroom

Plan for:
- AZ failure (surviving AZs absorb 1.5× load → 50% headroom)
- Traffic spike (50-100% headroom)
- Slow query / dependency (absorb backlog)

Modern: HPA, Cluster Autoscaler, Karpenter — automate scaling.

## Backpressure

When downstream slow:
- Queue grows
- Drop low-priority work
- Return 429 (Too Many Requests)
- Shed load
- Don't accept all traffic and crash

## Designing for Scale Indicators

| Indicator | Pattern |
|---|---|
| Read-heavy (10:1+) | Caching + read replicas |
| Write-heavy | Sharding, message queues |
| Bursty | Auto-scaling, queue buffering |
| Global users | CDN, multi-region, locality routing |
| Variable load | Serverless |
| Steady load | Reserved capacity |

## Interview Themes

- "Vertical vs horizontal scaling"
- "Sharding strategies"
- "Pick a shard key for X"
- "CAP — apply"
- "Read-heavy vs write-heavy patterns"
