# L07/C09 — Choosing a Cloud

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-AWS-Azure-GCP.md) | AWS vs Azure vs GCP (Honest Comparison) | 1 hr |
| [T02](T02-Vendor-Lock-In.md) | Vendor Lock-In: Reality vs Myth | 0.5 hr |
| [T03](T03-Multi-Cloud-Tradeoffs.md) | Multi-Cloud Strategy Tradeoffs | 0.5 hr |

## Honest Comparison

| Dimension | AWS | Azure | GCP |
|---|---|---|---|
| Market share | ~32% | ~23% | ~11% |
| Service breadth | Most | Second | Third |
| Regions | 33 | 60+ | 40+ |
| Enterprise integration | Strong | Strongest (MSFT licensing) | Weakest |
| Data/ML/Analytics | Strong | Strong | Strongest (BigQuery, Vertex) |
| Networking elegance | Complex | Complex | Cleanest (global VPC, global LB) |
| Documentation | Patchy but vast | Variable | Cleanest, sparser |
| Console UX | Inconsistent | Better | Best |
| Pricing transparency | Hardest | Medium | Easiest |
| Open-source friendliness | OK | Better recently | Best (Kubernetes origin) |

## Strengths By Provider

### AWS
- Largest service catalog (200+ services)
- Most mature ecosystem (3rd-party tools)
- Most enterprise certifications
- "Default" for many
- Deep in serverless innovation

### Azure
- Enterprise sales engine + Microsoft licensing bundles
- Best integration with M365, Active Directory, .NET, Windows Server
- Hybrid story (Azure Arc, Stack)
- Strong AI/Copilot integration
- Government/regulated industries

### GCP
- BigQuery (unique scale-out data warehouse)
- Spanner (unique global ACID SQL)
- Best Kubernetes (Google invented it)
- Cleanest networking (global VPC, global LB, anycast)
- Best ML infrastructure (Vertex AI, TPUs)
- Live migration of VMs (no reboot for hypervisor updates)

## How to Choose

| If you... | Pick |
|---|---|
| Starting fresh, no preference | AWS (default, broadest hire pool) |
| Already on M365, AD | Azure |
| Heavy data/ML focus | GCP (BigQuery + Vertex) |
| Need global ACID DB | GCP (Spanner) or CockroachDB on any |
| Need rich GovCloud / regulated | AWS GovCloud or Azure Government |
| Want best K8s experience | GKE Autopilot (GCP) |
| Already invested in Oracle/SAP | varies (all support) |
| Multi-region with simple LB | GCP (global LB) |

## Vendor Lock-In — Reality

| Layer | Lock-In Level |
|---|---|
| VMs (EC2 vs GCE vs Azure VM) | Low (Linux is Linux) |
| K8s | Low (CNCF standard) |
| Object storage API | Medium (boto3 vs gsutil; rclone abstracts) |
| Managed services (DynamoDB, BigQuery, Spanner) | High |
| IAM | Very high (each is unique) |
| Serverless (Lambda, Cloud Functions) | High |
| Networking constructs (VPC primitives differ) | Medium |

**The lock-in is real for managed services and IAM.** Pretending you can lift-and-shift Lambda to GCP Cloud Functions is misleading.

## Multi-Cloud Tradeoffs

### Real Reasons to Multi-Cloud

- Acquired companies use different clouds
- Specific service only on one cloud (BigQuery, Lambda@Edge)
- Compliance/sovereignty (data must stay in specific country/cloud)
- Geographic coverage (e.g., GCP weak in some regions)
- DR with strong isolation
- Negotiation leverage (rare)

### Bad Reasons

- "Avoid lock-in" — you'll lock in to your abstraction layer instead
- "Best of breed" — you'll abandon platform-specific best practices
- "We must use multiple clouds" — often executive direction without engineering input

### True Costs

- Doubled platform engineering investment
- Doubled hire pool requirement
- Doubled tooling
- Egress cost between clouds (often huge)
- Doubled compliance evidence
- Slower delivery

### Common Pattern (Pragmatic Multi-Cloud)

- One **primary** cloud for compute and data
- One **secondary** for specific services (e.g., BigQuery)
- Cross-cloud egress kept minimal
- Identity federated via OIDC/SAML

## Hybrid Cloud

On-prem + cloud. Real use cases:
- Migration in progress
- Specific workloads needing on-prem (latency, hardware, compliance)
- DR (cloud as failover)
- Data sovereignty constraints

Tools: AWS Outposts, Azure Arc + Stack, GCP Anthos.

## Interview Themes

- "When AWS vs Azure vs GCP?"
- "Multi-cloud — when and why?"
- "Is vendor lock-in real? Where?"
- "Compare global LB across the three clouds"
- "Hybrid cloud — what makes it succeed or fail?"
