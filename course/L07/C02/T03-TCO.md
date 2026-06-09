# L07/C02/T03 — Total Cost of Ownership

## Learning Objectives

- Compute TCO realistically
- Compare cloud vs on-prem

## TCO Components

### Compute
- Instance hours / reserved commitments
- License (Windows, SQL Server)

### Storage
- Volume size × $/GB
- IOPS / throughput tier
- Snapshots
- Backup retention

### Network
- Egress
- Inter-region
- Load balancer hours + LCUs
- NAT gateway hours + data
- VPN, Direct Connect

### Services
- DB (RDS instance + storage + IOPS)
- Queue (SQS per request)
- CDN (per GB)
- Lambda (per invocation + duration)
- Monitoring (CloudWatch)
- Secrets (Secrets Manager: $0.40/secret/mo)
- KMS keys: $1/mo + API calls

### Operations
- DevOps engineers
- 24/7 oncall
- Incident response

### Indirect
- Training
- Compliance audits
- Tools (Datadog, Splunk, etc.)
- DR drills

## On-Prem TCO

Often forgotten:
- Hardware ($)
- Hardware refresh every 3-5 years
- Power
- Cooling
- DC space rent
- Bandwidth
- Network equipment
- Hardware techs
- 24/7 NOC
- Disaster site

Industry rule: hardware = ~30% of TCO; rest is ops.

## Cloud TCO

- Compute
- Storage
- Network
- Managed services
- Less ops (provider handles base)
- Still: DevOps team
- Still: oncall
- Tools (CloudWatch, etc.)
- Egress (often 10-20% of bill)

## Comparison Example

Scenario: 500 VMs running 24/7 for 5 years.

### On-Prem
- Servers: $1M
- Refresh year 4: $1M
- Power/cooling: $200k/yr × 5 = $1M
- DC space: $100k/yr × 5 = $500k
- Network: $50k/yr × 5 = $250k
- Staff (5 sysadmins): $750k/yr × 5 = $3.75M
- Total: ~$7.5M

### Cloud (Reserved 3yr SP, refreshed)
- 500 × $100/mo × 60 = $3M (SP 3yr)
- Storage: $50k/yr × 5 = $250k
- Egress: $100k/yr × 5 = $500k
- Managed services: $50k/yr × 5 = $250k
- Staff (3 SREs): $500k/yr × 5 = $2.5M
- Total: ~$6.5M

Cloud slightly cheaper, plus elasticity, plus features.

### Cloud (On-Demand naive)
- 500 × $300/mo × 60 = $9M
- + everything else
- Total: ~$12M (more than on-prem)

Lesson: cloud needs governance.

## Hidden Costs

### Egress
$0.09/GB. If users download:
- 10 TB/mo to Internet = $900/mo = $11k/yr
- 1 PB/mo = $90k/mo = $1M/yr

CDN reduces (CloudFront cheaper after volume).

### Cross-AZ
For HA, you replicate across AZs. $0.01/GB each way:
- 1 TB/day replication = $20/day = $7k/yr per relationship

### Idle Resources
Test environments at night. Dev forgets EBS volume. Snapshot retention forever.

Estimate: 20-40% of bill is idle.

### Premium Support
AWS support: 3-10% of bill. Required for many enterprise SLAs.

## Cost per Customer / Unit

Cleanest metric: $$ per customer per month, or per million requests.

```
$50k/mo cloud bill
1M MAU
= $0.05 per MAU per month
```

Track over time. Goal: trend down (better efficiency or scaling benefit).

## When Cloud Loses

- Steady, predictable load at huge scale
- Existing DC sunk
- Latency-sensitive (cloud region too far)
- Data sovereignty
- High data transfer
- Specialty hardware (gov, military)

Dropbox famously moved off S3 → saved $75M/yr.

## When Cloud Wins

- New product (no DC investment)
- Variable load
- Need global presence
- Managed services valuable
- Team is small

For most startups: cloud is clearly right.

## Optimization Process

1. **Tag everything**: team, env, project
2. **Measure**: monthly review per team
3. **Right-size**: Compute Optimizer recommendations
4. **Reserve baseline**: SP/RI
5. **Shut off idle**: stop test envs at night
6. **Use cheaper tiers**: S3 IA, Glacier
7. **Egress**: review; CDN; compress
8. **Manage**: cron job to clean orphaned

Run quarterly. Saves 30-50% over time.

## FinOps Personas

- Engineer: builds, knows what's needed
- Finance: budgets, forecasts
- FinOps: bridges; reports, governance

Tag culture across all.

## SaaS / Managed Service ROI

Comparison: build vs buy.

Datadog: $25-100/host/mo.
Self-hosted (Prometheus+Grafana+Loki+Tempo): "free" but
- 1-2 SREs to operate
- Storage at scale
- Indexing/query infrastructure

At 100 hosts: Datadog ~$50k/yr; self-host ~$300k/yr (with people).

At 10,000 hosts: Datadog $5M/yr; self-host $500k-$1M. Flips.

Calculate at your scale.

## Common Mistakes

- "Cloud is cheap" assumption (it's not, without management)
- Lift-and-shift (1:1 from DC) → most expensive way
- No tagging → no visibility
- Production-sized dev/test
- Ignoring egress
- Over-committing on RI

## TCO Calculators

- AWS Pricing Calculator (per service)
- AWS Migration Hub Calculator (for migrating)
- TCO Calculator (high-level cloud vs on-prem)
- Azure / GCP equivalents

Useful for ballpark. Real bills always surprise.

## Interview Prep

**Mid**: "Cloud isn't always cheaper — why."

**Senior**: "Migrate $5M/yr DC to cloud — how to estimate."

**Staff**: "Cost per user metric — design."

## Next Topic

→ Move to [L07/C03 — Shared Responsibility](../C03/README.md)
