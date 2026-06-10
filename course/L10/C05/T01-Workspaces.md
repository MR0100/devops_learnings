# L10/C05/T01 — Workspaces vs Directories

## Learning Objectives

- Pick workspace strategy
- Apply per environment

## Workspaces

Multiple states under one configuration:
```bash
terraform workspace new dev
terraform workspace new prod
terraform workspace list
terraform workspace select prod
terraform workspace show
```

Each workspace: separate state file.

## Workspace State

S3 backend:
```
my-tfstate/
├── env:/default/path/terraform.tfstate
├── env:/dev/path/terraform.tfstate
└── env:/prod/path/terraform.tfstate
```

## Workspace in Code

```hcl
resource "aws_instance" "web" {
  tags = {
    Env = terraform.workspace
  }
  
  instance_type = terraform.workspace == "prod" ? "m5.large" : "t3.micro"
}
```

`terraform.workspace` available.

## Pros

- Simple
- Same config; different state
- Quick switching
- One repo

## Cons

- Same backend (all states share bucket)
- Risk of typo (apply to wrong env)
- Less isolation
- Limited per-env config

## When Workspaces

- Lightweight environments (dev / test / sandbox)
- Same provider / region
- Identical infrastructure

## Directories

Separate directory per environment:
```
infra/
├── dev/
│   ├── main.tf
│   ├── terraform.tfvars
│   └── backend.tf
├── staging/
│   └── ...
└── prod/
    └── ...
```

Each: own state, own backend, own variables.

## Directory Pros

- Explicit per-env
- Different backends (separate IAM)
- Different vars / providers
- Less risk
- Better for prod isolation

## Directory Cons

- Code duplication
- Multiple checkouts / applies
- Sync between envs manual

## DRY with Directories

Modules + per-env directories:
```
infra/
├── modules/
│   ├── vpc/
│   └── eks/
├── dev/
│   └── main.tf   # calls modules
├── staging/
└── prod/
```

Modules shared; envs differ in variables.

## Terragrunt

DRY for directories:
```hcl
# terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

inputs = {
  env = "prod"
}
```

For: extreme DRY.

## Best Approach

For production: directories.
For dev / experimental: workspaces OK.

For prod: separate state, separate backend, separate access.

## Workspace Per-Env

Avoid: prod + dev same workspace bucket = scary.

If using workspaces for envs:
- Separate backend per important env minimum
- IAM restrictions
- Naming clear

## Mixed Approach

Per workload-environment combo:
```
infra/
├── modules/
├── prod-us-east-1/
├── prod-eu-west-1/
├── staging-us-east-1/
└── dev-us-east-1/
```

Each: separate state. Clear boundaries.

## Terraform Cloud Workspaces

TFC workspaces are different from CLI:
- Each is a "remote state + run environment"
- Variables per workspace
- Run history
- Team access

Not the same as CLI workspaces (though similar concept).

## Workspace State Operations

```bash
# In specific workspace
terraform workspace select prod
terraform state list
terraform state show aws_vpc.main

# Different workspace
terraform workspace select dev
```

State isolated.

## Switching

Just `terraform workspace select` — different state.

But all use same `.tf` files. Code change affects all workspaces.

For env-specific code: directories better.

## Module Configuration Per-Env

```hcl
locals {
  config = {
    dev = {
      instance_type = "t3.micro"
      replicas      = 1
    }
    prod = {
      instance_type = "m5.large"
      replicas      = 5
    }
  }
}

resource "aws_instance" "web" {
  instance_type = local.config[terraform.workspace].instance_type
}
```

Works but error-prone.

## Common Mistakes

- Workspaces for prod (insufficient isolation)
- Mixed strategies (confusion)
- Single backend for all (security)
- No naming conventions
- Forgot which workspace selected

## Best Practices

- Directories per environment (production-grade)
- Workspaces for ephemeral (PR previews)
- One backend per critical env
- Clear naming
- Use terragrunt for DRY
- Document strategy

## Workspaces Use Case

PR preview environments:
```
terraform workspace new pr-1234
terraform apply
# Tests
terraform destroy
terraform workspace delete pr-1234
```

Ephemeral; same config; different state.

## Anti-Patterns

- Same workspace name for different things
- Forgetting `select`
- Workspaces in production
- No CI guardrails

## Cost Tracking

Workspaces:
- Hard to tag per workspace
- Variable cost attribution

Directories:
- Per-env tagging clear
- Easy cost reports

## Production Recommendation

For typical org:
```
infra/
├── modules/                 # reusable
├── environments/
│   ├── dev/
│   │   ├── us-east-1/
│   │   └── eu-west-1/
│   ├── staging/
│   └── prod/
└── README.md
```

Each leaf: own state, own backend.

## Migration

Workspaces → directories:
1. Create new dir
2. Copy `.tf`
3. Set up backend
4. `terraform init -migrate-state`
5. Verify
6. Delete workspace

Test in non-prod first.

## CI Integration

For directories:
```yaml
- run: cd environments/prod/us-east-1 && terraform plan
```

Per-env steps.

For workspaces:
```yaml
- run: |
    terraform workspace select prod
    terraform plan
```

Single dir; switch.

## Quick Refs

```bash
# Workspaces
terraform workspace list
terraform workspace new NAME
terraform workspace select NAME
terraform workspace delete NAME

# Directories
cd environments/prod/us-east-1
terraform init
terraform apply
```

## Interview Prep

**Mid**: "Workspaces vs directories."

**Senior**: "Production multi-env strategy."

**Staff**: "Terraform org structure for 100 services."

## Next Topic

→ [T02 — Multi-Account / Multi-Region Patterns](T02-Multi-Account-Region.md)
