# L10/C02/T01 — HCL Syntax

## Learning Objectives

- Write HCL fluently
- Use language features

## HCL

HashiCorp Configuration Language. Declarative; JSON-compatible.

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxx"
  instance_type = "t3.micro"
  
  tags = {
    Name = "web"
  }
}
```

## Block Structure

```
BLOCK_TYPE "LABEL_1" "LABEL_2" {
  ATTRIBUTE = VALUE
  NESTED_BLOCK {
    ...
  }
}
```

Examples:
- `resource "type" "name" {}`
- `data "type" "name" {}`
- `variable "name" {}`
- `output "name" {}`
- `module "name" {}`
- `provider "name" {}`

## Types

```hcl
# String
name = "web"

# Number
count = 3

# Bool
enabled = true

# List
tags = ["dev", "prod"]

# Map
labels = {
  env  = "prod"
  team = "platform"
}

# Object
server = {
  name = "web"
  port = 80
}

# Tuple (heterogeneous)
mixed = [1, "two", true]

# Null
nullable = null
```

## Variables

```hcl
variable "region" {
  type    = string
  default = "us-east-1"
  description = "AWS region"
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "tags" {
  type = map(string)
  default = {}
}

variable "subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}
```

Reference: `var.region`.

## Locals

```hcl
locals {
  common_tags = {
    Project   = "myapp"
    ManagedBy = "terraform"
  }
  
  bucket_name = "${var.project}-${var.env}-${random_id.suffix.hex}"
}
```

Reference: `local.common_tags`.

For computed / repeated values.

## Outputs

```hcl
output "instance_id" {
  value       = aws_instance.web.id
  description = "Instance ID"
}

output "private_ip" {
  value     = aws_instance.web.private_ip
  sensitive = true
}
```

After `apply`: displayed (unless sensitive).

Consumable by other modules.

## References

`<RESOURCE_TYPE>.<NAME>.<ATTRIBUTE>`:
```hcl
resource "aws_subnet" "main" {
  vpc_id = aws_vpc.main.id
}
```

`aws_vpc.main.id`: refers to id of VPC.

## Expressions

```hcl
# Arithmetic
total = var.x + var.y

# Comparison
is_prod = var.env == "prod"

# Logical
allowed = var.enabled && var.region == "us-east-1"

# Ternary
size = var.env == "prod" ? "large" : "small"

# String interpolation
name = "myapp-${var.env}"

# Concat
list1 = concat(var.a, var.b)
```

## Functions

Built-in:
- String: `format`, `replace`, `upper`, `lower`, `trim`, `split`, `join`
- Numeric: `min`, `max`, `abs`, `ceil`, `floor`
- Collection: `length`, `concat`, `merge`, `keys`, `values`, `flatten`, `compact`, `sort`
- Encoding: `jsonencode`, `jsondecode`, `yamlencode`, `base64encode`
- Filesystem: `file`, `templatefile`, `fileexists`
- Date: `timestamp`, `formatdate`
- Hash: `md5`, `sha1`, `sha256`
- IP: `cidrsubnet`, `cidrhost`
- Type: `tostring`, `tonumber`

Examples:
```hcl
upper("hello")             # "HELLO"
length([1, 2, 3])          # 3
merge({a=1}, {b=2})        # {a=1, b=2}
cidrsubnet("10.0.0.0/16", 8, 0)   # "10.0.0.0/24"
templatefile("init.sh.tpl", {name="web"})
```

## For Expressions

List comprehension:
```hcl
upper_list = [for s in var.list : upper(s)]
filtered = [for s in var.list : s if length(s) > 3]
```

Map:
```hcl
tag_map = {for k, v in var.input : k => upper(v)}
```

For dynamic data shaping.

## Splat Expression

Collect attribute across many:
```hcl
all_ids = aws_instance.web[*].id
```

For multi-instance resources.

## Dynamic Blocks

Generate repeated nested blocks:
```hcl
resource "aws_security_group" "web" {
  dynamic "ingress" {
    for_each = var.ingress_ports
    content {
      from_port = ingress.value
      to_port   = ingress.value
      protocol  = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

vs hardcoded multiple ingress.

## Comments

```hcl
# Single line
// Single line (also)
/* multi
   line */
```

## Indent + Style

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxx"
  instance_type = "t3.micro"
  
  tags = {
    Name = "web"
  }
}
```

`terraform fmt` enforces:
```bash
terraform fmt -recursive
```

Always commit formatted.

## Multi-Line Strings

```hcl
script = <<-EOT
  #!/bin/bash
  apt-get update
  apt-get install -y nginx
EOT
```

`<<-` strips leading whitespace.

## Conditional

```hcl
resource "aws_instance" "prod_only" {
  count = var.env == "prod" ? 1 : 0
  ...
}
```

count=0: resource not created.

## Count vs For Each

```hcl
# count: list (by index)
resource "aws_instance" "web" {
  count = 3
  ami   = "ami-xxx"
}
# Access: aws_instance.web[0], aws_instance.web[1], ...

# for_each: map (by key)
resource "aws_instance" "named" {
  for_each = {
    web  = "ami-1"
    db   = "ami-2"
  }
  ami = each.value
}
# Access: aws_instance.named["web"]
```

`for_each` better for named instances; `count` for homogenous.

### The `count` Reindexing Gotcha (important)

`count` addresses instances **by positional index** in state: `[0]`, `[1]`, `[2]`. The index is the identity. Remove or insert an element in the **middle** of a count-driven list and every later index shifts — Terraform then plans to **destroy and recreate** the shifted resources, even though you only meant to remove one.

Concrete example. Start with three users by index:

```hcl
variable "users" {
  default = ["alice", "bob", "carol"]
}

resource "aws_iam_user" "team" {
  count = length(var.users)
  name  = var.users[count.index]
}
# State: team[0]=alice, team[1]=bob, team[2]=carol
```

Now remove `bob` (the middle element) → `["alice", "carol"]`:

```
team[0] = alice   (unchanged)
team[1] = bob  -> carol     # index 1 now maps to carol
team[2] = carol -> (gone)   # index 2 removed
```

Terraform's plan:
```
# aws_iam_user.team[1] will be UPDATED IN PLACE or DESTROYED+CREATED
~ name = "bob" -> "carol"
# aws_iam_user.team[2] will be DESTROYED
- name = "carol"
```

So removing **bob** destroys/recreates **carol** too — disruptive for stateful resources (instances replaced, EBS volumes lost, IPs changed). With more elements the blast radius is everything after the removed index.

**`for_each` fixes this** — instances are keyed, not indexed:

```hcl
resource "aws_iam_user" "team" {
  for_each = toset(["alice", "bob", "carol"])
  name     = each.key
}
# State: team["alice"], team["bob"], team["carol"]
```

Remove `bob` → only `team["bob"]` is destroyed; `alice` and `carol` are untouched. Keys are stable identities; order changes don't reindex anything.

**Rule of thumb:** use `count` only for a fixed, homogeneous N where you never add/remove from the middle (or for the `count = condition ? 1 : 0` toggle). For anything keyed, named, or likely to change membership, use `for_each`.

Migrating an existing `count` resource to `for_each` reindexes state once; use `moved` blocks or `terraform state mv` to map old indices to new keys without destroy/recreate:

```hcl
moved {
  from = aws_iam_user.team[0]
  to   = aws_iam_user.team["alice"]
}
```

### Provider Lock File

`terraform init` writes `.terraform.lock.hcl`, which pins the **exact provider versions** (and their checksums) selected under your `required_providers` constraints. Commit it — it's the lockfile that makes provider versions reproducible across machines and CI (analogous to `package-lock.json`). Update deliberately with `terraform init -upgrade`. (Covered in depth in T02.)

## Tags

```hcl
locals {
  common_tags = {
    Project   = var.project
    Env       = var.env
    Team      = var.team
    ManagedBy = "terraform"
  }
}

resource "aws_instance" "web" {
  tags = merge(local.common_tags, {
    Name = "web"
  })
}
```

DRY tagging.

## Files

Convention:
- `main.tf`: resources
- `variables.tf`: vars
- `outputs.tf`: outputs
- `providers.tf`: providers
- `versions.tf`: required versions

Terraform reads all `*.tf` in dir.

## Modules

```hcl
module "vpc" {
  source = "./modules/vpc"
  
  cidr = "10.0.0.0/16"
  azs  = ["us-east-1a", "us-east-1b"]
}

# Use output
subnet_id = module.vpc.subnet_ids[0]
```

## Provider

```hcl
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = local.common_tags
  }
}
```

For multi-region:
```hcl
provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

resource "aws_instance" "in_west" {
  provider = aws.west
  ...
}
```

## Terraform Block

```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "my-tfstate"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}
```

## Best Practices

- `terraform fmt` always
- Use locals for repeated logic
- Variables for inputs
- Module compositions
- Tags consistent
- Comments for non-obvious

## Common Mistakes

- Hardcoded values
- Missing tags
- No outputs (modules unconsumable)
- No `terraform fmt`
- Manual changes (drift)

## Quick Refs

```bash
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
terraform destroy
```

## Interview Prep

**Junior**: "HCL basics."

**Mid**: "Count vs for_each."

**Senior**: "Dynamic blocks for SG."

## Next Topic

→ [T02 — Providers, Resources, Data Sources](T02-Providers-Resources-Data.md)
