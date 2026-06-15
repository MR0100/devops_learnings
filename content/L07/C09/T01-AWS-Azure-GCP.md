# L07/C09/T01 — AWS vs Azure vs GCP (Honest Comparison)

## Learning Objectives

- Compare clouds fairly
- Pick for context

## Market Position (2025)

| | Share | Strength |
|---|---|---|
| AWS | ~31% | Breadth, ecosystem, maturity |
| Azure | ~25% | Enterprise (MS shops), hybrid, gov |
| GCP | ~11% | Data, ML, K8s, networking |

## Service Breadth

AWS: most services (300+). Most regions. Earliest mover.
Azure: ~200 services. Strong in enterprise tools.
GCP: ~150 services. Curated; less breadth.

AWS has many overlapping; Azure middle; GCP curated.

## Strengths

### AWS
- Mature; battle-tested
- Largest ecosystem (jobs, partners, training)
- Most regions / AZs globally
- Deepest service catalog
- Best-of-class: S3, IAM, EC2 variety, Lambda

### Azure
- Office 365 / Windows integration
- Active Directory federation
- Enterprise sales / support
- Hybrid (Azure Arc, Stack)
- Government certifications
- .NET / SQL Server stacks

### GCP
- Google-grade networking (premium tier; global LB)
- BigQuery (best DWH arguably)
- K8s (Google invented; GKE most mature)
- ML/AI (Vertex AI; TPUs)
- Better UX in many places
- Live migration of VMs (no maintenance downtime)

## Weaknesses

### AWS
- Pricing complexity (200 EC2 types)
- UI can be busy
- Slow innovation in some areas
- Service overlap confusing

### Azure
- Console quirks
- Multi-region not as smooth
- Documentation inconsistent
- Eventual-consistency surprises

### GCP
- Fewer regions
- Smaller ecosystem
- Less enterprise sales muscle
- Newer; less battle-tested in some
- Less services compared to AWS

## Notable Differences

### Networking
- AWS: per-region VPCs
- GCP: global VPCs (subnets per region within one VPC)
- Azure: per-region VNets

GCP's global VPC simplifies multi-region.

### IAM
- AWS: identity vs resource policies; complex
- Azure: Azure AD; RBAC; familiar
- GCP: simpler IAM; permissive defaults (be careful)

### Compute
- AWS: most EC2 variety; Graviton (ARM)
- GCP: Tau T2A (ARM); custom machines; live migration
- Azure: Ampere (ARM); good Windows perf

### Storage
- S3: gold standard
- GCS: comparable; multi-region buckets
- Blob: comparable; tiers

### DB
- AWS: Aurora killer; many engines
- GCP: Spanner unique (global consistent SQL)
- Azure: Cosmos DB (multi-model global)

### Serverless
- Lambda: most mature; broad triggers
- Cloud Functions / Cloud Run: cleaner; Cloud Run scale-to-zero is great
- Azure Functions: solid; many languages

### K8s
- GKE: most mature; Autopilot best
- EKS: catching up; deep AWS integration
- AKS: free control plane; growing fast

## Pricing

Roughly similar list prices. Real costs depend on:
- Discounts (commitments, EA)
- Egress (each charges)
- Architecture (use right service mix)

GCP often slightly cheaper at list. AWS biggest discounts via EDP. Azure best for Windows licensing.

## Talent

AWS: most jobs; most candidates. Easiest hire.
Azure: enterprise-heavy; good candidates.
GCP: niche; high-quality but fewer.

## Compliance

All three: SOC, ISO, PCI, HIPAA, FedRAMP, etc.
Per-service variation; check before relying.

## Vendor Lock

All have proprietary services. Lock varies:
- Containers / K8s: portable
- Object storage: portable (S3 API compatible)
- IaC: Terraform helps
- Lambda / SQS / DynamoDB: proprietary; harder to leave

Multi-cloud reduces lock but increases complexity.

## When AWS

