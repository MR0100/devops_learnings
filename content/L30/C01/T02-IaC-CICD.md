# L30/C01/T02 — IaC for Underlying Infra

## Learning Objectives

- Build with IaC
- Showcase Terraform

## Goal

Everything in code:
- VPC, EKS, RDS, S3
- IAM
- DNS
- Monitoring infra

## Why IaC Is the Foundation of This Capstone

The infrastructure layer is what makes the whole project *reproducible* and
*tearable-down* — the two properties that keep a cloud capstone from bankrupting
you and let a reviewer actually run it. If the VPC and cluster exist only as
clicks in the console, the project isn't a portfolio piece; it's a one-off. With
Terraform, `terraform apply` brings it up and `terraform destroy` takes it down,
which is exactly the demo a hiring manager respects.

### Rationale & Trade-offs

- **Modules over a monolith** — a `vpc`/`eks`/`rds` module split lets you reuse,
  version, and reason about each piece independently, and it keeps the per-env
  root tiny. Trade-off: more files and a small indirection cost up front.
- **Remote state (S3 + DynamoDB lock) over local state** — state is shared,
  encrypted, and locked so two applies can't corrupt it. Local state is fine for
  a toy and a liability for anything a team touches.
- **Terraform over Crossplane *for the base layer*** — bootstrapping the cluster
  itself with Terraform avoids a chicken-and-egg problem (Crossplane runs *in* a
  cluster). Crossplane shines later for in-cluster self-service (the IDP
  capstone, C04/T03) — different layer, different tool.
- **`-00` vs pinned versions** — pin module and provider versions so the build
  is the same next month as today; unpinned `~>` drift is a classic capstone
  rot.

## Terraform Structure

```
infra/
  modules/
    vpc/
    eks/
    rds/
  environments/
    staging/
      main.tf
      backend.tf
    prod/
      main.tf
      backend.tf
```

## Modules

```hcl
module "vpc" {
  source = "./modules/vpc"
  cidr   = var.vpc_cidr
  azs    = var.azs
}

module "eks" {
  source     = "./modules/eks"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  ...
}
```

## State

```hcl
terraform {
  backend "s3" {
    bucket         = "tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-lock"
    encrypt        = true
  }
}
```

The S3 bucket holds shared, encrypted state; the DynamoDB table provides the
lock so two `apply`s can't race and corrupt it. This is the first thing you
provision (chicken-and-egg: create the bucket/table once, by hand or a tiny
bootstrap config, then everything else uses it).

## CI

```yaml
- name: Terraform plan
  run: terraform plan -out=plan.tfplan

- name: Terraform apply
  if: github.ref == 'refs/heads/main'
  run: terraform apply plan.tfplan
```

## Policy

```bash
checkov -d infra/
tfsec infra/
```

Run policy scanning in CI as a gate: it catches the classic IaC mistakes
(public S3 buckets, `0.0.0.0/0` security groups, unencrypted volumes) *before*
they reach an account. Make it fail the plan, not just warn.

## Cost

```bash
infracost breakdown --path=infra/
```

`infracost` posts a per-PR dollar delta so "this change adds a NAT gateway,
+$32/month" is visible at review time — exactly the FinOps-aware habit a senior
role wants to see. For this capstone it also keeps you honest about the
~$100/month run rate.

## Build Order & Acceptance

1. Bootstrap remote state (S3 bucket + DynamoDB lock table)
2. `network` (VPC, subnets, NAT) → `cluster` (EKS) → `ecr` → `observability`
3. Wire `checkov`/`tfsec`/`infracost` into the Terraform CI job

**Acceptance**: a fresh clone runs `terraform apply` to a working cluster, the
policy scan blocks an intentionally-public bucket, infracost shows a cost
estimate on the PR, and `terraform destroy` leaves nothing behind (no orphaned
ENIs, load balancers, or volumes).

## Document

- Module purpose
- Variables
- Outputs
- Examples

## Best Practices

- Modular
- Versioned modules
- Remote state
- Locking
- Policy scanning
- Cost estimation

## Common Mistakes

- Monolithic
- No state mgmt
- No policy
- Manual changes (drift)

## Quick Refs

```hcl
module "X" {
  source = "..."
  ...
}

backend "s3" { ... }
```

```bash
checkov -d .
infracost breakdown
```

## Interview Prep

**Junior**: "What is Infrastructure as Code and why use it here?" — It means
defining infrastructure (VPC, cluster, IAM) in declarative files instead of
clicking in a console, so it's version-controlled, reviewable, and repeatable.
For the capstone it means I can stand the whole environment up and tear it back
down with `terraform apply`/`destroy`.

**Mid**: "Why remote state with locking?" — State is the map between your config
and the real resources. Stored remotely (S3) it's shared and encrypted; with a
DynamoDB lock, two people or two CI runs can't apply at once and corrupt it.
Local state breaks the moment more than one actor is involved.

**Senior**: "How do you keep IaC from drifting and from being unsafe?" — Pin
module and provider versions so builds are reproducible; forbid manual console
changes (they cause drift Terraform will fight or silently overwrite); and gate
every PR with policy-as-code (`checkov`/`tfsec`) plus an `infracost` diff so
security and cost regressions are caught at review, not in production. Drift
detection on a schedule (`terraform plan` in CI) flags anything that slipped in
out of band.

**Staff**: "Terraform vs Crossplane — when each?" — Use Terraform to bootstrap
the foundational, low-churn layer (accounts, VPCs, the cluster itself) — it runs
from CI and has no chicken-and-egg dependency on a running cluster. Use
Crossplane for *in-cluster, self-service* provisioning where developers request
a database or bucket through the K8s API and a platform team owns the
composition (the IDP capstone). They're not competitors; they sit at different
layers — Terraform builds the platform, Crossplane lets the platform offer
self-service on top.

## Next Topic

→ [T03 — Jenkins/GitHub Actions + ArgoCD](T03-GitHub-Actions-ArgoCD.md)
