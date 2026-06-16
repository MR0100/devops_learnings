# L07 — Cloud Computing Fundamentals

## Overview

The cloud is now the default. This lecture builds a cloud-agnostic mental model so you can apply it to AWS (L08), Azure, and GCP (L09).

**9 chapters, 35 topics.**

## Chapter Map

### [C01](C01/) — Cloud Concepts
- T01 What Is "The Cloud" (Really)
- T02 IaaS vs PaaS vs SaaS vs FaaS
- T03 Public, Private, Hybrid, Multi-Cloud, Edge
- T04 Regions, Availability Zones, Edge Locations

### [C02](C02/) — Cloud Economics
- T01 CapEx vs OpEx
- T02 Pricing Models (On-Demand, Reserved, Spot, Savings Plans)
- T03 Total Cost of Ownership

### [C03](C03/) — Shared Responsibility Model
- T01 Customer vs Provider Responsibilities
- T02 Per-Service Variations

### [C04](C04/) — Compute Family
- T01 VMs (EC2, Compute Engine, Azure VMs)
- T02 Containers (ECS, EKS, GKE, AKS, Fargate, Cloud Run)
- T03 Serverless (Lambda, Cloud Functions, Azure Functions)

### [C05](C05/) — Storage Family
- T01 Object Storage (S3, GCS, Blob Storage)
- T02 Block Storage (EBS, Persistent Disk, Managed Disks)
- T03 File Storage (EFS, Filestore, Azure Files)

### [C06](C06/) — Database Family
- T01 Managed Relational (RDS, Cloud SQL, Azure SQL)
- T02 Managed NoSQL (DynamoDB, Firestore, Cosmos DB)
- T03 Managed Caches (ElastiCache, Memorystore)
- T04 Data Warehouses (Redshift, BigQuery, Synapse)

### [C07](C07/) — Cloud Networking Primitives
- T01 VPC, Subnets, Route Tables (Across Clouds)
- T02 Load Balancers (L4, L7)
- T03 DNS, CDN
- T04 Cross-Region Networking

### [C08](C08/) — Identity & Access Management
- T01 The IAM Mental Model (Principal, Action, Resource, Condition)
- T02 Roles vs Users vs Service Accounts
- T03 Federated Identity (SAML, OIDC)

### [C09](C09/) — Choosing a Cloud
- T01 AWS vs Azure vs GCP (Honest Comparison)
- T02 Vendor Lock-In: Reality vs Myth
- T03 Multi-Cloud Strategy Tradeoffs

## The Cloud Mental Model

Every cloud provides the same primitives differently named:

| Primitive | AWS | Azure | GCP |
|---|---|---|---|
| VM | EC2 | VM | GCE |
| Container | ECS, EKS, Fargate | AKS, Container Apps | GKE, Cloud Run |
| Serverless | Lambda | Functions | Cloud Functions |
| Object Storage | S3 | Blob | GCS |
| Block Storage | EBS | Managed Disks | Persistent Disk |
| File Storage | EFS, FSx | Files | Filestore |
| Managed SQL | RDS, Aurora | SQL Database | Cloud SQL, Spanner |
| Managed NoSQL | DynamoDB | Cosmos DB | Firestore, Bigtable |
| Queue | SQS | Service Bus | Pub/Sub |
| Event Bus | EventBridge | Event Grid | Eventarc |
| Stream | Kinesis | Event Hubs | Pub/Sub |
| Load Balancer | ALB, NLB, GWLB | Application Gateway, LB | Cloud LB |
| DNS | Route53 | DNS | Cloud DNS |
| CDN | CloudFront | CDN | Cloud CDN |
| IAM | IAM | Entra ID + RBAC | IAM |
| Secrets | Secrets Manager | Key Vault | Secret Manager |
| Encryption Key | KMS | Key Vault | KMS |
| WAF | WAF + Shield | Front Door / WAF | Cloud Armor |

## Pricing Mental Model

```
Total Cost = Compute + Storage + Network (egress!) + Service Fees
```

The biggest surprises are usually:
- Cross-AZ traffic (often $0.01/GB each way)
- Egress to internet ($0.05–0.09/GB)
- NAT Gateway data processing
- Log ingestion (Datadog, Splunk, etc.)

## Shared Responsibility

```
Customer manages:
   Application code, data, IAM, network config
Provider manages:
   Hardware, virtualization, physical security
Variable (depending on service):
   OS patches, runtime versions
```

PaaS shifts more to provider; IaaS leaves more with you.

## Regions, AZs, Edge

- **Region** — geographic area (e.g., us-east-1)
- **Availability Zone** — one or more datacenters in a region, isolated power/network
- **Edge Location / PoP** — CDN endpoint, closer to users

**Rule of thumb:** Multi-AZ for HA; multi-region for DR and global users.

## Recommended Reading

- *Cloud Native Patterns* — Cornelia Davis
- *Cloud FinOps* — J.R. Storment & Mike Fuller
- *The Phoenix Project* (still relevant for cloud transformations)
- AWS Well-Architected Framework
- Azure Well-Architected Framework
- Google SRE workbook

## Interview Relevance

- "Compare IaaS, PaaS, SaaS, FaaS"
- "What's the shared responsibility model?"
- "Design a multi-AZ web app on your cloud of choice"
- "When would you multi-cloud and what's the cost?"

## Next

→ [L08 — AWS Deep Dive](../L08-aws/README.md)
