# L10/C04/T03 — Composition Patterns

## Learning Objectives

- Compose Terraform modules
- Apply composition over inheritance

## Composition

Build complex from simple. Modules call modules.

```hcl
module "platform" {
  source = "./modules/platform"
}

module "platform" depends on:
  ./modules/vpc
  ./modules/eks
  ./modules/rds
```

Layered.

## Patterns

### Root Module per Workload
```
infra/
├── prod-us-east-1/
│   ├── main.tf
│   └── ...
├── prod-eu-west-1/
└── staging-us-east-1/
```

Each: separate state, own configuration.

### Shared Modules
```
modules/
├── vpc/
├── eks/
├── rds/
└── ingress/
```

Reused across workloads.

### Composition Example

```hcl
# infra/prod-us-east-1/main.tf
module "vpc" {
  source = "../../modules/vpc"
  cidr   = "10.0.0.0/16"
  azs    = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

module "eks" {
  source = "../../modules/eks"
  vpc_id = module.vpc.vpc_id
  subnets = module.vpc.private_subnet_ids
  version = "1.30"
}

module "rds" {
  source = "../../modules/rds"
  vpc_id = module.vpc.vpc_id
  subnets = module.vpc.db_subnet_ids
}
```

Modules depend via output references.

## Cross-Module References

```hcl
# Module outputs
output "vpc_id" {
  value = aws_vpc.main.id
}

# Caller consumes
module "eks" {
  vpc_id = module.vpc.vpc_id
}
```

## Module Dependency

Implicit via reference:
```hcl
module "eks" {
  source = "..."
  vpc_id = module.vpc.vpc_id   # creates dependency
}
```

Terraform builds DAG; vpc applies first.

Explicit (rare):
```hcl
depends_on = [module.vpc]
```

## Stack Pattern

Compose:
```hcl
module "network_stack" {
  source = "./stacks/network"
}

module "app_stack" {
  source = "./stacks/app"
  vpc_id = module.network_stack.vpc_id
}

module "data_stack" {
  source = "./stacks/data"
  vpc_id = module.network_stack.vpc_id
}
```

Stack = collection of related modules.

## Module Versioning

Pin versions:
```hcl
module "vpc" {
  source  = "git::https://github.com/me/modules.git//vpc?ref=v1.2.3"
}
```

For: reproducibility.

## Inheritance vs Composition

Terraform doesn't have inheritance (no override of base module).

Compose: combine smaller modules.

For variation:
- Different modules per use case
- Conditional via count/for_each
- Variable defaults

## Module Refactoring

Split big module:
```
Old: modules/everything/
New: modules/vpc/ + modules/eks/ + modules/rds/
```

Update state with `moved` blocks:
```hcl
moved {
  from = module.everything.aws_vpc.main
  to   = module.vpc.aws_vpc.main
}
```

No destroy/recreate.

## Provider Pass-Through

Caller provides provider:
```hcl
module "vpc" {
  source = "./modules/vpc"
  
  providers = {
    aws = aws.us_east
  }
}
```

For multi-region/multi-account.

## Module Outputs Aggregation

Module exposes:
```hcl
output "endpoints" {
  value = {
    vpc_id = aws_vpc.main.id
    private_subnets = aws_subnet.private[*].id
    public_subnets = aws_subnet.public[*].id
  }
}
```

Caller:
```hcl
private_subnets = module.vpc.endpoints.private_subnets
```

For: grouped outputs.

## Variable Validation

```hcl
variable "env" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.env)
    error_message = "env must be dev/staging/prod"
  }
}
```

Catch at plan.

## Module Configuration

Configure module via:
- Variables
- Locals
- Data sources

Don't:
- Hardcode in module
- Modify state externally

## Common Mistakes

- Mega-module (everything in one)
- Tiny modules (overhead > benefit)
- Hidden dependencies
- Circular references
- Provider in module (let caller provide)

## Best Practices

- One responsibility per module
- Clear input/output interfaces
- Versioned modules
- Tested
- Documented
- Composed at root

## Compose with Terragrunt

```hcl
# terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

inputs = {
  cidr = "10.0.0.0/16"
}
```

For DRY (covered T03 next chapter).

## Real-World Example

Multi-tier app:
```hcl
module "vpc" { source = "..." }
module "k8s" { source = "..."; vpc_id = module.vpc.vpc_id }
module "db" { source = "..."; vpc_id = module.vpc.vpc_id }
module "cache" { source = "..."; vpc_id = module.vpc.vpc_id }
module "queue" { source = "..."; vpc_id = module.vpc.vpc_id }
module "app" {
  source = "..."
  k8s_cluster = module.k8s.cluster
  db_endpoint = module.db.endpoint
  cache_endpoint = module.cache.endpoint
  queue_arn = module.queue.arn
}
```

Each module focused; root composes.

## Migration

Existing monolithic Terraform → modular:
1. Identify boundaries
2. Extract module
3. Move state with `moved`
4. Test plan = no changes
5. Repeat per module

Gradual; safe.

## Quick Refs

```hcl
# Use module
module "name" {
  source  = "./path/or/git/or/registry"
  version = "1.0.0"
  
  input1 = "value"
}

# Access outputs
module.name.output_name

# Pass providers
providers = {
  aws = aws.alias
}
```

## Interview Prep

**Mid**: "Module composition."

**Senior**: "Refactor monolithic Terraform."

**Staff**: "Module strategy for 200-team org."

## Next Topic

→ [T04 — Module Testing](T04-Module-Testing.md)