- Default for most
- Modern app from scratch
- Need breadth (specialized services)
- Best ecosystem
- Most regions

## When Azure

- Microsoft shop (Office 365, AD, SQL Server)
- Enterprise procurement easier
- Hybrid scenarios
- .NET workloads
- US government

## When GCP

- Data / analytics heavy (BigQuery)
- K8s expertise
- ML / AI workloads
- Better networking (global LB)
- Willing for smaller ecosystem

## Multi-Cloud Reality

Few companies "truly" multi-cloud. Usually:
- Primary cloud
- Secondary for backup / specific workloads
- M&A inheritance

Tooling: Terraform, Kubernetes, Crossplane help.

## Cost Comparison Example

100 VMs (m6i.large equivalent) 24/7:

- AWS On-Demand: ~$70k/yr
- AWS 3yr SP: ~$25k/yr
- GCP On-Demand: ~$65k/yr
- GCP 3yr CUD: ~$28k/yr
- Azure PAYG: ~$72k/yr
- Azure 3yr RI: ~$22k/yr

Close. Real difference in egress, managed services, support.

## Innovation Pace

- AWS: re:Invent annual; many launches
- GCP: Cloud Next; fewer but often impactful
- Azure: Build / Ignite; steady

All add features constantly. Six months ago's tradeoffs may not apply.

## Decision Framework

1. Existing investments / contracts?
2. Team skills?
3. Strategic partner deals?
4. Specific service needs (Spanner? BigQuery? Aurora?)
5. Geographic regions / compliance?
6. Cost negotiated discounts?

Rarely a wrong answer if executed well.

## My Take (Opinionated)

- Default to AWS unless reason otherwise
- GCP if data-heavy
- Azure if MS-heavy enterprise
- Multi-cloud only with strong reason

## Common Mistakes

- Choosing by feature list (all have what you need)
- Ignoring talent market
- Lock-in fear over execution speed
- Multi-cloud "for resilience" (usually wrong)
- Ignoring existing investments

## Best Practices

- Choose by context, not feature checklist — all three cover the basics; weigh existing investments, team skills, negotiated discounts, and one or two killer services (Spanner, BigQuery, Aurora) that genuinely matter to you.
- Factor in the talent market: AWS is easiest to hire for, Azure suits enterprise/MS shops, GCP skills are scarcer but high quality.
- Default to a single primary cloud and execute well; add a second cloud only for a concrete driver (compliance, M&A, a uniquely strong service), since multi-cloud multiplies tooling and egress cost.
- Use Terraform/Kubernetes/open formats to keep the lock-in you accept deliberate and the exit cost bounded.
- Re-evaluate periodically — the providers ship constantly and a comparison from six months ago may be stale.
- Model real cost (discounts, egress, managed services, support), not list price, when comparing.

## Quick Refs

Pick-a-cloud decision rule:

| If you... | Lean |
|---|---|
| Want the default, broadest catalog, biggest ecosystem | AWS |
| Run Microsoft stack (O365/AD/SQL Server/.NET), gov, hybrid | Azure |
| Are data/ML-heavy, K8s-native, want best networking | GCP |
| Have no strong driver | AWS (largest talent pool) |

Notable per-cloud edges: AWS — breadth, S3/IAM/EC2 variety, most regions · Azure — AD/O365 integration, free AKS control plane, gov certs · GCP — global VPC, BigQuery, GKE Autopilot, Spanner, live VM migration.

Market share (2025): AWS ~31% · Azure ~25% · GCP ~11%. Cost of 100 VMs 24/7 lands within ~10% across all three on 3-yr commitments; the real delta is egress, managed services, and negotiated discounts.

## Interview Prep

**Junior**: "Major cloud providers?"

**Mid**: "AWS vs Azure for new startup."

**Senior**: "Pick cloud for ML training pipeline."

**Staff**: "Cloud strategy for 5-year roadmap."

## Next Topic

→ [T02 — Vendor Lock-In: Reality vs Myth](T02-Vendor-Lock-In.md)
