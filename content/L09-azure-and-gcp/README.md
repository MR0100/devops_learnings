# L09 — Azure & GCP Comparative Mastery

## Overview

After L08 (AWS), this lecture covers Azure and GCP at comparable depth, with constant comparison to AWS so concepts transfer. Multi-cloud is the norm at FAANGM scale.

**4 chapters, 18 topics.**

## Chapter Map

### [C01](C01/) — Azure Core
- T01 Resource Groups, Subscriptions, Management Groups
- T02 Entra ID (formerly Azure AD)
- T03 Compute (VMs, VMSS, AKS, App Service, Functions)
- T04 Storage (Blob, Files, Disks)
- T05 Networking (VNets, NSGs, Application Gateway, Front Door)
- T06 Bicep & ARM Templates

### [C02](C02/) — GCP Core
- T01 Projects, Folders, Organizations
- T02 IAM (Roles, Service Accounts, Workload Identity)
- T03 Compute (GCE, GKE, Cloud Run, Cloud Functions)
- T04 Storage (GCS, Persistent Disk, Filestore)
- T05 Networking (VPC, Cloud Load Balancing, Cloud Armor)
- T06 Deployment Manager, Config Connector

### [C03](C03/) — Multi-Cloud Strategy
- T01 Choosing Workload Placement
- T02 Cross-Cloud Connectivity
- T03 Cross-Cloud IAM Federation
- T04 Data Gravity & Egress Cost Traps

### [C04](C04/) — Service-by-Service Comparison
- T01 Compute Equivalents
- T02 Storage Equivalents
- T03 Database Equivalents
- T04 Networking Equivalents

## Key Azure Differences From AWS

- **Resource Groups** are mandatory containers (not optional like AWS tags)
- **Subscriptions** are billing + access boundaries (more granular than AWS accounts)
- **Entra ID** (Azure AD) handles all identity — not just cloud
- **Front Door** = ALB + CloudFront + WAF + Route53 in one
- **Cosmos DB** is multi-model (NoSQL, SQL, Graph, etc.)

## Key GCP Differences From AWS

- **Projects** are the unit of access + billing (smallest scope)
- **Global VPC** by default (subnets are regional, VPC spans world)
- **Single global load balancer** with anycast (no per-region setup)
- **BigQuery** is serverless data warehouse (no clusters to manage)
- **Spanner** is global ACID SQL (unique offering)
- **GKE Autopilot** removes node management

## Honest Cloud Comparison

| | AWS | Azure | GCP |
|---|---|---|---|
| Market share | 35% | 23% | 11% |
| Strengths | Most services, most regions, most mature | Enterprise integration (M365, AD) | Data, ML, networking elegance |
| Weaknesses | UX inconsistency, IAM complexity | Documentation, occasional outages | Service breadth, fewer regions |
| Best for | General purpose, startups | Enterprises with MS ecosystem | Data-heavy, K8s-first orgs |

## When Multi-Cloud

| Reason | Reality |
|---|---|
| "Avoid lock-in" | Often costs more than it saves |
| "Geographic coverage" | Valid (some regions only on one cloud) |
| "Cherry-pick best services" | Valid (e.g., BigQuery + EKS) |
| "M&A integration" | Common in practice |
| "Compliance forces it" | Rare but real (sovereignty) |

## Recommended Reading

- *Microsoft Cloud Adoption Framework*
- *Google Cloud Architecture Framework*
- *AWS Well-Architected Framework*
- *Cloud FinOps* — Storment & Fuller

## Interview Relevance

- "Compare AWS X and GCP/Azure equivalent"
- "Why would you choose Azure over AWS for this workload?"
- "Design a multi-cloud disaster recovery strategy"

## Next

→ [L10 — Infrastructure as Code (Terraform, Pulumi, CDK)](../L10-infrastructure-as-code/README.md)
