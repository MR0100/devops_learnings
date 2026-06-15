# L07/C02/T01 — CapEx vs OpEx

## Learning Objectives

- Understand the financial shift cloud causes
- Speak finance/CFO language

## Definitions

**CapEx (Capital Expenditure)**: large upfront purchase; asset depreciates over years.
- Buy servers $1M
- Use for 5 years
- $200k/year depreciation

**OpEx (Operating Expenditure)**: ongoing operating cost; tax-deductible immediately.
- Rent cloud: $20k/month
- $240k/year, expensed immediately

## Why It Matters

CFOs care because:
- CapEx: hits balance sheet; financed; depreciated over years
- OpEx: hits income statement; immediate expense; affects margins

**Cash flow**: OpEx is monthly bills; CapEx is one big payment.

**Predictability**: CapEx is fixed; OpEx varies with usage.

## Cloud Shifts to OpEx

Traditional:
- Buy server: $5k CapEx
- Use for 5 years
- Cost amortized

Cloud:
- Rent equivalent: ~$200/mo OpEx
- 5 years = $12k
- More expensive in raw $ but no upfront commitment

## Why Companies Like OpEx Cloud

- No upfront capital
- Scale up/down
- No DC mgmt overhead
- Tax benefits in some structures
- Predictable per-unit cost

## Why Some Prefer CapEx

- After scale, owning cheaper
- Predictable monthly
- Asset on balance sheet
- Less variable

## Hidden Cloud Costs

Cloud bills often surprise:
- Data egress
- IOPS on storage
- Inter-region traffic
- Idle resources (forgotten test envs)
- Over-provisioned (10× what's needed)

Without governance: 30-50% waste typical.

## TCO Comparison

For 100 VMs running 24/7 for 5 years:
- DC: build → $1M upfront + $500k/year ops = $3.5M
- Cloud on-demand: $2k/mo × 100 × 60 mo = $12M
- Cloud reserved 3yr: $500/mo × 100 × 60 = $3M

Cloud cheap if right pricing model. Expensive if naive.

## Cloud Sweet Spot

Cloud wins when:
- Variable load (peaks vs valleys)
- Geographically distributed
- New features fast
- Managed services valued

Cloud loses when:
- Steady 24/7 load at huge scale
- Latency / locality critical
- Existing DC sunk cost

## Reservation Strategies

To shift cloud OpEx toward CapEx-like commitment:
- AWS Reserved Instances: 1 or 3 year commit; 30-72% discount
- AWS Savings Plans: flexible commit; similar discount
- GCP Committed Use: 1 or 3 year; ~30-57% off
- Azure Reserved VM: 1 or 3 year; up to 72% off

Trade flexibility for cost. Predict usage; reserve.

## Spot / Preemptible

Lowest tier:
- AWS Spot: up to 90% off; instance can be reclaimed
- GCP Preemptible: up to 80% off; 24h max
- Azure Spot: variable discount

For: batch, stateless, fault-tolerant.

## Free Tier

Each cloud has free tier (12 months or always-free):
- Small VM hours
- Limited storage
- Some Lambda invocations

Useful for learning; useful for tiny side projects.

## Discount Programs

- Enterprise agreements (EA, EDP): negotiated discounts
- Migration credits (AWS MAP, Azure migrate)
- Startup credits (each provider)
- Customer-specific deals

Large customers negotiate 10-40% off list.

## Showback vs Chargeback

For multi-team orgs:
- **Showback**: tell each team their cost (visibility)
- **Chargeback**: each team's budget gets debited

Tagging is critical for both.

## FinOps Movement

Discipline for cloud cost mgmt:
- Visibility (dashboards per team)
- Optimization (RI coverage, right-sizing)
- Operate (continuous improvement)

FinOps Foundation; FinOps Certified Practitioner cert.

## Reserved vs On-Demand Math

App needs 10 servers 24/7.
- On-demand: 10 × $200/mo = $24,000/yr
- 1-yr RI (30% off): 10 × $140 × 12 = $16,800/yr (save $7,200)
- 3-yr RI (50% off): 10 × $100 × 12 = $12,000/yr (save $12,000)

For burst (avg 5, peak 15):
- 5 RI + 5-10 on-demand
- RI base; on-demand for surge

## Common Mistakes

- All on-demand (most expensive)
- Over-reservation (paying for unused)
- No tagging (can't track)
- Idle test envs running 24/7
- Over-provisioned (4× CPU you need)
- No alerts on bill spike

## Tools

- AWS Cost Explorer, Trusted Advisor
- Azure Cost Management
- GCP Billing
- Vendor tools: CloudHealth, Cloudability, Vantage, ProsperOps, Spot.io

## Best Practices

- Cover steady, predictable baseline load with reservations/Savings Plans (CapEx-like commitment) and burst with on-demand; reserve only what you're confident you'll run.
- Tag every resource (team, env, app, cost-center) from day one — without tags, showback/chargeback and accountability are impossible.
- Run spot/preemptible for fault-tolerant, stateless, batch workloads to capture up to ~90% savings.
- Right-size continuously and kill idle/forgotten resources (test envs, unattached volumes, orphaned IPs) — 30–50% waste is typical without governance.
- Set billing alerts and anomaly detection so a spike is caught in hours, not at the end of the month.
- Establish a FinOps practice (visibility → optimization → operate) and review RI/SP coverage and utilization regularly.

## Quick Refs

CapEx vs OpEx at a glance:

| | CapEx | OpEx |
|---|---|---|
| Payment | Large upfront | Ongoing monthly |
| Accounting | Balance sheet, depreciated | Income statement, immediate |
| Predictability | Fixed | Varies with usage |
| Cloud fit | Owned DC / reservations | On-demand cloud |

Commitment ladder (cheapest → most flexible):

| Option | Discount | Trade-off |
|---|---|---|
| Spot / Preemptible | up to 90% | Can be reclaimed any time |
| 3-yr Reserved / Committed Use | up to ~72% | Long lock-in |
| 1-yr Reserved / Savings Plan | ~30–40% | Shorter commitment |
| On-demand | 0% | Full flexibility, highest price |

Rule of thumb: reserve the baseline you'd run anyway; never reserve speculative growth.

## Interview Prep

**Mid**: "CapEx vs OpEx."

**Senior**: "Cloud bill out of control — what to investigate."

**Staff**: "Build FinOps program for org."

## Next Topic

→ [T02 — Pricing Models](T02-Pricing-Models.md)
