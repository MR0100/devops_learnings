# L10 — Infrastructure as Code (Terraform, Pulumi, CDK)

## Overview

IaC is non-negotiable for senior+ DevOps roles. Terraform dominates; Pulumi and CDK are gaining. This lecture covers IaC philosophy, Terraform deeply, plus alternatives.

**9 chapters, 33 topics.**

## Chapter Map

### [C01](C01/) — IaC Fundamentals
- T01 Imperative vs Declarative
- T02 Mutable vs Immutable Infrastructure
- T03 GitOps for Infrastructure

### [C02](C02/) — Terraform Fundamentals
- T01 HCL Syntax
- T02 Providers, Resources, Data Sources
- T03 Variables, Locals, Outputs
- T04 Lifecycle Meta-Arguments

### [C03](C03/) — Terraform State
- T01 What State Is & Why It Matters
- T02 Backends (S3 + DynamoDB, Terraform Cloud, GCS, Azure Storage)
- T03 State Locking & Concurrency
- T04 terraform state Commands (mv, rm, import, replace)
- T05 State Drift Detection

### [C04](C04/) — Terraform Modules
- T01 Module Anatomy
- T02 Versioning & the Registry
- T03 Composition Patterns
- T04 Module Testing (Terratest, Terraform Test)

### [C05](C05/) — Terraform at Scale
- T01 Workspaces vs Directories
- T02 Multi-Account / Multi-Region Patterns
- T03 Terragrunt for DRY Infrastructure
- T04 Atlantis for PR-Driven Workflows

### [C06](C06/) — Writing Custom Providers
- T01 Provider Anatomy (Go)
- T02 Plugin Framework vs SDK v2

### [C07](C07/) — Pulumi & CDK
- T01 Pulumi (Real Programming Languages)
- T02 AWS CDK (TypeScript, Python)
- T03 CDK for Terraform (CDKTF)

### [C08](C08/) — Best Practices
- T01 Repository Structure
- T02 Secrets in IaC (Vault, KMS, SOPS)
- T03 Policy as Code (OPA, Sentinel, Checkov)
- T04 Cost Estimation (Infracost)

### [C09](C09/) — Disasters & Recovery
- T01 Importing Brownfield Infrastructure
- T02 Recovering Lost State
- T03 The "Big Refactor" Without Downtime

## Core Concepts

### Declarative IaC
You declare the desired state. The tool computes the diff and applies. Terraform plan/apply embodies this.

### State
Terraform's state file maps resources in code → real resources in the cloud. **State management is the #1 source of Terraform disasters at scale.**

- Remote backends (S3+DynamoDB, TFC, GCS) — don't use local state in teams
- State locking prevents concurrent apply
- State files contain secrets — encrypt them

### Module Anatomy
```
mymodule/
├── main.tf          # resources
├── variables.tf     # inputs
├── outputs.tf       # outputs
├── versions.tf      # provider versions
└── README.md
```

### Terragrunt Layout
```
live/
├── prod/
│   ├── us-east-1/
│   │   ├── vpc/terragrunt.hcl
│   │   └── eks/terragrunt.hcl
├── staging/
└── _envcommon/
modules/
├── vpc/
└── eks/
```

### Recommended Repository Structure

```
infrastructure/
├── modules/           # reusable modules
├── live/              # actual deployments
│   ├── prod/
│   ├── staging/
│   └── dev/
├── shared/            # shared resources (org, IAM)
├── pipelines/         # CI/CD configs
└── docs/
```

### Policy as Code

- OPA / Gatekeeper
- HashiCorp Sentinel (Terraform Cloud)
- Checkov, tfsec, terrascan, KICS for IaC scanning

## Common Mistakes

- Local state in team
- Committing state to git
- No state locking
- One giant Terraform root (`terraform plan` takes 20 min)
- No module versioning
- Hardcoded values instead of variables/data sources
- No drift detection

## Terraform vs Pulumi vs CDK

| | Terraform | Pulumi | CDK |
|---|---|---|---|
| Language | HCL | TS/Py/Go/Java/.NET | TS/Py/Java/Go/.NET |
| Multi-cloud | Yes | Yes | AWS only (or CDKTF) |
| Ecosystem | Largest | Growing | AWS-deep |
| State | Custom backend | Pulumi Cloud or self-host | CloudFormation |
| Best for | Teams, multi-cloud | Polyglot teams | AWS-deep, CDK fans |

## Recommended Reading

- *Terraform: Up & Running* — Yevgeniy Brikman
- *Infrastructure as Code* — Kief Morris
- HashiCorp's Terraform docs
- Gruntwork blog

## Interview Relevance

- "Walk me through how Terraform plans changes"
- "How do you handle Terraform state in a team?"
- "Design a Terraform module structure for a 200-engineer org"
- "Compare Terraform and CDK"

## Next

→ [L11 — Configuration Management](../L11-configuration-management/README.md)
