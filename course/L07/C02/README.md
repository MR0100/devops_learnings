# L07/C02 — Cloud Economics

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-CapEx-OpEx.md) | CapEx vs OpEx | 0.5 hr |
| [T02](T02-Pricing-Models.md) | Pricing Models (On-Demand, Reserved, Spot, Savings Plans) | 1 hr |
| [T03](T03-TCO.md) | Total Cost of Ownership | 0.5 hr |

## CapEx vs OpEx

**CapEx (Capital Expenditure)**:
- Buy hardware, depreciate over years
- Upfront cost, predictable, slow to scale
- On-prem datacenters
- Tax: depreciation

**OpEx (Operating Expenditure)**:
- Pay-as-you-go
- Variable cost, fast to scale
- Cloud
- Tax: fully deductible same year (usually)

Most companies shifted CapEx → OpEx with cloud. Some hyperscalers (Meta, Google) now move back to CapEx for their own DCs at huge scale (cost optimization).

## Pricing Models

### On-Demand
- Standard hourly/second pricing
- No commitment
- Flexible, expensive
- Use: variable workloads, dev/test

### Reserved Instances (RI)
- Commit to instance type + region + 1 or 3 years
- ~30-50% off On-Demand
- Standard (no flexibility) vs Convertible (can change family)
- Use: stable, predictable baseline workloads

### Savings Plans (AWS)
- Commit to $X/hour for 1 or 3 years
- More flexible than RIs (any instance family, region, OS)
- Up to ~72% off
- Use: stable workloads, broad applicability

### Spot Instances
- Bid on spare capacity
- 60-90% off On-Demand
- Can be reclaimed with 2-minute warning
- Use: fault-tolerant batch, CI runners, K8s scale-out

### Free Tier
- Limited resources free for 12 months (AWS) or always (some)
- Use: dev, learning

## Reserved / Savings Plans Strategy

```
Always-on baseline → 1-year Savings Plan (60% discount)
Predictable growth → additional 1-year SP each quarter
Peak surge        → On-Demand
Batch / async      → Spot
Spike unpredictable → On-Demand auto-scaling
```

Aim for ~70-80% commitment coverage; leave room for flexibility.

## TCO Calculation

```
TCO = (CapEx_cloud + OpEx_cloud) - (savings from automation, agility, time-to-market)
vs
TCO = (CapEx_onprem + OpEx_onprem) - (savings from owning at scale)
```

Hidden cloud costs:
- Egress (often huge)
- Cross-AZ
- Inter-region replication
- Load balancer hours + GB processed
- NAT Gateway
- Logging (Datadog ingest, CloudWatch)
- Idle resources

Hidden on-prem costs:
- Power + cooling
- DC rent
- Hardware refresh cycle
- 24×7 ops team
- Software licenses (VMware, RHEL)
- Capacity planning over-provision

## Reserved vs Spot Decision

| Workload | Best |
|---|---|
| Production web tier (stable load) | RI / SP |
| Batch jobs, ML training | Spot |
| CI/CD runners | Spot + small On-Demand fallback |
| Database (stateful) | RI / SP |
| Dev/test | Spot or On-Demand with auto-stop |

## Common Cost Anti-Patterns

- Forgot to terminate dev resources
- Snapshot collection growing unbounded
- Idle load balancers
- Unattached EBS volumes
- Logs retained forever
- Inter-AZ chatter for microservices
- NAT Gateway data processing for high-egress workloads
- Always-on test environments

## Interview Themes

- "Compare On-Demand, Reserved, Savings Plans, Spot"
- "When Spot? When not?"
- "Walk through cloud TCO vs on-prem"
- "Hidden costs in cloud bills"
- "Strategy to commit to RIs without overcommitting"
