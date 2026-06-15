# L07/C09/T03 — Multi-Cloud Strategy Tradeoffs

## Learning Objectives

- When multi-cloud makes sense
- How to implement if needed

## What Is Multi-Cloud

Using 2+ cloud providers for workloads. Spectrum:
- Single-Cloud (one provider, multi-region for HA)
- Polynimbus (apps choose best-fit cloud; not portable)
- Multi-Cloud (same workload on multiple clouds)
- Cloud-Agnostic (abstraction layer for portability)

## Reasons For

### Avoid Lock-In
Theoretical. Often more expensive than the lock-in cost.

### Negotiating Leverage
Real. Even partial multi-cloud → discount.

### Best-of-Breed
Use BigQuery for analytics, AWS for everything else. Genuine value.

### Resilience
"If AWS goes down, we have Azure." Real but rare (regional disruption common; provider-wide rare).

### Compliance
Specific data in specific region/cloud per regulation.

### Acquisition
Got a company on different cloud. Reality.

### Geographic
Provider X covers different country.

## Reasons Against

### Complexity
3× tooling, 3× docs, 3× incidents.

### Skill Spread
Each cloud is huge. Teams lose depth.

### Network Costs
Inter-cloud egress: $0.09/GB. Each direction. Adds up.

### Slower Innovation
Lowest common denominator if portable.

### Coordination Overhead
Two on-call rotations. Two billing models. Two security postures.

### Migration Cost
Setting up second cloud properly: months.

## Architectures

### Polynimbus (Per-Workload)
- Web app on AWS
- Analytics on GCP
- Internal apps on Azure
- Each is single-cloud; no portability

Simplest "multi-cloud."

### Active-Passive DR
- Primary: AWS
- DR: Azure (cold standby)
- Failover: rare; manual or scripted

Expensive (paying for unused). Real value if AWS true-down.

### Active-Active
- Same app on AWS + GCP
- Load balanced
- Data replicated

VERY hard:
- Multi-region writes (conflicts)
- Latency for cross-cloud sync
- Cost (compute + egress)
- Complexity

Few do this successfully.

### Cloud-Agnostic Platform
- K8s on all clouds
- Apps use only portable APIs (S3-compatible storage; standard Postgres)
- Build internal platform abstracting clouds

Big upfront investment. Pays off at scale.

## Tools That Help

### Terraform / OpenTofu
Multi-provider; same workflow.

### Kubernetes
Run on EKS, GKE, AKS, OpenShift. Apps portable if standard K8s only.

### Crossplane
K8s API to provision cloud resources. Cloud-agnostic-ish.

### Anthos / Azure Arc / AWS Outposts
Bring cloud APIs to other clouds or on-prem.

### Pulumi
Programming-language IaC across clouds.

### MinIO
S3-compatible storage, deploy anywhere.

### CockroachDB / YugabyteDB
Distributed SQL across clouds.

## Networking

Inter-cloud:
- Public Internet (cheapest, variable)
- Direct peering at colo (Equinix etc.)
- Dedicated lines

Egress always:
- AWS → Internet: $0.09/GB
- GCP → Internet: $0.12/GB
- Azure → Internet: $0.087/GB

For TBs of data: real money.

## Identity Federation

One IdP (Okta, Auth0); federate to all clouds. Required for sanity.

## Observability

- Datadog, New Relic, Dynatrace: multi-cloud
- Or unified logging / metrics stack you control

CloudWatch only shows AWS; Stackdriver only GCP; Azure Monitor only Azure.

## CI/CD

GitHub Actions, GitLab CI, Jenkins: work across.
Deploy to multi-cloud needs config per target.

## Multi-Cloud K8s Specific

Each cloud's K8s service is slightly different:
- Networking (CNI varies: VPC CNI, GKE Dataplane V2, Azure CNI)
- Storage (CSI per cloud)
- LB / Ingress (cloud-specific controllers)
- IAM integration (IRSA, Workload Identity, ...)

Apps using only K8s primitives = portable. Using cloud-specific = not.

