# L07/C03 — Shared Responsibility Model

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Customer-vs-Provider.md) | Customer vs Provider Responsibilities | 0.5 hr |
| [T02](T02-Per-Service-Variation.md) | Per-Service Variations | 0.5 hr |

## The Model

```
+-------------------------------------------+
| Customer Data                             | ← always customer
| Application Code                          | ← always customer
| IAM (your principals, your policies)      | ← always customer
| Configuration (per service)               | ← customer
+-------------------------------------------+
| Service config / patching                 | ← varies (IaaS vs PaaS)
| OS patching                                | ← IaaS: customer; PaaS: provider
| Runtime                                    | ← IaaS: customer; PaaS: provider
+-------------------------------------------+
| Virtualization, hypervisor                | ← provider
| Physical hardware                          | ← provider
| Datacenter physical security              | ← provider
| Network infrastructure                     | ← provider
+-------------------------------------------+
```

> "Provider responsible for security **OF** the cloud. Customer responsible for security **IN** the cloud."

## Variation by Service Type

### IaaS (e.g., EC2)
- **Provider**: hardware, hypervisor, datacenter
- **Customer**: OS patching, runtime, app, data, config, IAM, network rules

### Containers (e.g., ECS on EC2)
- **Customer**: container image, app, data, networking
- **Provider**: orchestration, EC2 underneath (your responsibility OS), datacenter
- ECS on Fargate: provider takes OS too

### Managed K8s (e.g., EKS)
- **Provider**: control plane (apiserver, etcd, scheduler, controller-mgr)
- **Customer**: worker nodes OS (unless Fargate), workloads, IAM, NetworkPolicies

### Serverless (e.g., Lambda)
- **Provider**: runtime, OS, scaling, infra
- **Customer**: code, IAM, env config

### SaaS (e.g., Cognito, RDS, S3)
- **Provider**: nearly everything technical
- **Customer**: config, IAM, data, what you store

## Compliance & Shared Responsibility

For audits (SOC 2, PCI, HIPAA):
- Provider provides their controls (SOC reports, attestations)
- Customer is responsible for their part
- Customer must show: their IAM is correct, their data is encrypted, their access is logged

The provider's audit doesn't make you compliant — only your config on top of their compliant platform does.

## Misconceptions

### "S3 is secure by default"
S3 buckets are private by default since 2018+, but:
- Bucket policy can override
- ACLs can override (legacy)
- You can mis-configure SSE
- Public access blocks must be enabled at account level

### "RDS handles backups"
RDS does daily backups, but:
- 7-day default retention (often too short for compliance)
- Cross-region copies are your responsibility
- Encryption choice is yours
- IAM auth is opt-in

### "Lambda is secure because it's serverless"
- Your code can have vulns
- IAM policy attached is your responsibility
- Dependencies (libs) bring CVEs
- Environment variables can leak secrets if logs are public

## Pitfalls & Detection

Use **CSPM** (Cloud Security Posture Management):
- Wiz, Lacework, Prisma Cloud, AWS Security Hub
- Continuously scans config against best practices
- Flags: public buckets, unencrypted volumes, overly broad IAM, etc.

## Interview Themes

- "Explain shared responsibility"
- "Compare responsibility for IaaS vs managed K8s vs Lambda"
- "Who is responsible for OS patching on Fargate vs EC2 vs EKS managed nodes?"
- "What's a CSPM?"
