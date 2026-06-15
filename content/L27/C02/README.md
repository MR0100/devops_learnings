# L27/C02 — High Availability Patterns

## Topics

- **T01 Single AZ vs Multi-AZ** — Within region
- **T02 Multi-Region Architecture** — Across regions
- **T03 Active/Active vs Active/Passive** — Modes
- **T04 Cells & Bulkheads** — Amazon's approach

## Single AZ vs Multi-AZ

Single AZ = single failure domain. AZ goes down, service down.

Multi-AZ = redundancy:
- Multiple instances across AZs
- Cloud LB distributes
- Auto-recovery on AZ failure (~minutes)

For Tier 1+ in cloud: always Multi-AZ.

### Cost
- Compute: same (you'd run multiple instances anyway)
- Cross-AZ traffic: small additional cost
- Multi-AZ RDS: ~2× cost of single-AZ (sync replica)

### Capacity Math
3 AZs serving equal traffic → 1/3 per AZ.
On AZ failure: surviving 2 absorb 50% more load each.
Pods must have 50% headroom at steady-state utilization.

## Multi-Region Architecture

```
Region A (primary)               Region B (DR or secondary)
[ALB → app → DB]    ←─ replication ─→     [ALB → app → DB]
```

Cross-region replication:
- Async for most services (sub-second to few seconds lag)
- Sync only for low-latency same-continent pairs (rare; expensive)

### Routing
- Route 53 latency / geo policy
- Global Accelerator (anycast IP)
- DNS failover (slowest)

### Failover Mechanics
- Detect failure (health checks)
- Promote secondary (DB; if active/passive)
- Route traffic to secondary

## Active/Active

Both regions actively serving.

### Pros
- Load distributed
- Both regions warm
- Zero-downtime failover

### Cons
- Data conflicts possible (multi-master)
- Higher cost (both regions provisioned for full load)
- Complex (CRDTs, conflict resolution)

### Patterns
- **Sharded** (each region owns specific data)
- **Eventually consistent** (DynamoDB Global Tables, Cassandra)
- **Globally consistent** (Spanner, CockroachDB)

## Active/Passive

Primary serves; secondary stands by.

### Pros
- Simpler (no conflict resolution)
- Cheaper (passive can be smaller)

### Cons
- Failover not instant
- Passive "rusts" (not regularly exercised)

### Sub-Variants
- Hot standby (passive fully warm)
- Warm standby (smaller capacity; scale up on failover)
- Cold standby (powered off; longer RTO)

## Cells & Bulkheads

Amazon's approach to limiting blast radius.

### Cell
A self-contained slice of the system. Customer routing to a specific cell.

```
[Cell 1]   serves users [1, 1000)
[Cell 2]   serves users [1000, 2000)
[Cell 3]   serves users [2000, 3000)
...
[Cell N]   serves users [...]
```

Failure in Cell 5 only affects users in Cell 5 (~1/N of customers).

### Why
- Limits blast radius
- Independent failure domains
- Easier to reason about
- Cells can be different versions / configs

### How
- Cell router (lightweight stable layer)
- Cell-specific storage
- Cells deployed independently
- Customer affinity rule (consistent hash on user_id)

### Used By
- Amazon S3
- DynamoDB
- AWS overall is heavily cell-based internally

## Stateless Tier Multi-Region

Stateless services are easy:
- Deploy in N regions
- Route 53 / Global Accelerator distribute traffic
- Add region: scale; remove: shrink

State is hard.

## Stateful Tier Multi-Region

### Data Replication Choices

#### Async Replication
- Primary in region A; replica in region B
- Writes ack on primary; replicate after
- Lag: sub-second typical; can spike under load
- Tradeoff: potential data loss on primary failure

#### Sync Replication
- Writes only ack after replica confirms
- Cross-region sync: high latency per write (~100ms+)
- Rarely used cross-region

#### Multi-Region Consensus
- Spanner, CockroachDB: distributed consensus
- Writes work globally
- Sub-second consistency
- Expensive infrastructure

### Choosing
Most services use async cross-region replication and accept small RPO.

## Failover Trigger

### Automated
- Health checks pass at TTL → cut over
- Risk: false positive triggers unnecessary failover

### Semi-Auto
- Health checks trigger paging
- Human reviews + confirms
- Bot does the cutover

### Manual
- Senior engineer assesses
- Sets up failover manually
- Slower but safer for major changes

## DNS Failover Caveats

- TTLs lie (DNS resolvers ignore short TTLs)
- Clients cache DNS for session lifetime
- Java JVMs cache DNS forever by default
- Real-world failover: 1-5 min instead of "TTL"

For faster: anycast (Global Accelerator) bypasses DNS.

## Anycast Failover

Anycast IP advertised from multiple regions. Internet routing prefers nearest.

Withdraw advertisement from failing region → routing shifts to surviving regions (within minutes).

Used by:
- Global Accelerator
- Cloudflare
- DNS root servers
- AWS S3 endpoints

## Service Mesh Failover

Service mesh can do region-aware routing:
- Prefer local region
- Fall back to remote region on failure
- mTLS preserved

Cilium Cluster Mesh, Istio multi-cluster, Linkerd multi-cluster.

## Interview Themes

- "Active/active vs active/passive"
- "Cell architecture — what does it solve?"
- "Why is DNS failover slow?"
- "Cross-region replication patterns"
- "AZ failure math"