Service Mesh (Istio, Linkerd) helps with cross-cluster service discovery.

## Cost Allocation

Each cloud has own billing.
Tools (CloudHealth, Vantage): aggregate.

Tagging discipline across all clouds.

## Real Talk

For most companies:
- Single cloud + multi-region is enough for HA
- Pick best cloud per workload (polynimbus) — easy
- Active-active multi-cloud — rare, valid for huge / strategic
- Cloud-agnostic platform — only at huge scale

## Decision Framework

| Question | Single | Polynimbus | Multi-Cloud Active |
|---|---|---|---|
| Team size | Any | 50+ engineers | 200+ engineers |
| Customers | Most | Specific needs | Global / mission-critical |
| Budget | Normal | Higher | 2× compute |
| Reasoning | Speed | Best-of-breed | True resilience |
| Operational maturity | Mature | Very mature | Top-tier |

## When To Genuinely Multi-Cloud

- Salesforce-acquired-by-Microsoft scenario: forced multi-cloud
- Financial services with strict provider concentration limits
- Mission-critical with regulator requiring it
- Global SaaS where one cloud's regions don't cover all customers

Otherwise: single-cloud, multi-region; smarter use of one cloud.

## Common Mistakes

- Multi-cloud "for resilience" without doing the work to actually fail over
- Cloud-agnostic but only one cloud used in practice (paying tax for nothing)
- Different teams = different clouds = unmanageable
- Multi-cloud as default mantra; everything LCD

## Reality Check

Surveys say 90% of orgs "multi-cloud." Reality: most have 1 primary, 1 secondary, with secondary <10% workload.

True multi-cloud (50/50): rare and hard.

## Hybrid Cloud

Often confused with multi-cloud. Hybrid = cloud + on-prem.
Multi-cloud = multiple clouds.
Both = mixed.

Each adds complexity. Often, simpler is better.

## Best Practices

- Default to single-cloud multi-region for HA; reach for multi-cloud only with a concrete driver (best-of-breed service, regulatory concentration limits, acquisition, geographic coverage).
- Prefer polynimbus (each workload on its best-fit cloud, each single-cloud) over true portable active-active — it captures most of the value with far less complexity.
- Centralize identity (one IdP federated to all clouds) and observability (Datadog/New Relic or your own stack), since per-cloud native tools only see their own cloud.
- Use Terraform/OpenTofu and Kubernetes for a consistent workflow, and stick to portable primitives where portability is the actual goal.
- Model inter-cloud egress explicitly (AWS $0.09, GCP $0.12, Azure $0.087 per GB to internet) and minimize chatty cross-cloud data paths; peer at a colo for heavy traffic.
- Enforce consistent tagging and aggregate billing (CloudHealth/Vantage) so multi-cloud cost stays visible.

## Quick Refs

Multi-cloud spectrum: Single-cloud (multi-region HA) → Polynimbus (best-fit per workload, not portable) → Multi-cloud (same workload on 2+) → Cloud-agnostic (abstraction for portability). Complexity and cost rise left to right.

Maturity gate (rough):

| Pattern | When |
|---|---|
| Single cloud | Most teams; speed matters |
| Polynimbus | 50+ engineers, specific best-of-breed needs |
| Active-active multi-cloud | 200+ engineers, mission-critical, top-tier ops |
| Cloud-agnostic platform | Only at huge scale |

Portability tools: Terraform/OpenTofu (multi-provider IaC) · Kubernetes (EKS/GKE/AKS) · Crossplane/Pulumi · MinIO (S3-compatible) · CockroachDB/YugabyteDB (distributed SQL). Reality check: ~90% of orgs claim "multi-cloud," but most run 1 primary + 1 secondary <10% — true 50/50 is rare and hard. Hybrid (cloud + on-prem) ≠ multi-cloud.

## Interview Prep

**Mid**: "Multi-cloud reasons."

**Senior**: "Multi-cloud risks; mitigation."

**Staff**: "Build multi-cloud strategy for $1B SaaS."

## Next Topic

→ Move to [L08 — AWS in Depth](../../L08/README.md)
