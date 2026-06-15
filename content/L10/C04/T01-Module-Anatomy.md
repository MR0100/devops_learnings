# L10/C04/T01 — Module Anatomy

## Learning Objectives

- Structure modules
- Apply best practices

## Module

Reusable Terraform component:
- Inputs (variables)
- Resources
- Outputs

Like a function.

## Anatomy

```
modules/vpc/
├── README.md
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
└── examples/
    └── basic/
        └── main.tf
```

## Using a Module

```hcl
module "vpc" {
  source = "./modules/vpc"
  
  cidr = "10.0.0.0/16"
  azs  = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# Access outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}
```

## Source Types

```hcl
# Local
source = "./modules/vpc"

# Git
source = "git::https://github.com/me/my-modules.git//vpc?ref=v1.0.0"

# GitHub
source = "github.com/me/my-modules//vpc?ref=v1.0.0"

# Registry (Terraform Registry)
source  = "terraform-aws-modules/vpc/aws"
version = "5.0.0"

# S3
source = "s3::https://s3.amazonaws.com/my-modules/vpc.zip"

# Mercurial, generic Git, etc.
```

For team / org: Git + tags or private registry.

## Versioning

Tag releases in Git:
```bash
git tag v1.0.0
git push origin v1.0.0
```

Reference:
```hcl
source = "git::...//vpc?ref=v1.0.0"
```

Pin to version. Don't track `main` (breaks).

## Inputs

```hcl
# modules/vpc/variables.tf
variable "cidr" {
  type        = string
  description = "VPC CIDR block"
  
  validation {
    condition     = can(cidrnetmask(var.cidr))
    error_message = "Must be valid CIDR"
  }
}

variable "azs" {
  type        = list(string)
  description = "AZs to use"
  default     = []
  
  validation {
    condition     = length(var.azs) >= 2
    error_message = "At least 2 AZs required"
  }
}

variable "tags" {
  type    = map(string)
  default = {}
}
```

## Outputs

```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "Private subnet IDs"
}

output "vpc_cidr" {
  value = aws_vpc.main.cidr_block
}
```

## Main

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.cidr
  
  tags = merge(var.tags, {
    Name = "${var.name}-vpc"
  })
}

resource "aws_subnet" "private" {
  count = length(var.azs)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr, 8, count.index)
  availability_zone = var.azs[count.index]
  
  tags = merge(var.tags, {
    Name = "${var.name}-private-${var.azs[count.index]}"
  })
}
```

## Versions

```hcl
# modules/vpc/versions.tf
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

For consumer compatibility.

## README

Documentation:
```markdown
# VPC Module

## Usage

```hcl
module "vpc" {
  source = "./modules/vpc"
  cidr   = "10.0.0.0/16"
  azs    = ["us-east-1a", "us-east-1b"]
}
```

## Inputs
| Name | Type | Required | Description |
|---|---|---|---|
| cidr | string | yes | VPC CIDR |

## Outputs
...
```

Auto-generate with terraform-docs.

## terraform-docs

```bash
brew install terraform-docs
cd modules/vpc
terraform-docs markdown table . > README.md
```

Generates inputs/outputs tables.

CI integration: enforce up-to-date.

## Examples

```
modules/vpc/examples/
├── basic/
│   └── main.tf
├── advanced/
│   └── main.tf
└── multi-az/
    └── main.tf
```

Each example uses module:
```hcl
# examples/basic/main.tf
module "vpc" {
  source = "../../"   # the module
  cidr   = "10.0.0.0/16"
  azs    = ["us-east-1a"]
}
```

For: docs by example; test cases.

## Composition

Module using modules:
```hcl
# modules/network/main.tf
module "vpc" {
  source = "../vpc"
  cidr   = var.cidr
}

module "subnets" {
  source = "../subnets"
  vpc_id = module.vpc.vpc_id
}
```

Hierarchies of modules.

## Variables Best Practices

### Required vs Optional
```hcl
variable "name" {
  type = string
  # no default = required
}

variable "tags" {
  type    = map(string)
  default = {}    # optional
}
```

### Validation
Catch errors at plan time:
```hcl
validation {
  condition     = ...
  error_message = "..."
}
```

### Type Constraints
Strict types:
```hcl
type = list(object({
  name = string
  port = number
}))
```

Catches bad input.

## Outputs Best Practices

### Document
```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID for downstream resources"
}
```

### Sensitive
```hcl
output "db_password" {
  value     = aws_db_instance.main.password
  sensitive = true
}
```

### Aggregate
```hcl
output "subnet_ids" {
  value = {
    private = aws_subnet.private[*].id
    public  = aws_subnet.public[*].id
  }
}
```

Group related.

## Best Practices

- Single Responsibility (one concern)
- Clear inputs (typed, validated, documented)
- Clear outputs (documented, sensitive when needed)
- Versioned (tagged releases)
- Examples
- Tests
- README (auto-generated)
- Backwards compat (semver)

## Common Mistakes

- Mega-module (does everything)
- Module per resource (overhead)
- Magic numbers (hardcoded)
- No outputs (unconsumable)
- No version pin (consumer breaks)

## When to Module

- Reused 2+ times
- Encapsulates pattern (VPC + subnets + routes)
- Hides complexity

When NOT:
- One-off
- Simple wrapper (just inline)

## Module Granularity

| Size | Pros | Cons |
|---|---|---|
| Tiny (1 resource) | Reuse | Overhead |
| Medium (pattern) | Useful | Some flexibility lost |
| Big (whole stack) | Convenient | Tied to one pattern |

Aim for medium: encapsulates pattern, reusable, flexible.

## Provider Pattern

Best: caller provides provider; module doesn't:
```hcl
# Module: doesn't declare provider
resource "aws_instance" "x" {}

# Caller
provider "aws" {
  region = "us-east-1"
}

module "x" {
  source = "..."
}
```

For multi-region:
```hcl
# Caller passes alias
module "x" {
  providers = {
    aws = aws.west
  }
}
```

## Required Providers in Module

```hcl
terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 5.0"
      configuration_aliases = [aws.replica]   # for multi-region
    }
  }
}
```

Module declares; caller satisfies.

## State

Each `module` block: separate namespace in state:
```
module.vpc.aws_vpc.main
module.vpc.aws_subnet.private[0]
```

No separate state file (still one for root + all modules).

## Refactoring

Moving resources between modules:
```hcl
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

Or `terraform state mv` (covered earlier).

## Versioning Strategy

Semver:
- Major: breaking change (input renamed, removed)
- Minor: backward-compat (new optional input)
- Patch: bug fix

Document in CHANGELOG.

## Public vs Private

- Public Registry: Terraform Registry. Browse, version, doc.
- Private Registry: HCP Terraform, Spacelift, Artifactory.
- Git-based: free private; less polish.

For org: private registry or Git.

## Examples Module Catalog

terraform-aws-modules: massive catalog of community modules:
- vpc
- eks
- rds
- s3-bucket
- iam
- etc.

Battle-tested. Reuse vs reinvent.

## Quick Refs

```bash
# Validate
terraform validate

# Format
terraform fmt -recursive

# Init (downloads modules)
terraform init

# Plan
terraform plan
```

## Interview Prep

**Mid**: "What's a Terraform module."

**Senior**: "Module design for VPC."

**Staff**: "Module strategy for 50-team org."

## Next Topic

→ [T02 — Versioning & the Registry](T02-Versioning-Registry.md)
