# L27/C02/T02 — Multi-Region Architecture

## Learning Objectives

- Design multi-region
- Handle complexity

## Why Multi-Region

- Region failure resilience
- Lower latency globally
- Compliance (data residency)
- Disaster recovery

## Why Hesitate

- Cost (2x infra)
- Complexity (data consistency)
- Latency cross-region
- Ops burden

## Patterns

### Active-Active
Both serve traffic.
- Lowest latency
- Highest cost

### Active-Passive
One serves; other standby.
- Cost-effective
- Failover latency

### Read Replicas
Writes to primary; reads from any.
- Easier
- Read latency low

## Data

Hardest part:
- Sync replication (slow)
- Async (lag, conflicts)
- Conflict resolution

Tools:
- Aurora Global (async; 1 sec)
- Spanner (sync; global)
- CockroachDB (sync)
- DynamoDB Global Tables (active-active; LWW)

## Compute

Multi-region:
- Deploy to N regions
- Same artifact
- Per-region config

For: standard.

## DNS

Route 53:
- Latency-based routing
- Geolocation
- Health checks

Or:
- Cloudflare global LB
- AWS Global Accelerator (anycast)

## Static Content

CDN handles:
- Edge caching globally
- Origin in primary region

## Stateful

DBs, caches:
- Cross-region replication
- Plan failover
- Backup

## Cost

Estimate:
- 2x compute
- Cross-region transfer
- Egress out of cloud
- Tools

For: significant.

## Examples

### Netflix
Multi-region; sophisticated.

### Stripe
US-EU multi-region.

### Many SaaS
Single region with DR.

## Per Tier

- Tier 1: multi-region active
- Tier 2: multi-region with failover
- Tier 3: single region with backup

## Latency Implications

- Cross-region: 50-200 ms
- Avoid sync calls cross-region
- Async / eventual where possible

## Best Practices

- Justify multi-region
- Latency-aware design
- Per-region capacity
- Drill failover
- Per-region capacity

## Common Mistakes

- Multi-region without need (cost)
- Sync cross-region (slow)
- No failover plan
- Stateful inconsistencies

## Quick Refs

```
Active-Active: both regions
Active-Passive: failover
Read Replicas: writes one; reads many

Tools:
- DNS: Route 53 / Cloudflare
- Anycast: Global Accelerator
- DB: Aurora Global, Spanner, Cockroach
```

## Interview Prep

**Senior**: "Multi-region."

**Staff**: "Pattern design."

**Principal**: "Global architecture."

## Next Topic

→ [T03 — Active/Active vs Active/Passive](T03-Active-Active-Passive.md)
