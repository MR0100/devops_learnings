# L27/C01/T02 — DR Strategies

## Learning Objectives

- Compare 4 DR strategies
- Pick by needs

## The Four

The AWS-canonical DR spectrum runs from cheapest/slowest to most
expensive/instant. They differ on one core question: **how much of the DR
environment is already running before disaster strikes?**

1. **Backup & Restore** — nothing running; rebuild from backups
2. **Pilot Light** — only the data layer is live; compute is provisioned on failover
3. **Warm Standby** — a scaled-down but fully functional copy is always running
4. **Active/Active** — full capacity serving traffic in both regions already

As you move down the list, RTO and RPO shrink and cost grows. Pick the cheapest
strategy that still meets the tier's RTO/RPO (from T01).

## 1. Backup & Restore

- Backups in DR region
- Provision when needed
- RTO: hours-days
- RPO: hours
- Cost: low

For: non-critical.

## 2. Pilot Light

- Core infra running (small)
- Scale up on disaster
- RTO: minutes-hours
- RPO: minutes-hours
- Cost: medium

Example:
- DB replica in DR
- Stopped app servers (templated)

## 3. Warm Standby

- Functional copy at smaller scale
- Scale up on disaster
- RTO: minutes
- RPO: seconds-minutes
- Cost: medium-high

Example:
- DB replica
- App servers running (smaller)
- Some traffic for warm-up

## 4. Active/Active

- Both regions serve traffic
- Failover instant
- RTO: seconds
- RPO: 0-seconds
- Cost: high (2x+)

Example:
- Multi-region DB
- Both DCs serving

## Choose

Map the strategy to the tier's RTO/RPO from T01 — don't default everything to
the same one:

- Tier 1 (critical): **Active/Active** — RTO/RPO ≈ 0, justifies 2×+ cost
- Tier 2 (important): **Warm Standby** — RTO minutes, RPO seconds
- Tier 3 (standard): **Pilot Light** — RTO tens of minutes, RPO minutes
- Tier 4 (low): **Backup/Restore** — RTO hours–days, RPO hours

The honest pick is the *cheapest* strategy that still meets the tier's targets.
Putting analytics on active/active wastes money; putting payments on
backup/restore breaks the business.

## Cost vs Recovery

```
Cost
  ↑
A/A  ●
W/S    ●
P/L      ●
B/R        ●
  ──────────→ RTO/RPO (lower is faster)
```

## Implementation

### Backup/Restore
- Daily backups
- Cross-region copy
- Documented restore

### Pilot Light
- DB replica
- AMI ready
- Network setup
- Scripts to scale

### Warm Standby
- DB replica
- App servers running (low capacity)
- LB ready

### Active/Active
- DB multi-region
- Apps in both
- DNS / anycast for traffic
- Conflict resolution

## DNS Failover

For Warm Standby / Pilot Light:
- Route 53 health checks
- Failover record
- DNS TTL matters (low for fast)

## Active/Active Examples

### DynamoDB Global Tables
Multi-region active-active.

### Aurora Global
1-sec cross-region.

### S3 Multi-Region Access Points

### CockroachDB / Spanner
Native multi-region.

## Trade-Offs

### Active/Active
Pros: lowest RTO/RPO.
Cons: expensive; conflict resolution.

### Warm Standby
Pros: balance.
Cons: scaling delay.

### Pilot Light
Pros: cheaper than warm.
Cons: longer RTO.

### Backup/Restore
Pros: cheapest.
Cons: hours-days.

## Best Practices

- Tier services
- Strategy per tier
- Documented runbook
- Drilled quarterly
- Test failover

## Common Mistakes

- All services Active/Active (cost)
- All services Backup/Restore (slow)
- Never tested
- No runbook

## Quick Refs

```
B/R:  cheapest; slow
P/L:  cheap-ish; medium
W/S:  medium; fast
A/A:  expensive; instant
```

## Interview Prep

**Junior**: "Name the four DR strategies." — Backup & Restore (rebuild from backups, cheapest/slowest), Pilot Light (data live, compute provisioned on failover), Warm Standby (a scaled-down running copy), and Active/Active (full capacity in both regions, instant). Cost and recovery speed both rise down the list.

**Mid**: "What's the difference between Pilot Light and Warm Standby?" — Pilot Light keeps only the data layer running (DB replica) and brings compute up on disaster, so RTO is tens of minutes. Warm Standby keeps a *fully functional* but smaller stack always running, so RTO is minutes — you only scale up, you don't cold-start the application tier.

**Senior**: "How do you choose a strategy for a service?" — Take the service's tier and its RTO/RPO targets, then pick the cheapest strategy that still meets them: Active/Active only where RTO/RPO must be ~0, Warm Standby for minutes/seconds, Pilot Light for tens-of-minutes, Backup/Restore where hours are acceptable. The mistake is one strategy for everything.

**Staff**: "Design a tiered DR program for a platform." — Classify services into tiers, assign each the cheapest strategy meeting its RTO/RPO, and standardize the failover mechanics (DNS health checks for warm/pilot, conflict resolution and global tables for active/active). Then make it real: documented runbooks, quarterly drills measuring actual vs target, and explicit cost trade-offs so the business consciously funds active/active only where the value justifies the 2×+ spend.

## Next Topic

→ Move to [L27/C02 — HA Patterns](../C02/README.md)
