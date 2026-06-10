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

**Mid**: "Failover automation."

**Senior**: "Risks."

**Staff**: "DR strategy."

## Next Topic

→ Move to [L27/C05 — Backups That Actually Work](../C05/README.md)
