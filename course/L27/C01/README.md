# L27/C01 — DR Fundamentals

## Topics

- **T01 RTO, RPO, MTD** — Recovery quantifications
- **T02 DR Strategies** — Backup/Restore, Pilot Light, Warm Standby, Active/Active

## RTO, RPO, MTD

- **RTO (Recovery Time Objective)**: max time to restore service
- **RPO (Recovery Point Objective)**: max data loss tolerable
- **MTD (Maximum Tolerable Downtime)**: business-defined hard limit

Typical:
| Tier | RTO | RPO |
|---|---|---|
| Tier 1 (revenue critical) | < 15 min | < 1 min |
| Tier 2 (important) | < 4 hours | < 1 hour |
| Tier 3 (other) | < 1 day | < 1 day |

## The Four DR Strategies

### 1. Backup & Restore
```
Primary running
Backups to remote location (S3)
On disaster: restore from backup → start new infrastructure
```

- **Cost**: low (storage only)
- **RTO**: hours-days
- **RPO**: backup interval (~hours)
- **Use**: cold tier, less critical data

### 2. Pilot Light
```
Primary running fully
Minimal core running in DR (DB replicated; idle compute)
On disaster: scale up DR compute → traffic to DR
```

- **Cost**: moderate
- **RTO**: tens of minutes
- **RPO**: seconds (async replication) to zero (sync)
- **Use**: Tier 2 services

### 3. Warm Standby
```
Primary running fully
Reduced-capacity copy running in DR
On disaster: scale up + cut over
```

- **Cost**: moderate-high (paying for partial DR capacity)
- **RTO**: minutes
- **RPO**: seconds
- **Use**: Tier 1 with budget constraint

### 4. Active/Active
```
Two regions both serving traffic
Data replicated bi-directionally
On regional loss: surviving region absorbs all traffic
```

- **Cost**: high (2× capacity)
- **RTO**: ~zero
- **RPO**: near-zero
- **Use**: Tier 0, no-downtime products

## Comparison

| Strategy | RTO | RPO | Cost |
|---|---|---|---|
| Backup/Restore | Hours-Days | Hours | Low |
| Pilot Light | Tens of min | Sec-Min | Medium |
| Warm Standby | Minutes | Seconds | Med-High |
| Active/Active | Near zero | Near zero | High |

## Choosing

Match strategy to service tier. Don't over-engineer Tier 3 services.

## Beyond Disaster Recovery

DR addresses regional failure. But also:
- AZ failure (multi-AZ within region)
- Node / pod failure (K8s handles)
- App bug / config error (logical failures)
- Data corruption (need historical backups)
- Ransomware (need immutable backups)

A complete plan covers all.

## DR vs HA

| | HA | DR |
|---|---|---|
| Scope | Within region | Cross-region |
| Failures handled | Hardware, AZ | Regional, datacenter |
| Cost | Multi-AZ | Multi-region (×2) |
| Strategy | Built-in (Multi-AZ DBs, ASG) | Explicit (replication, failover) |

## Components of a DR Plan

1. **Architecture** — replication, failover, traffic shifting
2. **Runbook** — step-by-step procedure
3. **Communication plan** — internal + external comms
4. **Testing schedule** — quarterly drills
5. **Recovery criteria** — when do we declare disaster?
6. **Failback procedure** — recover from DR back to primary

## DR is a Process, Not Tech

Tech is necessary but insufficient:
- Drilling
- Documentation
- Team familiarity
- Clear decision criteria
- Authority for failover (who decides?)

Many DR fails because:
- Backup never tested
- Runbook outdated
- Authority unclear
- Communication breaks

## Failover Authority

Who declares disaster and triggers failover?
- VP Engineering / CTO for major
- On-call engineer for tier-3
- Automated for some (DNS failover on health check)

Document. Practice.

## Failback

After primary recovers:
- Recovery may need data sync back (DR → primary)
- Traffic cutover back
- Run primary + DR in sync for a period
- Verify before declaring "back to normal"

## Common Mistakes

- "We have backups" — but never tested restore
- "We're Multi-AZ" — but DB is single-region
- DR runbook references services that no longer exist
- No clear authority for failover
- Backups encrypted with key only the lost region has access to
- DNS TTL too long for failover speed

## Interview Themes

- "RTO vs RPO"
- "Four DR strategies — compare"
- "Pick a DR strategy for X service"
- "Test DR — strategies"
- "Authority for failover"
