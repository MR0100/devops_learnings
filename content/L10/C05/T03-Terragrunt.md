# L10/C05/T03 — Terragrunt for DRY Infrastructure

## Learning Objectives

- Use Terragrunt
- Apply DRY pattern

## Terragrunt

Wrapper around Terraform; provides:
- DRY backend configuration
- DRY provider configuration
- Dependencies between modules
- Run on multiple modules
- Hooks

```bash
brew install terragrunt
```

## Structure

```
infra/
├── terragrunt.hcl              # root config
├── modules/                    # Terraform modules
│   ├── vpc/
│   └── eks/
└── live/                       # live infrastructure
    ├── prod/
    │   ├── env.hcl
    │   ├── us-east-1/
    │   │   ├── region.hcl
    │   │   ├── vpc/
    │   │   │   └── terragrunt.hcl
    │   │   └── eks/
    │   │       └── terragrunt.hcl
    │   └── eu-west-1/
    └── dev/
```

## Root terragrunt.hcl

```hcl
remote_state {
  backend = "s3"
  config = {
    bucket         = "tfstate-${get_env("ACCT")}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "tflock"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.region}"
}
EOF
}

locals {
  region = "us-east-1"
}
```

## Child terragrunt.hcl

```hcl
# live/prod/us-east-1/vpc/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../../modules//vpc"
}

inputs = {
  cidr = "10.0.0.0/16"
  azs  = ["us-east-1a", "us-east-1b", "us-east-1c"]
  
  env  = "prod"
}
```

`include` brings in root config. `inputs` provides variables.

## Apply

```bash
cd live/prod/us-east-1/vpc
terragrunt apply
```

Terragrunt:
1. Reads root config
2. Generates backend.tf
3. Generates provider.tf
4. Calls terraform with module source
5. Passes inputs as `-var`

## Dependencies

```hcl
# live/prod/us-east-1/eks/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../../modules//eks"
}

dependency "vpc" {
  config_path = "../vpc"
}

inputs = {
  vpc_id  = dependency.vpc.outputs.vpc_id
  subnets = dependency.vpc.outputs.private_subnet_ids
}
```

Terragrunt:
- Applies VPC first
- Reads VPC outputs
- Passes to EKS

For: cross-module dependencies in different state files.

## run-all

Apply many modules:
```bash
terragrunt run-all apply
```

Walks directory; applies in dependency order.

## Hierarchical Config

```
prod/env.hcl
prod/us-east-1/region.hcl
prod/us-east-1/vpc/terragrunt.hcl
```

Each level adds context.

```hcl
# env.hcl
locals {
  env = "prod"
  account_id = "..."
}

# region.hcl
locals {
  region = "us-east-1"
}

# vpc/terragrunt.hcl
include "root" {...}
include "env" { path = find_in_parent_folders("env.hcl") }
include "region" { path = find_in_parent_folders("region.hcl") }

inputs = {
  env    = include.env.locals.env
  region = include.region.locals.region
}
```

Composition of config.

## DRY Benefits

Without Terragrunt:
- Each env: duplicate backend, provider config
- Hard to maintain

With:
- Root config = single source
- Per-module: just inputs

## Hooks

```hcl
terraform {
  before_hook "before_apply" {
    commands = ["apply"]
    execute  = ["echo", "Applying..."]
  }
  
  after_hook "after_apply" {
    commands = ["apply"]
    execute  = ["./notify-slack.sh"]
  }
}
```

For: notifications, pre-checks.

## Generate Files

```hcl
generate "versions" {
  path      = "versions.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
EOF
}
```

For: consistent versions across modules.

## Common Patterns

### Per-Env Variables
```
live/prod/env.hcl: env = "prod"
live/staging/env.hcl: env = "staging"
```

Modules inherit.

### Per-Region
```
live/prod/us-east-1/region.hcl: region = "us-east-1"
live/prod/eu-west-1/region.hcl: region = "eu-west-1"
```

### Per-Workload Module
```
live/prod/us-east-1/vpc/
live/prod/us-east-1/eks/
live/prod/us-east-1/rds/
```

Each: own state; can apply independently.

## When Terragrunt

- Many modules (10+)
- Multiple environments
- Cross-module dependencies
- DRY important

For small (1-2 envs): vanilla Terraform fine.

## When NOT Terragrunt

- One env
- Simple state
- Don't want extra tool

For: simple cases.

## Terragrunt vs Modules

Modules: code reuse.
Terragrunt: configuration reuse.

Together: maximum DRY.

## Terragrunt vs Workspaces

Workspaces: same code, different state.
Terragrunt: same modules, different configurations + states.

Terragrunt more powerful.

## Common Mistakes

- Forgetting `include`
- Circular dependencies
- Outputs not exposed (module must `output`)
- Run-all without understanding order

## Best Practices

- Hierarchical config (env / region / module)
- Document structure
- Use dependencies for cross-module
- Generate common files
- Hooks for notifications
- Test dependencies

## CI Integration

```yaml
- run: cd live/prod/us-east-1/vpc && terragrunt plan
- run: cd live/prod/us-east-1/eks && terragrunt plan
```

Or:
```yaml
- run: terragrunt run-all plan --terragrunt-working-dir live/prod
```

For all in env.

## Locks

Terragrunt respects Terraform locking. Each module's state has own lock.

For run-all: locks per module sequentially.

## Performance

For 100+ modules: run-all slow.

Mitigate:
- Parallel apply (run-all does some)
- Selective (only what changed)

## Anti-Patterns

- Massive run-all in CI (slow + risky)
- No dependencies (manual order)
- Forgot to commit terragrunt.hcl files

## Alternative

Terraform Cloud workspaces:
- Each = remote state + run env
- Variables per workspace
- Less DRY needed

For TFC users: less Terragrunt.

## Quick Refs

```bash
# Single
cd live/prod/us-east-1/vpc
terragrunt apply

# All in dir
terragrunt run-all apply

# Plan all
terragrunt run-all plan

# Dependency tree
terragrunt graph-dependencies
```

## Interview Prep

**Mid**: "Terragrunt purpose."

**Senior**: "Dependencies between modules."

**Staff**: "DRY Terraform at 100-module scale."

## Next Topic

→ [T04 — Atlantis for PR-Driven Workflows](T04-Atlantis.md)
