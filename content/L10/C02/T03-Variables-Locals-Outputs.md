# L10/C02/T03 — Variables, Locals, Outputs

## Learning Objectives

- Use variables, locals, outputs
- Pick right tool

## Variables

Inputs from outside:
```hcl
variable "region" {
  type    = string
  default = "us-east-1"
}

variable "env" {
  type        = string
  description = "Environment (dev/staging/prod)"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.env)
    error_message = "env must be dev/staging/prod"
  }
}
```

## Setting Values

Priority (high to low):
1. `-var "key=value"` on CLI
2. `-var-file=...` on CLI
3. `*.auto.tfvars` files
4. `terraform.tfvars` file
5. `TF_VAR_<name>` env vars
6. `default` in variable block

## terraform.tfvars

```hcl
# terraform.tfvars
region = "us-east-1"
env    = "prod"
tags   = {
  Team = "platform"
}
```

Not committed if env-specific.

## Environment Variables

```bash
export TF_VAR_region=us-east-1
terraform apply
```

## Variable Types

```hcl
variable "name" { type = string }
variable "count" { type = number }
variable "enabled" { type = bool }
variable "tags" { type = map(string) }
variable "subnets" { type = list(string) }

# Complex
variable "server" {
  type = object({
    name = string
    port = number
  })
}

variable "servers" {
  type = list(object({
    name = string
    port = number
  }))
}
```

## Validation

```hcl
variable "instance_type" {
  type = string
  
  validation {
    condition     = can(regex("^[tm][3-7]\\.", var.instance_type))
    error_message = "Use t3-t7 or m3-m7 instance types."
  }
}
```

Multiple validation blocks allowed.

## Sensitive Variables

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

Not displayed in plan / apply output. Still in state (encrypted backend recommended).

## Locals

Computed values inside config:
```hcl
locals {
  common_tags = {
    Project     = var.project
    Environment = var.env
    ManagedBy   = "terraform"
  }
  
  name_prefix = "${var.project}-${var.env}"
  
  is_prod = var.env == "prod"
  
  instance_count = local.is_prod ? 10 : 2
}
```

Reference: `local.X`.

## When Local vs Variable

- Variable: external input
- Local: derived / computed / repeated

Don't pass everything as variable. Use locals for internal computation.

## Outputs

Exports from module / root:
```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "db_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}
```

After apply: shown unless sensitive.

## Output as Module Interface

Modules expose attributes via outputs:
```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}
```

Root references:
```hcl
module "vpc" {
  source = "./modules/vpc"
}

resource "aws_instance" "web" {
  subnet_id = module.vpc.private_subnet_ids[0]
}
```

## Reading Outputs

```bash
terraform output                       # all
terraform output vpc_id                # specific
terraform output -json                 # JSON for scripts
```

For CI / scripts:
```bash
VPC_ID=$(terraform output -raw vpc_id)
```

## Variable Files Pattern

For multiple environments:
```
terraform.tfvars            # default / dev
prod.tfvars                # prod overrides
staging.tfvars             # staging
```

Apply with file:
```bash
terraform apply -var-file=prod.tfvars
```

## Workspace vs Var File

For env isolation:

**Workspaces**: separate state per workspace; same code:
```bash
terraform workspace new prod
terraform workspace select prod
terraform apply
```

**Var files**: same workspace; different vars:
```bash
terraform apply -var-file=prod.tfvars
```

Both work; var files more flexible.

## Computed via Locals

```hcl
variable "subnet_count" {
  type = number
}

locals {
  azs           = data.aws_availability_zones.available.names
  subnet_cidrs  = [for i in range(var.subnet_count) : cidrsubnet(var.vpc_cidr, 8, i)]
  subnet_az_map = {for i in range(var.subnet_count) : local.subnet_cidrs[i] => local.azs[i % length(local.azs)]}
}

resource "aws_subnet" "main" {
  for_each = local.subnet_az_map
  cidr_block        = each.key
  availability_zone = each.value
}
```

## Sensitive Outputs

```hcl
output "db_password" {
  value     = random_password.db.result
  sensitive = true
}
```

Stored in state. State encrypted.

## CI Usage

```bash
terraform apply -auto-approve -var-file=prod.tfvars
DB_ENDPOINT=$(terraform output -raw db_endpoint)
echo "DB_ENDPOINT=$DB_ENDPOINT" >> $GITHUB_OUTPUT
```

Pass values between steps.

## Best Practices

- Type variables
- Default for optional
- Validate where useful
- Sensitive for secrets
- Locals for computed
- Outputs documented
- Description for all

## Common Mistakes

- No defaults (every plan prompts)
- No types (silent type errors)
- Sensitive forgotten
- Outputs not documented
- Locals for static (just hardcode)
- Locals abused (over-abstract)

## Tagging Pattern

```hcl
locals {
  required_tags = {
    Project   = var.project
    Env       = var.env
    Owner     = var.owner
    ManagedBy = "terraform"
  }
}

# Apply via provider default_tags
provider "aws" {
  default_tags {
    tags = local.required_tags
  }
}
```

All resources auto-tagged.

## Conditional Resource

```hcl
variable "create_bucket" {
  type    = bool
  default = false
}

resource "aws_s3_bucket" "optional" {
  count  = var.create_bucket ? 1 : 0
  bucket = "..."
}

# Reference with conditional
output "bucket_arn" {
  value = var.create_bucket ? aws_s3_bucket.optional[0].arn : null
}
```

## Variable Defaults in Modules

```hcl
# modules/lb/variables.tf
variable "enabled" {
  type    = bool
  default = true
}

variable "internal" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
```

Caller overrides what's needed; defaults for the rest.

## Heredoc + Templates

For complex strings:
```hcl
locals {
  user_data = <<-EOT
    #!/bin/bash
    yum install -y nginx
    systemctl enable nginx
    systemctl start nginx
  EOT
}

# Or external
locals {
  user_data = file("${path.module}/user_data.sh")
}

# Templated
locals {
  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    domain = var.domain
  })
}
```

## Output Aggregation

```hcl
output "all_endpoints" {
  value = {
    api  = aws_lb.api.dns_name
    web  = aws_lb.web.dns_name
    grpc = aws_lb.grpc.dns_name
  }
}
```

Group related outputs.

## Quick Refs

```bash
# Set var
terraform plan -var="region=us-west-2"

# Use file
terraform plan -var-file=prod.tfvars

# Outputs
terraform output
terraform output -json
terraform output -raw vpc_id
```

## Interview Prep

**Mid**: "var vs local."

**Senior**: "Output design for module."

**Staff**: "Multi-env via vars."

## Next Topic

→ [T04 — Lifecycle Meta-Arguments](T04-Lifecycle.md)
