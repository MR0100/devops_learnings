# L26/C02/T02 — Showback vs Chargeback

## Learning Objectives

- Distinguish models
- Choose

## Showback

Show teams what they cost:
- Reports
- No actual financial impact
- Awareness

```
Team A: $50k/month
Team B: $30k/month
Team C: $20k/month
```

## Chargeback

Actually charge to team budget:
- Team's P&L hit
- Real accountability

## Why

### Showback
- Awareness
- Cultural shift
- Lower friction

### Chargeback
- Strong incentive
- Real accountability
- Aligned with business

## Maturity

Usually:
- Crawl: no visibility
- Walk: showback
- Run: chargeback

Years to mature.

## Implementation

### Showback
- Monthly report per team
- Dashboard access
- Trend over time

### Chargeback
- Internal transfer pricing
- Budget per team
- Real charge

## Pricing Models

### Direct
Team's actual usage = charge.

### Tier
- Free: < $X
- Tier 1: $X-Y
- Tier 2: > Y

### Allocated
Shared resources (e.g. K8s cluster):
- Per pod / vCPU consumed
- Or % of total

## Shared Resources

- Networking
- Logs
- Monitoring
- Shared cluster

Allocate:
- Usage proportion
- Equal share
- Skipped (overhead)

## Granularity

- Per service
- Per team
- Per product

## Frequency

- Daily
- Weekly
- Monthly

## Tools

- AWS Cost Categories
- Azure Cost Mgmt
- CloudHealth
- Vantage
- Apptio Cloudability

## Disputes

If team disputes charge:
- Audit
- Re-classify
- Update tags

## Examples

### Banking
Chargeback strict. Cost centers.

### SaaS
Mix; chargeback critical services.

### Many startups
Showback initially.

## Best Practices

- Start showback
- Move to chargeback gradually
- Clear allocation rules
- Dispute process
- Tooling supports

## Common Mistakes

- Skip to chargeback (team resistance)
- No allocation rules (chaos)
- No process for shared
- Stale tags (wrong charges)

## Quick Refs

```
Showback: see; no charge
Chargeback: pay
Maturity: Showback → Chargeback
```

## Interview Prep

**Mid**: "Showback vs chargeback."

**Senior**: "Implement."

**Staff**: "Org maturity."

## Next Topic

→ [T03 — Tools (CUR + Athena, CUDOS, Cloudability, Vantage)](T03-Cost-Tools.md)
