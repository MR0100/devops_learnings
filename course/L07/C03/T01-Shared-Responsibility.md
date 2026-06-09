# L07/C03/T01 — Customer vs Provider Responsibilities

## Learning Objectives

- Apply the shared responsibility model
- Avoid common misconceptions

## The Core Idea

In cloud, security and operations are split:
- **Provider**: security OF the cloud
- **Customer**: security IN the cloud

Specifics depend on service.

## AWS Mental Model

```
Customer:
  Data
  Configuration  
  Identity & Access
  OS (in IaaS)
  Apps

AWS:
  Hypervisor
  Hardware
  Physical security
  Network infrastructure
```

## Per-Service Variations

### EC2 (IaaS)
- AWS: hypervisor, hardware, AZ, network
- You: OS patches, app, firewall config, encryption, IAM

### RDS (Managed DB)
- AWS: OS, DB engine patches (per maintenance window), HA, backups
- You: DB schema, queries, encryption choice, network access

### Lambda (FaaS)
- AWS: everything except your function
- You: code, env vars, IAM role, secrets

### S3 (Managed Storage)
- AWS: durability, availability, replication
- You: bucket policy, access keys, encryption choice (SSE-S3 default), object permissions

### EKS (Managed K8s)
- AWS: control plane, node OS updates (you trigger)
- You: pods, RBAC, network policies, app

## Common Misconceptions

**"AWS secures my S3 bucket."**
Bucket private by default; but YOU set policy/ACL. If you make it public, your fault. (S3 bucket leaks: customer error 99% of time.)

**"RDS backups are automatic."**
AWS takes snapshots per your config. If you turn off backups: gone.

**"Lambda is secure by default."**
Function inherits IAM role you give it. If too permissive: blast radius huge.

**"DR is included."**
Multi-AZ ≠ cross-region. You design DR; AWS provides primitives.

## The Configuration Trap

90%+ of cloud breaches: customer misconfiguration.
- Public S3 buckets
- Permissive IAM roles
- Open security groups (0.0.0.0/0 on 22)
- Exposed RDS endpoints
- Hard-coded keys in code

Tools help:
- AWS Config (compliance rules)
- AWS Security Hub
- Azure Security Center
- GCP Security Command Center
- Third-party: Wiz, Lacework, Prisma Cloud

## Compliance

Provider's certs (SOC, PCI, HIPAA, FedRAMP) cover their infrastructure. You must:
- Use compliant services (not all in scope)
- Configure correctly (encryption, access)
- Process for your data

Read the "AWS Customer Responsibility" sheets per certification.

## Patching

| Service | Provider patches | You patch |
|---|---|---|
| EC2 OS | No | Yes (you) |
| RDS engine | Yes (mz window) | App schema you |
| Lambda runtime | Yes | Function code you |
| EKS control plane | Yes | Node AMI you trigger |
| Fargate | Yes | App image you |

## SLA

Provider commits uptime; pays credits if missed. NOT damages.

- EC2: 99.99% in AZ; 99.95% multi-AZ
- S3: 99.9% availability; 11 9s durability
- DynamoDB: 99.99% multi-AZ
- Lambda: 99.95%

You design for higher than SLA (defense in depth).

## Multi-Region DR

YOU plan. Provider gives you primitives:
- S3 Cross-Region Replication
- RDS cross-region read replica
- Route53 DNS failover

Cost: real money. RTO/RPO: yours to define.

## Backups

You decide retention. Provider stores.

AWS Backup centralizes (EBS, RDS, EFS, DynamoDB) with retention policies.

## Encryption

Provider:
- At-rest: usually automatic (S3, EBS, RDS) but you may want to manage keys (CMK in KMS)
- In-transit: TLS available; you configure

You:
- Choose: AWS-managed (free) vs customer-managed key (CMK; $1/mo + API)
- Rotate
- Enforce (block unencrypted in policies)

## Networking

Provider:
- VPC infrastructure
- Inter-AZ links
- Edge POPs

You:
- VPC config (CIDR, subnets, routing)
- Security groups
- NACLs
- Firewall rules

Most "AWS down" outages are customer network misconfig (typo in routing).

## Identity

Provider:
- IAM service exists
- Multi-factor available

You:
- Users, roles
- Policies
- MFA enforced
- Key rotation

90% of cloud breaches: IAM mistake.

## Logging / Auditing

Provider:
- CloudTrail / Activity Log / Audit Log: who did what, when
- VPC Flow Logs

You:
- Enable
- Store (S3 / log service)
- Retain (per compliance)
- Analyze / alert

## What If Provider Fails?

- AWS down: regional disruption ≠ your DR
- Bug in service: rare but happens (S3 typo 2017)
- Account compromised: AWS support helps but slow

Multi-region for tier-0; have an exit plan; backups in different AWS account.

## Models Differ

- **IaaS**: most on you (you manage OS)
- **PaaS**: less on you (manage app + config)
- **FaaS**: only function and config
- **SaaS**: only data and users

Higher abstraction = more on provider.

## Account Strategy

Multiple AWS accounts limits blast radius:
- Dev separate from prod
- Per business unit
- Per environment

Account = security boundary. Cross-account access explicit.

## Service Control Policies

For Organizations: org-level guardrails:
- Block use of unapproved regions
- Block public S3
- Enforce encryption
- Require MFA

Cascade to accounts.

## Common Mistakes

- "Cloud secure by default" — needs configuration
- Not reviewing IAM roles
- Open security groups
- No CloudTrail
- Backups not tested
- DR plan exists on paper only

## Interview Prep

**Junior**: "What does shared responsibility mean?"

**Mid**: "Who's responsible for RDS backups?"

**Senior**: "S3 leak — investigate."

**Staff**: "Build cloud governance program."

## Next Topic

→ [T02 — Per-Service Variations](T02-Per-Service-Variations.md)
