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

For: state + locking.

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

For: security gate.

## Cost

```bash
infracost breakdown --path=infra/
```

For: estimate.

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

## Next Topic

→ [T03 — Jenkins/GitHub Actions + ArgoCD](T03-GitHub-Actions-ArgoCD.md)
