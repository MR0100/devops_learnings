# L26/C03/T02 — Reserved Instances & Savings Plans

## Learning Objectives

- Use RIs / SPs
- Maximize discount

## Reserved Instance (RI)

Commit 1 or 3 years:
- Discount 30-72%
- Specific instance type

## Savings Plan (SP)

Commit $ / hour for 1 or 3 yr:
- Discount similar
- Flexible (any size / family)

## Compare

| | RI | SP |
|---|---|---|
| Commit | instance | dollar |
| Flexibility | low | high |
| Discount | 30-72% | 30-72% |
| Use | stable workload | mixed |

For: SP for flexibility.

## Compute Savings Plan

Any EC2 / Fargate / Lambda:
- Highest flexibility
- Slightly less discount

## EC2 Instance SP

Specific family + region:
- More discount
- Less flexibility

## Buy

```bash
aws savingsplans create-savings-plan \
  --savings-plan-offering-id ... \
  --commitment 100
```

## Coverage

Goal: ~70-80% covered:
- Don't over-commit (waste if unused)
- Don't under-commit (pay on-demand)

For: leave room for variability.

## Tools

- AWS Compute Optimizer (recommendations)
- ProsperOps (auto-managed)
- Vantage / CloudHealth recommendations

## ProsperOps

Auto-buys / sells RIs/SPs:
- Optimize portfolio
- Continuous
- Fee per saved $

For: hands-off.

## When 1yr vs 3yr

### 1 yr
- Less commitment
- Worse discount

### 3 yr
- Better discount
- More commitment

For: stable workloads: 3 yr. For uncertain: 1 yr.

## Payment Options

### All Upfront
Most discount.

### Partial Upfront
Some discount.

### No Upfront
Spread over term.

For: cash flow vs discount.

## Reserved Capacity

For specific:
- RDS RI
- Redshift RI
- ElastiCache RI
- OpenSearch RI

Per service.

## Azure

Reservations: similar.
Hybrid Benefit: Windows / SQL Server licenses.

## GCP

Committed Use Discount:
- 1 yr / 3 yr
- vCPU + memory commit
- 30-70% off

Flexible Committed Use:
- More flexible

## Coverage Reports

```sql
SELECT 
  date_trunc('day', usage_start_date) AS day,
  SUM(reservation_amortized_upfront_cost_for_usage) AS ri_cost,
  SUM(line_item_unblended_cost) AS total_cost
FROM cur
WHERE pricing_term = 'Reserved'
GROUP BY day
```

For: track.

## Best Practices

- Cover 70-80%
- Mix RI + SP
- Tool-assisted (ProsperOps)
- Review quarterly
- Adjust for growth

## Common Mistakes

- 100% coverage (waste on idle)
- 0% coverage (full on-demand)
- Wrong type
- Forget to renew

## Quick Refs

```bash
# AWS
aws savingsplans / aws ec2 describe-reserved-instances

# Coverage
aws ce get-savings-plans-coverage
aws ce get-reservation-coverage
```

## Interview Prep

**Mid**: "RI vs SP."

**Senior**: "Coverage strategy."

**Staff**: "Commit optimization."

## Next Topic

→ [T03 — Spot Instances (and Karpenter Strategy)](T03-Spot.md)
