# L09/C03/T01 — Choosing Workload Placement

## Learning Objectives

- Decide which cloud per workload
- Avoid mistakes

## Why Multi-Cloud

- Risk reduction (single-vendor failure)
- Cost negotiation leverage
- Service quality per cloud
- Acquisition / merger (inherited)
- Data sovereignty

But: complexity cost is high.

## Reasons to Stay Single-Cloud

- Simpler ops
- Discount aggregation (commit)
- Tooling consistency
- Skills concentration

For: most companies, single-cloud + multi-region beats multi-cloud.

## When Multi-Cloud Makes Sense

- Regulated (must be on X cloud for region)
- One workload heavily optimized for one cloud (BigQuery on GCP)
- Strategic hedge (FAANGM scale)
- Customer demand ("we deploy where you deploy")

## Decision Framework

For new workload:
```
1. Does it need a specific cloud's service?
   (BigQuery, Athena, Cosmos DB) → that cloud
2. Where's the data? → close to data
3. Where's the team? → familiar cloud
4. Compliance constraints?
5. Cost model?
6. Latency requirements?
```

## Workload Types

### Data Warehouse
GCP BigQuery is dominant.
AWS Redshift / Snowflake.
Azure Synapse.

For: GCP often wins.

### ML Training
GCP TPUs (proprietary).
AWS GPU (broad).
Azure GPU.

For TPU: GCP.
For commodity GPU: any.

### Enterprise Windows
Azure (AD integration).
AWS / GCP weaker.

### Microsoft Stack
Azure (M365 integration).

### Cost-Sensitive
- Spot: 70-90% off
- Reserved: 30-60% off
- Commit
- Negotiate at scale

### Edge / Global
- AWS: most regions
- Cloudflare: edge specialist
- Azure / GCP: catching up

## Data Gravity

Data is expensive to move:
- Egress fees ($0.08-0.12/GB)
- Time
- Network bandwidth

For: compute follows data. New workloads on same cloud.

## Compliance

- FedRAMP: AWS GovCloud, Azure Gov
- HIPAA: all major
- EU data residency: regional choices

## Cost Comparison

Hard to compare directly:
- Different SKUs
- Different discount models
- Egress fees
- Hidden costs

For: per-workload TCO analysis.

## Lift-and-Shift vs Cloud-Native

### Lift-and-Shift
- VM-based
- Less cloud-specific
- Easier to multi-cloud (or move)

### Cloud-Native
- Managed services (Lambda, BigQuery, Spanner)
- Better economics for greenfield
- Vendor lock-in

For: hybrid approach common.

## Multi-Cloud Architectures

### Active-Active
Run in multiple clouds simultaneously.
Complex; high HA.

For: extreme uptime.

### Active-Passive
Primary cloud; DR in other.

For: business continuity.

### Per-Workload
Workload A in AWS; B in GCP.

For: cherry-pick services.

### Geo-Distributed
Cloud A in US; B in EU.

For: sovereignty.

## Lock-In Considerations

### High Lock-In
- DynamoDB, Spanner, Cosmos DB
- Lambda, Cloud Functions, Functions
- App Engine
- Proprietary ML platforms

### Lower Lock-In
- VMs (most portable)
- Object storage (similar APIs)
- K8s (somewhat portable)
- PostgreSQL / MySQL
- Open source DBs on managed (RDS / Cloud SQL)

For multi-cloud goal: choose open-source equivalents.

## Tools for Portability

- Terraform (IaC across clouds)
- Kubernetes (compute orchestration)
- Helm (K8s apps)
- Crossplane (multi-cloud K8s)
- Cilium (multi-cloud networking)
- Apache projects (Kafka, Cassandra, Spark)

## Hybrid

On-prem + cloud:
- Outposts (AWS on-prem)
- Anthos (GCP)
- Azure Arc
- VMware on cloud

For: data residency, latency.

## Real Examples

### Netflix
Primarily AWS. Reasoning: started early.

### Snap
Multi-cloud (GCP + AWS). Hedge.

### Apple
Multi-cloud (AWS + GCP + own DCs).

### Salesforce
Multi-cloud. Acquired tech on various.

## Decision Anti-Patterns

- "Future-proof" via multi-cloud upfront (premature)
- Same workload on multiple clouds (waste)
- No primary cloud (no expertise depth)
- Choose cloud per project ad-hoc

For: deliberate strategy.

## Migration Patterns

- 6R framework:
  - Rehost (lift-and-shift)
  - Replatform (lift + minor changes)
  - Repurchase (SaaS)
  - Refactor (cloud-native rewrite)
  - Retain (keep on-prem)
  - Retire (decommission)

## Cost Optimization Strategy

Single cloud:
- Commit (RIs, Savings Plans)
- Spot for batch
- Right-size
- Lifecycle

Multi-cloud:
- Hard to commit (can't aggregate)
- Negotiate at scale
- Use cheapest per workload

For: single cloud generally cheaper after commits.

## Best Practices

- Pick primary cloud
- Multi-cloud for strategic only
- Terraform / K8s for portability where it matters
- Document decisions
- Quarterly TCO review
- Avoid lock-in for portable workloads
- Embrace lock-in for high-leverage services

## Common Mistakes

- Multi-cloud without strategic reason
- Premature optimization
- No primary; no expertise
- Treating all workloads identically
- Ignoring egress costs

## Quick Refs

```
For data warehouse: GCP (BigQuery) often
For Microsoft stack: Azure
For breadth: AWS
For ML/TPU: GCP
For edge: consider Cloudflare
```

## Interview Prep

**Mid**: "Why multi-cloud."

**Senior**: "Workload placement framework."

**Staff**: "Multi-cloud strategy at FAANGM."

**Principal**: "Cost vs portability tradeoffs."

## Next Topic

→ [T02 — Cross-Cloud Connectivity](T02-Cross-Cloud-Connectivity.md)
