# L27/C01/T01 — RTO, RPO, MTD

## Learning Objectives

- Define DR metrics
- Apply to design

(Covered L21/C06/T01 for DBs. Broader here.)

## RTO

Recovery Time Objective:
- Max acceptable downtime
- Hours / minutes / seconds

## RPO

Recovery Point Objective:
- Max acceptable data loss
- Time-based

## MTD

Maximum Tolerable Downtime:
- Business-driven
- Catastrophic if exceeded

## Examples

### Critical
- RTO: < 1 min
- RPO: 0 (no loss)
- MTD: 4 hours

### Important
- RTO: < 1 hour
- RPO: 15 min
- MTD: 1 day

### Standard
- RTO: 4 hours
- RPO: 1 hour
- MTD: 3 days

## Per Service

Different tiers:
- Mission-critical (payment): strictest
- Important (user-facing): tight
- Internal (admin): looser
- Batch (analytics): loose

## Investment

Lower RTO/RPO = higher cost:
- Sync replication (RPO 0): expensive
- Multi-region active: 2x infra
- Cold backup: cheap

For: match to value.

## Measure

Tracking:
- Actual RTO during incidents
- Actual RPO (data loss)
- Trends

## DR Drill

Quarterly: measure RTO/RPO.

If exceeded target: invest more.

## Compute RTO

Time to:
- Detect failure
- Decide failover
- Execute failover
- Verify

Each: minutes typically.

For: tight automation.

## Compute RPO

Replication lag:
- Sync: 0
- Async cross-region: 1-30 sec
- Cross-region async: 1-5 min
- Daily backup: 24 hr

## Communication

To business:
- "RTO 1 hour means..."
- "RPO 5 min means..."

For: aligned expectations.

## Best Practices

- Per service tier
- Document targets
- Drill quarterly
- Adjust based on cost / value

## Common Mistakes

- One RTO for all (waste)
- Set without measuring
- Drill annually (insufficient)
- Promise without ability

## Quick Refs

```
RTO: how fast back up
RPO: how much data lost
MTD: maximum tolerable down
```

## Interview Prep

**Mid**: "RTO / RPO."

**Senior**: "Design for targets."

**Staff**: "DR strategy."

## Next Topic

→ [T02 — DR Strategies](T02-DR-Strategies.md)
