# L01/C04/T04 — Cloud Engineer / Infrastructure Engineer

## Learning Objectives

- Identify cloud-engineer scope and how it differs from DevOps, SRE, and Platform roles
- Map your skills to cloud-engineer-specific career paths and specializations
- Choose a specialization track (networking, security, data infra, FinOps, migration)
- Judge when certifications help and when experience matters more

## Prerequisites

L01/C04/T01–T03, plus working familiarity with one cloud provider's core services.

## What a Cloud Engineer Owns

A Cloud Engineer (often titled Infrastructure Engineer) is the person who **designs and operates the foundation everything else runs on**: the accounts, networks, identity, encryption, and the spend that pays for it all. Where DevOps focuses on the delivery pipeline and SRE on reliability, the Cloud Engineer goes **deep on the cloud substrate** — the parts that are expensive to get wrong and slow to change.

> If DevOps owns "how code gets to production," the Cloud Engineer owns "the production environment itself" — the VPCs, IAM, landing zones, and cost model underneath.

## Typical Day-to-Day

- Designing cloud architectures — multi-AZ for availability, multi-region for DR/latency
- Setting up VPCs, subnetting, routing, peering, Transit Gateway, and private connectivity
- Implementing IAM, encryption, and KMS key hierarchies with least privilege
- Cost analysis, rightsizing, and Reserved Instance / Savings Plan strategy
- Building **landing zones** and multi-account structures (AWS Organizations, GCP folders)
- Migrating workloads from on-prem to cloud, or between clouds
- Capacity and scaling design — autoscaling groups, quotas, service limits

## Where Cloud Engineering Sits

```
   Software Engineer ──► Infrastructure Engineer ──► Cloud Engineer
                              │
                              ├──► DevOps Engineer (more dev tooling)
                              ├──► SRE (more reliability)
                              └──► Platform Engineer (more product)
```

The roles share a base of Linux, networking, and IaC, then diverge by emphasis. A Cloud Engineer can pivot into any of the three branches; the cloud-substrate depth transfers everywhere.

## Landing Zones — A Defining Artifact

The clearest signal of cloud-engineering maturity is a well-designed **multi-account landing zone**: a repeatable account structure with guardrails baked in.

```
   AWS Organization (root)
   ├── Security OU
   │   ├── Log Archive account     (centralized CloudTrail/Config)
   │   └── Security Tooling account (GuardDuty, Security Hub)
   ├── Infrastructure OU
   │   ├── Network account         (Transit Gateway, shared VPCs)
   │   └── Shared Services account  (CI runners, registries)
   └── Workloads OU
       ├── Prod accounts  (one per business unit / blast-radius boundary)
       └── Non-prod accounts
```

