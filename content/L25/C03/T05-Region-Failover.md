# L25/C03/T05 — Region Failover

## Learning Objectives

- Test multi-region resilience
- Practice failover

## Why

Region failures rare but catastrophic:
- AWS us-east-1 outages happened
- DR tested annually minimum

## Simulated Failure

### DNS Failover
Switch DNS:
```bash
# Route 53 health check failover
```

### Block Traffic
At LB or edge:
```bash
# Cloudflare: block us-east-1 origin
```

### Stop Region
For non-prod:
- Stop all instances in region

## Goal

Verify:
- Traffic shifts to other region
- DB read replica promotes
- Cache warm-up
- App functions

## RPO / RTO

Measure:
- Data loss (RPO)
- Recovery time (RTO)

## Practice

Quarterly:
- Drill in lower env
- Annual: production

## Steps

```
1. Announce
2. Verify monitoring ready
3. Inject failure
4. Watch traffic shift
5. Verify app works
6. Restore region
7. Watch traffic shift back
8. Debrief
```

## Tools

- AWS Route 53 health checks
- Cloudflare Load Balancing
- App-level fallback

## Multi-Region Patterns

### Active-Active
Both regions serve:
- Switch instant (DNS / anycast)

### Active-Passive
Primary serves; standby ready:
- Promote on failure

## DB Failover

### Aurora Global
1-second cross-region.

### Read Replica
Manual promote.

### Backups
PITR cross-region.

## Caches Warm-Up

Cold cache → DB hit:
- Stampede risk
- Pre-warm if possible

## Testing

Read traffic:
- Easy to shift
- Lower risk

Write traffic:
- DB primary must shift
- Riskier

## Best Practices

- Quarterly drill
- Annual production
- Document RTO/RPO
- Test rollback too

## Common Mistakes

- Never test (don't work when needed)
- Only test reads (writes fail)
- DNS only (cache TTL slow)
- No comms

## Quick Refs

```
1. Plan
2. Communicate
3. Inject (DNS / block)
4. Verify
5. Restore
6. Debrief
```

## Interview Prep

**Senior**: "Region chaos."

**Staff**: "DR drill."

**Principal**: "Multi-region strategy."

## Next Topic

→ Move to [L25/C04 — Game Days](../C04/README.md)
