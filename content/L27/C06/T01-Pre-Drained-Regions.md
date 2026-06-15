# L27/C06/T01 — Pre-Drained Regions

## Learning Objectives

- Drain regions
- Plan evacuation

## Pre-Drain

Before maintenance / known event:
- Move traffic out
- Region quieter
- Easier maintenance

For: planned operations.

## Why

- Maintenance window
- AWS regional event
- Known issue

Better than auto-failover under stress.

## How

```
1. Notify
2. Gradually shift DNS / weights
3. Drain connections
4. Verify other regions handle load
5. Maintain
6. Restore
```

## Tools

- Route 53 weighted records
- AWS Global Accelerator weights
- Cloudflare load balancing

## Example

```bash
# Weighted gradually
aws route53 update-record \
  --primary-weight 80 --secondary-weight 20

# Then
aws route53 update-record \
  --primary-weight 50 --secondary-weight 50

# ...
aws route53 update-record \
  --primary-weight 0 --secondary-weight 100
```

## Practice

Periodic:
- Drain region for an hour
- Verify works
- Restore

For: muscle memory.

## Cross-AZ Drain

Same concept within region:
- Drain AZ
- Maintain
- Restore

## Capacity Plan

Other regions:
- Can handle load?
- Pre-provision?

For: not overwhelm.

## Comms

- Engineers notified
- Customer-facing if impact
- Status page

## Tools / Automation

- Scripts
- Runbook
- Auto via metric

## Best Practices

- Practice
- Capacity planned
- Gradual shifts
- Monitor during

## Common Mistakes

- Sudden 100% shift (other region overwhelmed)
- No comm
- No practice

## Quick Refs

```
Pre-drain: planned shift out
Gradual: 80 → 50 → 20 → 0
Practice: periodic
```

## Interview Prep

**Senior**: "Pre-drain."

**Staff**: "Region operations."

## Next Topic

→ [T02 — Traffic Steering](T02-Traffic-Steering.md)