Why separate accounts instead of one big one? **Blast-radius isolation** (a compromised dev account can't touch prod), **clean cost attribution** (billing per account), and **simpler IAM** (account boundaries are the strongest isolation AWS offers). Service Control Policies (SCPs) enforce guardrails org-wide.

## Common Specializations

| Track | What you go deep on | Representative skills |
|---|---|---|
| **Cloud Networking** | VPC at scale, hub-and-spoke topologies | Transit Gateway, Direct Connect, BGP, DNS, PrivateLink |
| **Cloud Security** | Identity, encryption, posture | IAM/IRSA, KMS, CSPM/CIEM, SCPs, OIDC federation |
| **Cloud Data Infrastructure** | Managed data plane operations | RDS/Aurora, Spanner, BigQuery, DynamoDB, backups/PITR |
| **FinOps Engineer** | Cost optimization at scale | Tagging strategy, RIs/Savings Plans, anomaly detection |
| **Cloud Migration** | Moving workloads in | 7 R's (rehost, replatform, refactor…), DMS, cutover plans |

## Skill Profile

- **One cloud at expert depth** (AWS most common), broad and conversant on the other two
- **IaC** — Terraform/OpenTofu, Pulumi, or native templates (CloudFormation/CDK, ARM/Bicep)
- **Deep networking** — the part most engineers underinvest in and where cloud bugs hide
- **Security and IAM** — least privilege as a default reflex, not an afterthought
- **Strong cost awareness** — you can read a bill and explain a 30% month-over-month jump
- **Compliance fluency** — comfortable mapping controls to SOC 2 / PCI / HIPAA / FedRAMP

## Certification Reality

- Useful as a **baseline at junior/mid** levels and to pass HR keyword filters
- **Diminishing returns at senior+** — depth and a track record of real architectures matter far more
- Worth doing (if you do any): **AWS Solutions Architect Professional**, **GCP Professional Cloud Architect**, **Azure Solutions Architect Expert**
- Skip generic "DevOps Engineer" certs unless your employer reimburses — they rarely move the hiring needle
- A cert proves you can pass a test; a documented migration or landing-zone design proves you can do the job

## Common Mistakes

- **The single mega-account** — one AWS account for everything, with no blast-radius isolation and a nightmarish IAM policy
- **Ignoring egress and NAT costs** — data transfer and NAT Gateway charges quietly become a top-three line item
- **Click-ops** — building infrastructure by hand in the console, leaving nothing reproducible in IaC
- **Wildcard IAM** — `Action: "*"` / `Resource: "*"` policies that violate least privilege and fail audits
- **Single-AZ "highly available"** — claiming HA while everything sits in one Availability Zone
- **Cert-collecting over building** — a wall of badges with no production-scale design experience behind them

## Best Practices

- **Multi-account from day one** — separate prod/non-prod and security accounts before you have to retrofit it
- **Everything in IaC** — no console changes that aren't reflected in Terraform; treat drift as a defect
- **Least privilege by default** — scope IAM to specific actions/resources; prefer roles and short-lived credentials over keys
- **Tag relentlessly** — a `team`/`env`/`cost-center` tagging policy is the foundation of all FinOps
- **Design for failure** — multi-AZ as a baseline, multi-region only where the SLO and budget justify it
- **Right-size continuously** — review utilization and commit to RIs/Savings Plans once usage is steady

## Quick Refs

```bash
# Find unattached (wasted) EBS volumes still costing money
aws ec2 describe-volumes --filters Name=status,Values=available \
  --query 'Volumes[].{ID:VolumeId,GiB:Size,AZ:AvailabilityZone}' --output table

# Audit overly-permissive IAM policies (wildcard actions)
aws iam list-policies --scope Local --query 'Policies[].Arn' --output text | \
  xargs -n1 -I{} aws iam get-policy-version --policy-arn {} \
  --version-id v1 --query 'PolicyVersion.Document'

# Cost by linked account this month
aws ce get-cost-and-usage --time-period Start=2026-06-01,End=2026-06-15 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=LINKED_ACCOUNT
```

The 7 R's of migration: **Retire, Retain, Rehost, Relocate, Repurchase, Replatform, Refactor** — ordered roughly from least to most effort.

## Interview Prep

**Junior**: "Design a 2-tier web app on AWS."
- Public ALB across two AZs in public subnets, EC2/ECS app tier in private subnets, RDS Multi-AZ in private subnets, security groups scoped tier-to-tier, NAT Gateway for egress, and Route 53 + ACM for DNS/TLS.

**Mid**: "Why use multiple AWS accounts instead of one, and how would you structure them?"
- For blast-radius isolation, clean cost attribution, and stronger IAM boundaries — organized into Security, Infrastructure/Network, and Workloads OUs with SCP guardrails and centralized logging.

**Senior**: "How would you design a multi-account AWS organization for a 500-engineer company?"
- A landing zone with OUs by function and environment, a dedicated network account fronting a Transit Gateway hub, centralized logging and security tooling, SCP guardrails, SSO/OIDC federation, and a tagging + FinOps model so cost and access scale with the org.

**Staff**: "Walk through migrating a stateful on-prem monolith to AWS — network, security, data, and cost."
- Choose a migration R (likely replatform), establish hybrid connectivity (Direct Connect/VPN), replicate data with DMS to RDS with a tested cutover and rollback, enforce least-privilege IAM and encryption in transit/at rest, and model run-rate vs. on-prem cost with rightsizing and commitment discounts before committing to a cutover date.

## Next Topic

→ [T05 — Career Progression: IC1 → Staff → Principal → Distinguished](T05-Career-Progression.md)
