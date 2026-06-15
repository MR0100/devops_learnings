# L27/C04/T03 — Failover Automation

## Learning Objectives

- Automate failover
- Avoid risks

## Why Automate

- Speed (less RTO)
- Reduce human error
- 24/7 (off-hours)
- Less stress

## Why Not (Sometimes)

- False positives → unnecessary failover
- Complex failures (need judgment)
- Manual control feels safer

For: hybrid usually.

## Stages

### Manual
Page on-call; engineer decides; executes.
RTO: 30+ min.

### Semi-Auto
Page; engineer confirms; auto-execute.
RTO: 5-15 min.

### Auto
Detect → execute.
RTO: 1-5 min.

## Tools

- Patroni (Postgres)
- Group Replication (MySQL)
- AWS Aurora (auto failover Multi-AZ)
- Spanner / Cockroach (native)
- Route 53 health checks
- Custom

## Components

### Detection
Health checks.

### Decision
Should we failover?
- Severity?
- Just transient?

### Execute
- Promote replica
- Update DNS / config
- Verify

### Notify
Engineers informed.

## Risks

### Flapping
Primary recovers → flap.

Mitigation: cooldown after failover; manual recover.

### Split Brain
Both think they're primary.

Mitigation: quorum, fencing.

### Data Loss
Promoting async replica.

Mitigation: wait for replication; or accept.

## Confirm

For some failovers:
- Auto-detect + suggest
- Human confirms
- Then execute

For: balance.

## Practice

Quarterly:
- Drill auto-failover
- Verify
- Tune

## DR Playbook

```markdown
## Auto Failover

Trigger:
- Health check failure 3x consecutive (90 sec)
- Multiple checkers agree

Action:
1. Mark primary unhealthy
2. Promote replica
3. Update Route 53 record
4. Notify Slack + page
5. Wait 10 min cooldown before considering recovery

Manual override:
- /failover stop
- /failover force-region us-west-2
```

## Examples

### Aurora Multi-AZ
Auto-failover; ~30 sec RTO.

### Patroni
Postgres HA; auto.

### Route 53 + ALB
DNS-level auto.

## Best Practices

- Quorum
- Cooldown
- Manual override
- Notification
- Practice

## Common Mistakes

- No flapping protection
- Auto without test
- No notification (silent)
- Override missing

## Quick Refs

```
Detection → Decision → Execute → Notify
Cooldown after failover
Manual override always
```

## Interview Prep

**Junior**: "Why automate failover?" — To cut RTO and remove human latency: an automated system detects and cuts over in 1–5 minutes, any time of day, instead of waiting to page an engineer who decides and executes in 30+ minutes. The trade-off is the risk of false positives.

**Mid**: "Auto vs semi-auto vs manual — when each?" — Auto (detect→execute) for low-risk, well-understood failures like AZ-level DB failover where speed matters most. Semi-auto (detect→page→human confirms→execute) for region-level cutover where a false positive is expensive. Manual for rare, high-judgment cases. Most orgs run a hybrid: auto at AZ level, semi-auto at region level.

**Senior**: "What are the main risks of automated failover and how do you mitigate them?" — Flapping (primary recovers and traffic oscillates) — mitigate with a cooldown and not auto-recovering; split-brain (both nodes think they're primary) — mitigate with quorum and fencing; and data loss from promoting an async replica — wait for replication to catch up or explicitly accept the RPO. Always keep a manual override and notify so the failover isn't silent.

**Staff**: "Design an automated failover system that's safe to trust." — Layer it: multiple independent health checkers must agree before acting (no single false positive triggers it), require quorum to decide the new primary and fencing/STONITH to stop the old one (preventing split-brain), enforce a cooldown to stop flapping, never auto-fail-back, and always expose a manual override (`/failover stop`, `/failover force-region`). Then prove it with quarterly drills measuring actual RTO/RPO, because an untested automated failover is more dangerous than a manual one.

## Next Topic

→ [T04 — Split-Brain, Fencing & Failback](T04-Split-Brain-Fencing-Failback.md)
