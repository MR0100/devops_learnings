# L07/C02/T02 — Pricing Models (On-Demand, Reserved, Spot, Savings Plans)

## Learning Objectives

- Pick the right model per workload
- Estimate savings

## On-Demand

Pay per second / hour. No commitment.

Use: dev/test, unpredictable, short-lived.

Price: list. Most expensive.

## Reserved Instances (RIs)

Commit 1 or 3 years. Discount 30-72%.

AWS variants:
- **Standard RI**: locked to instance type/family
- **Convertible RI**: can switch family later
- **Regional RI**: applies to any AZ in region
- **Zonal RI**: capacity reservation in specific AZ

Payment options: No Upfront, Partial, All Upfront (bigger discount).

Use: steady workloads.

## Savings Plans (AWS)

Commit $X/hour for 1 or 3 years.

Variants:
- **Compute Savings Plans**: 66% off; flexible across EC2, Fargate, Lambda; any region/family
- **EC2 Instance Savings Plans**: 72% off; specific family + region

More flexible than RIs; preferred now.

## Spot Instances

Use spare AWS capacity; up to 90% off; can be reclaimed with 2-min notice.

Use: batch, fault-tolerant, stateless, K8s nodes (with checkpointing).

Avoid: production DBs, primary state.

```
EC2 Spot: 60-90% off
GCP Preemptible: 60-91% off; max 24h
Azure Spot: similar
```

## Spot Strategies

- Diversify across instance types/AZs (one type's price spike doesn't kill all)
- Mixed: on-demand for baseline, spot for surge (ASG with mixed instance policy)
- Fleet: AWS picks cheapest matching specs
- Capacity-Optimized: AWS picks where most capacity (less interruption)

## Free Tier

Permanent:
- AWS: small Lambda, DynamoDB, S3
- GCP: small VM, small storage
- Azure: small VM, storage

12-month:
- AWS: 750 hr t2.micro
- GCP: $300 credit
- Azure: $200 credit + 12 months free

Great for learning; thin for real apps.

## Pricing Per Service

### EC2
- per second (Linux); per hour (Windows)
- + EBS storage / IOPS
- + Data transfer
- + Load Balancer

### S3
- $0.023/GB/mo standard
- Cheaper tiers for cold (Glacier $0.004)
- $0.005/1000 GET, $0.005/1000 PUT
- Egress: $0.09/GB

### Lambda
- $0.20 per 1M requests
- $0.0000166667 per GB-second
- 1M req × 1s × 1GB = $16.87

### RDS
- per instance-hour
- + storage / IOPS
- Backup storage
- Multi-AZ doubles cost

### DynamoDB
- Provisioned: per RCU/WCU
- On-demand: per request
- Plus storage

## Data Transfer

The hidden cost:
- Within AZ: free
- Cross-AZ: $0.01/GB each way
- Within region: free for some services
- Cross-region: $0.02-0.09/GB
- To Internet: $0.09/GB (first 10 TB)
- From Internet: free
- Via CloudFront to internet: cheaper

Many "cheap" architectures fail when egress is computed.

## Cost Tools

### AWS
- Cost Explorer: trends, forecasts
- Cost & Usage Report (CUR): detailed
- Budgets: alerts on threshold
- Trusted Advisor: savings recommendations
- Compute Optimizer: right-sizing

### Azure
- Cost Management: analyze, budget
- Advisor: recommendations

### GCP
- Billing Console: trends
- Budgets & Alerts
- Recommender

### Third-Party
- CloudHealth (VMware)
- Cloudability (Apptio)
- Vantage
- Spot.io (RIs + Spot mgmt)
- Kubecost (K8s specific)
- ProsperOps (RI automation)

## Optimization Levers

| Lever | Savings |
|---|---|
| Reserved/Savings Plans | 30-72% |
| Right-sizing (drop instance size) | 20-50% |
| Spot (where applicable) | 60-90% |
| Off-hours shutdown (dev) | 60% |
| Auto-scaling (vs always-max) | 30-50% |
| Storage tiering (cold to Glacier) | 90% |
| Delete idle / orphaned | varies |
| Compress logs / data | varies |

Layered: applied together, 60-80% off list common.

## RIs vs Savings Plans

RIs:
- Specific instance family
- Bigger discount on All-Upfront Standard
- Less flexible

SPs:
- More flexible (Compute SP covers everything)
- Slightly less discount but easier to fully utilize
- Recommended for most

## Commitment Math

App needs 100 vCPU 24/7.

On-demand: $7,300/mo
1-yr SP (30% off): $5,110/mo
3-yr SP, all upfront (66% off): $2,482/mo

Saving: $58k/year for 3-yr.

Risk: if usage drops, still pay.

Strategy: reserve baseline; on-demand for surge.

## Common Mistakes

- 100% RI/SP for elastic workloads → over-commit waste
- Unused RIs (not converted)
- Letting RIs expire (drop to on-demand)
- Spot for stateful (lose data on interruption)

## Sample Plan

Production e-commerce:
- 60% on Savings Plans (steady baseline)
- 30% on-demand (variable)
- 10% on Spot (batch jobs, dev)

Result: 40-50% off list.

## Best Practices

- Layer pricing to the load shape: Savings Plans/RIs for the always-on baseline, on-demand for variable demand, Spot for fault-tolerant batch/surge.
- Prefer Compute Savings Plans over Standard RIs for most fleets — the flexibility across family/region/Fargate/Lambda makes them easier to fully utilize.
- Diversify Spot across instance types and AZs and use capacity-optimized allocation to minimize interruptions.
- Model data-transfer costs (cross-AZ, cross-region, egress) into every architecture — they sink many "cheap" designs.
- Right-size and schedule off-hours shutdowns for non-prod; combine levers (reserve + right-size + tier storage) for 60–80% off list.
- Review SP/RI coverage and utilization monthly and treat unused commitments as a bug to fix.

## Quick Refs

Pricing model selector:

| Workload | Model |
|---|---|
| Dev/test, unpredictable, short-lived | On-demand |
| Steady 24/7 baseline | Savings Plans / Reserved (1 or 3 yr) |
| Fault-tolerant batch, stateless, surge | Spot / Preemptible |
| Capacity guarantee in a specific AZ | Zonal RI / capacity reservation |

Discount ranges (AWS): On-demand 0% · 1-yr SP ~30% · 3-yr SP/RI up to 66–72% · Spot up to 90%.

Optimization levers (apply together):

| Lever | Typical savings |
|---|---|
| Savings Plans / RIs | 30–72% |
| Right-sizing | 20–50% |
| Spot (where applicable) | 60–90% |
| Off-hours shutdown (dev) | ~60% |
| Storage tiering to Glacier | up to 90% |

## Interview Prep

**Mid**: "RI vs Spot vs On-demand."

**Senior**: "Optimize $1M/mo bill — strategy."

**Staff**: "Savings Plans portfolio for multi-team org."

## Next Topic

→ [T03 — Total Cost of Ownership](T03-TCO.md)
