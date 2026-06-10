# L10/C05/T02 — Multi-Account / Multi-Region Patterns

## Learning Objectives

- Manage Terraform across accounts + regions
- Use providers correctly

## Provider Aliases

Multiple providers; aliased:
```hcl
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

provider "aws" {
  alias  = "us_west"
  region = "us-west-2"
}

resource "aws_instance" "primary" {
  provider = aws.us_east
  ...
}

resource "aws_instance" "dr" {
  provider = aws.us_west
  ...
}
```

For multi-region.

## Cross-Account

```hcl
provider "aws" {
  alias  = "prod"
  region = "us-east-1"
  assume_role {
    role_arn = "arn:aws:iam::PROD_ACCT:role/Deploy"
  }
}

provider "aws" {
  alias  = "staging"
  region = "us-east-1"
  assume_role {
    role_arn = "arn:aws:iam::STAGING_ACCT:role/Deploy"
  }
}
```

Different accounts; same region.

## Module with Multiple Providers

```hcl
# In module
terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      configuration_aliases = [aws.primary, aws.replica]
    }
  }
}

resource "aws_db_instance" "primary" {
  provider = aws.primary
  ...
}

resource "aws_db_instance" "replica" {
  provider = aws.replica
  ...
}
```

Caller passes:
```hcl
module "rds" {
  source = "./modules/rds"
  
  providers = {
    aws.primary = aws.us_east
    aws.replica = aws.us_west
  }
}
```

## Per-Account State

```
infra/
├── accounts/
│   ├── shared-services/
│   ├── prod/
│   ├── staging/
│   └── dev/
```

Each: separate state, separate backend.

State backend in dedicated account (security):
```hcl
backend "s3" {
  bucket = "tfstate-shared"   # in shared services account
  key    = "prod/terraform.tfstate"
}
```

## Cross-Account State Access

For one account to read another's state:
```hcl
data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket = "tfstate-shared"
    key    = "shared-services/terraform.tfstate"
    region = "us-east-1"
    
    assume_role = {
      role_arn = "arn:aws:iam::SHARED:role/ReadState"
    }
  }
}

vpc_id = data.terraform_remote_state.shared.outputs.vpc_id
```

For: per-team / per-workload state, shared infrastructure.

## Per-Region State

```
infra/prod/us-east-1/    # state in us-east-1 bucket
infra/prod/eu-west-1/    # state in eu-west-1 bucket
```

Each: own state, own region.

For: per-region applies; isolation.

## Org-Wide Pattern

```
infra/
├── modules/                          # shared
├── accounts/                         # account-level
│   ├── security/                     # CloudTrail, IAM org
│   ├── shared-services/              # central networking
│   ├── prod/
│   │   └── workloads/
│   │       ├── app-1/
│   │       └── app-2/
│   ├── staging/
│   └── dev/
```

Layered: org → account → workload.

## Bootstrap

For new account:
1. Create account (Organizations)
2. Bootstrap S3 + DynamoDB for state
3. Bootstrap IAM role for Terraform
4. Apply workload Terraform

Chicken-and-egg for state. Manual bootstrap once.

## Provider Configuration File

```hcl
# providers.tf
provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = local.common_tags
  }
}
```

Common settings; default_tags applied to all.

## Default Tags

```hcl
provider "aws" {
  default_tags {
    tags = {
      Env       = var.env
      Team      = var.team
      ManagedBy = "terraform"
    }
  }
}
```

All resources auto-tagged.

For: cost tracking, ownership.

## Region Patterns

### Active-Passive
- Primary in region A
- Backup in region B
- Replicate data

```hcl
module "primary" {
  providers = { aws = aws.us_east }
  ...
}

module "backup" {
  providers = { aws = aws.us_west }
  ...
}
```

### Active-Active
Both regions serving.

### Single Region
Most common; simpler.

## Multi-Account Strategies

### AWS Organizations
SCPs enforce policy at org level.

Terraform deploys in member accounts; org admin sets guardrails.

### Per-Workload Account
Each app: own account.
- Blast radius small
- Per-account billing
- IAM simpler

## Cross-Account Resource Sharing

### RAM (Resource Access Manager)
Share VPC, TGW from network account:
```hcl
resource "aws_ram_resource_share" "vpc" {
  provider = aws.network
  name = "shared-vpc"
}

resource "aws_ram_principal_association" "workload" {
  provider           = aws.network
  resource_share_arn = aws_ram_resource_share.vpc.arn
  principal          = "WORKLOAD_ACCT_ID"
}
```

Workload account sees subnets via RAM.

## State Backend Per Workload

```hcl
backend "s3" {
  bucket = "${var.team}-tfstate-${var.env}"
  key    = "${var.workload}/terraform.tfstate"
}
```

Per team / env / workload.

For: ownership clarity.

## IAM Strategy

Bootstrap role:
- Trust: org SSO / GitHub OIDC
- Permissions: enough to manage workload

For CI: OIDC federation (no static keys).

```hcl
provider "aws" {
  assume_role_with_web_identity {
    role_arn                = var.role_arn
    web_identity_token_file = "/var/run/secrets/github-token"
  }
}
```

## Pipeline Per Account

Per-account pipeline:
- Terraform plan in PR
- Apply on merge
- Per-environment approvals

For: controlled rollout.

## Common Mistakes

- All accounts in one state
- Wide cross-account IAM
- No default tags
- Forgetting provider aliases (deploys to wrong region)
- Mixing accounts in one apply

## Best Practices

- Separate state per account / env / workload
- Provider aliases for explicit multi-region
- RAM for cross-account sharing
- OIDC for CI auth
- Default tags
- Documented architecture
- Bootstrap script for new accounts

## Bootstrap Module

```hcl
module "bootstrap" {
  source = "./modules/bootstrap"
  
  account_id   = "..."
  state_bucket = "tfstate-..."
  state_table  = "tflock-..."
}
```

Creates: S3 bucket, DynamoDB, KMS key, IAM role.

Run once per account.

## Account Factory

Automated:
- Terraform creates new AWS account (Organizations)
- Bootstraps state
- Sets up baseline IAM
- Ready for workload

For: org with many accounts.

## Quick Refs

```hcl
# Multi-region
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

resource "X" "y" {
  provider = aws.us_east
}

# Multi-account
provider "aws" {
  alias = "prod"
  assume_role { role_arn = "..." }
}

# Module
module "x" {
  providers = {
    aws = aws.prod
  }
}
```

## Interview Prep

**Mid**: "Provider aliases."

**Senior**: "Multi-account Terraform strategy."

**Staff**: "Org structure for 50 accounts."

## Next Topic

→ [T03 — Terragrunt for DRY Infrastructure](T03-Terragrunt.md)
