# L10/C05 — Terraform at Scale

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Workspaces.md) | Workspaces vs Directories | 0.5 hr |
| [T02](T02-Multi-Account-Region.md) | Multi-Account / Multi-Region Patterns | 1 hr |
| [T03](T03-Terragrunt.md) | Terragrunt for DRY Infrastructure | 1 hr |
| [T04](T04-Atlantis.md) | Atlantis for PR-Driven Workflows | 0.5 hr |

## Workspaces vs Directories

### Workspaces (Built-in)
```bash
terraform workspace new prod
terraform workspace select prod
terraform workspace list
```
State: separate state file per workspace; same backend config.

Use case: rarely good. Suitable for:
- Truly identical envs with only var differences
- Per-developer ephemeral copies

### Directories
```
live/
├── prod/
│   ├── network/
│   │   ├── main.tf
│   │   └── backend.tf
│   └── compute/
├── staging/
└── dev/
```

Separate state, separate backend, separate Terraform version possible. Clearer blast radius. **Preferred for most teams.**

## Multi-Account / Multi-Region

```
live/
├── shared/             # shared services (org, IAM, log archive)
├── prod/
│   ├── us-east-1/
│   │   ├── network/
│   │   ├── compute/
│   │   └── data/
│   ├── us-west-2/
│   └── eu-west-1/
├── staging/
└── dev/
```

### Provider Aliases for Multi-Account
```hcl
provider "aws" {
  alias  = "shared"
  assume_role { role_arn = "arn:aws:iam::SHARED:role/tf-deployer" }
}

provider "aws" {
  alias  = "prod"
  assume_role { role_arn = "arn:aws:iam::PROD:role/tf-deployer" }
}

resource "aws_s3_bucket" "log_bucket" {
  provider = aws.shared
  bucket   = "..."
}

resource "aws_iam_role" "x" {
  provider = aws.prod
}
```

## Terragrunt

Wrapper for Terraform that solves DRY for multi-environment.

### Layout
```
live/
├── terragrunt.hcl              # root config (remote_state, generate provider)
├── prod/
│   ├── env.hcl
│   ├── us-east-1/
│   │   ├── region.hcl
│   │   ├── network/
│   │   │   └── terragrunt.hcl  # references module + inputs
│   │   └── eks/
│   │       └── terragrunt.hcl
│   └── us-west-2/
└── modules/                    # actual Terraform modules
    ├── network/
    └── eks/
```

### terragrunt.hcl (root)
```hcl
remote_state {
  backend = "s3"
  config = {
    bucket         = "my-tf-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-lock"
    encrypt        = true
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "aws" {
  region = "${local.region_vars.aws_region}"
}
EOF
}

locals {
  env_vars    = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  region_vars = read_terragrunt_config(find_in_parent_folders("region.hcl"))
}

inputs = merge(local.env_vars.locals, local.region_vars.locals)
```

### terragrunt.hcl (per-component)
```hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../../modules/network"
}

inputs = {
  vpc_cidr = "10.0.0.0/16"
}
```

### Run
```bash
cd live/prod/us-east-1/network
terragrunt plan
terragrunt apply

# all-at-once
cd live/prod/us-east-1
terragrunt run-all plan
terragrunt run-all apply
```

### Benefits
- DRY backend config
- DRY provider config
- Single command can deploy a whole environment
- Dependency graph (a depends on b in same env)

### Trade-Offs
- Extra tool to learn
- Some Terraform features not fully supported
- Wrapper magic can be confusing

## Atlantis

Self-hosted PR-driven Terraform.

Workflow:
1. PR opened
2. Atlantis runs `terraform plan` automatically on changed dirs
3. Plan output posted as PR comment
4. Reviewer approves
5. Comment `atlantis apply` runs apply
6. Merge

### Why
- Plan is reviewable in PR
- Apply happens from a controlled bot (no local creds spread)
- Locking per directory prevents concurrent applies
- Easy approval workflow

### Setup
- Run Atlantis (Docker / K8s)
- GitHub/GitLab webhook → Atlantis
- atlantis.yaml in repo configures dirs/workflows

## Alternative Tools

- **Spacelift** — SaaS, advanced workflow control, policy as code
- **env0** — SaaS, similar
- **Scalr** — SaaS
- **Terraform Cloud / Enterprise** — HashiCorp's offering

## Tooling Decision

| Need | Tool |
|---|---|
| Just need a backend + run on laptop | terraform CLI |
| Want PR-driven, self-hosted | Atlantis |
| Need DRY across many envs | Terragrunt (+ Atlantis) |
| Want full SaaS, policy, RBAC | TFC / Enterprise / Spacelift |

## Scale Patterns

- **Many small TF roots** > one huge root (faster plans, smaller blast radius)
- Per-team, per-domain, per-env splits
- Use CODEOWNERS for review enforcement
- Pre-merge plan in CI
- Post-merge apply via dedicated runner with cloud creds
- Drift detection scheduled

## Interview Themes

- "Compare workspaces and directories"
- "How do you organize Terraform for a 50-engineer org?"
- "What does Terragrunt solve?"
- "Walk me through Atlantis workflow"
- "Multi-account TF — how?"
