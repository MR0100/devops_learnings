# L27/C01/T02 — DR Strategies

## Learning Objectives

- Compare 4 DR strategies
- Pick by needs

## The Four

1. Backup & Restore
2. Pilot Light
3. Warm Standby
4. Active/Active

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

Per service tier:
- Tier 1 (critical): Active/Active
- Tier 2 (important): Warm Standby
- Tier 3 (standard): Pilot Light
- Tier 4 (low): Backup/Restore

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

**Mid**: "DR strategies."

**Senior**: "Pick strategy."

**Staff**: "Tiered DR."

## Next Topic

→ Move to [L27/C02 — HA Patterns](../C02/README.md)
