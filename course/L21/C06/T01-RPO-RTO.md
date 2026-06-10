# L21/C06/T01 — RPO & RTO for Databases

## Learning Objectives

- Define RPO and RTO
- Design for targets

## RPO

Recovery Point Objective: maximum tolerable data loss.

```
RPO = time of last good backup
```

For: business decision.

## RTO

Recovery Time Objective: maximum tolerable downtime.

```
RTO = time to restore service
```

## Examples

| Tier | RPO | RTO |
|---|---|---|
| Mission-critical | 0 (sync replica) | < 1 min |
| Critical | < 1 min | < 5 min |
| Important | < 15 min | < 1 hr |
| Standard | < 1 hr | < 4 hr |
| Backup-only | < 24 hr | days |

## RPO Implementations

### Sync Replica (RPO=0)
- Writes replicate sync
- No data loss on failover
- Slower writes

### Async Replica (RPO=seconds)
- Replicate asynchronously
- Lag = potential loss

### Continuous WAL Archive (RPO=minutes)
- WAL → S3 every ~5 min
- Restore to last WAL

### Daily Backup (RPO=24 hr)
- Snapshot daily
- Up to 24 hr loss

## RTO Implementations

### Hot Standby (RTO=seconds)
- Already running
- Failover instant
- IP / DNS swap

### Warm Standby (RTO=minutes)
- DB ready
- App startup time

### Cold Restore (RTO=hours)
- Restore from S3
- Apply WAL
- Start app

## Trade-Offs

Lower RPO/RTO = higher cost.

For: tier services; not all need same.

## Postgres Example

```
Primary (us-east-1)
├─ Sync standby (us-east-1b)   ← RPO=0; RTO=1 min
├─ Async standby (us-east-1c)
├─ Async standby (us-west-2)    ← RPO=10s; RTO=5 min (DR)
└─ WAL archive (S3)              ← RPO=5 min; RTO=hours
```

Layered.

## MySQL Example

```
Primary
├─ Semi-sync replica (same DC)  ← RPO=0
└─ Async replica (different DC)
+ XtraBackup daily              ← RPO=24 hr
+ Binlog archive                ← RPO=5 min
```

## Auto-Failover

Tools:
- Patroni (PG)
- MySQL Group Replication
- AWS RDS Multi-AZ

For: low RTO.

## Test Failover

Quarterly:
- Simulate primary failure
- Measure RTO
- Verify RPO

For: known performance.

## Backup Compliance

- Encrypted
- Cross-region
- Retention per policy
- Tested

## Cost

For low RPO/RTO:
- More replicas
- Sync replication
- More infra

Justify per tier.

## Multi-Region

For region failure:
- Cross-region replica
- Higher RTO due to DNS
- Higher RPO (async lag)

## Manual Process

If automated fails:
- Documented runbook
- Practiced quarterly
- 24/7 on-call

## Real Examples

### Bank (Mission-Critical)
RPO=0, RTO<1 min.

### SaaS
RPO=1 min, RTO<10 min.

### Internal Tool
RPO=24 hr, RTO=4 hr.

## Best Practices

- Define per service
- SLO matches RPO/RTO
- Test regularly
- Document
- Tooling for failover

## Common Mistakes

- One RPO for all
- No test
- Manual failover (slow)
- Cross-region untested

## Quick Refs

```
RPO: data loss tolerable
RTO: downtime tolerable

Sync replica: RPO=0
Async replica: RPO=seconds
WAL archive: RPO=minutes
Daily backup: RPO=24 hr

Hot standby: RTO=seconds
Warm: RTO=minutes
Cold: RTO=hours
```

## Interview Prep

**Mid**: "RPO vs RTO."

**Senior**: "Implement for service."

**Staff**: "Tiered DR."

## Next Topic

→ [T02 — Point-in-Time Recovery](T02-PITR.md)
