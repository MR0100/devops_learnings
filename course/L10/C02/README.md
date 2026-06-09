# L10/C02 — Terraform Fundamentals

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-HCL-Syntax.md) | HCL Syntax | 1 hr |
| [T02](T02-Providers-Resources.md) | Providers, Resources, Data Sources | 1 hr |
| [T03](T03-Variables-Locals-Outputs.md) | Variables, Locals, Outputs | 1 hr |
| [T04](T04-Lifecycle.md) | Lifecycle Meta-Arguments | 0.5 hr |

## HCL (HashiCorp Configuration Language)

Declarative, JSON-like with comments and expressions.

```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "prod/network/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Environment = "prod"
      ManagedBy   = "terraform"
    }
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}

locals {
  common_tags = {
    Project = "myapp"
    Env     = var.environment
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "myapp-${var.environment}-data-${data.aws_caller_identity.current.account_id}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_caller_identity" "current" {}

output "bucket_name" {
  value = aws_s3_bucket.data.id
}
```

## Resources, Data Sources, Providers

### Resources
- Things you CREATE and manage
- `resource "type" "name" { ... }`
- Address: `aws_s3_bucket.data`

### Data Sources
- Things you READ (already exist)
- `data "type" "name" { ... }`
- Address: `data.aws_ami.latest.id`

### Providers
- Plugin for a cloud or service
- Each has versions; pin them (semver)
- Required in `required_providers`

### Provider Configuration & Multi-Region
```hcl
provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

resource "aws_s3_bucket" "west_data" {
  provider = aws.west
  bucket   = "..."
}
```

## Variables

### Input Variables
```hcl
variable "instance_count" {
  type        = number
  default     = 3
  description = "..."
  sensitive   = false
  nullable    = false
}
```

### Variable Sources (precedence, low → high)
1. Defaults in `variable` block
2. Environment variable `TF_VAR_instance_count=5`
3. `terraform.tfvars`
4. `*.auto.tfvars`
5. `-var` and `-var-file` CLI

### Types
```hcl
type = string
type = number
type = bool
type = list(string)
type = set(string)
type = map(any)
type = object({ name = string, port = number })
type = tuple([string, number, bool])
```

## Locals

Internal computed values:
```hcl
locals {
  name_prefix = "myapp-${var.environment}"
  common_tags = merge(var.tags, { Env = var.environment })
}
```

## Outputs

Expose values:
```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "..."
  sensitive   = false
}
```

Used:
- After `terraform apply` (displayed)
- By `terraform output` command
- By another stack via remote state data source

## Lifecycle Meta-Arguments

```hcl
resource "aws_instance" "x" {
  ...
  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
    ignore_changes        = [tags]
    replace_triggered_by  = [aws_security_group.app.id]
  }
}
```

- **create_before_destroy**: avoid downtime by creating new before destroying old
- **prevent_destroy**: hard block on `terraform destroy` (production DB!)
- **ignore_changes**: don't update specific attributes (e.g., tags managed externally)
- **replace_triggered_by**: replace when other resource changes

## Other Meta-Arguments

- `count = N` — make N copies (legacy, use for_each when possible)
- `for_each = toset([...])` — iterate over set/map; better than count for adds/removes
- `depends_on = [resource.x]` — explicit dependency
- `provider = aws.west` — pick provider alias

## for_each vs count

```hcl
# count — by index (changes shift)
resource "aws_instance" "by_count" {
  count         = 3
  instance_type = "t3.micro"
  ami           = "ami-X"
}

# for_each — by key (stable)
resource "aws_instance" "by_each" {
  for_each      = toset(["web1", "web2", "web3"])
  instance_type = "t3.micro"
  ami           = "ami-X"
  tags          = { Name = each.key }
}
```

Use `for_each` unless you have a specific reason to use `count`.

## Common Functions

```hcl
length(var.list)
length(keys(var.map))
contains(var.list, "value")
lookup(var.map, "key", "default")
merge(var.a, var.b)
concat(list1, list2)
toset(var.list)
tolist(var.set)
keys(var.map)
values(var.map)
flatten(var.list)
distinct(var.list)
join(",", var.list)
split(",", var.string)
format("hello-%s", var.x)
formatdate("YYYY-MM-DD", timestamp())
file("./config.yaml")
templatefile("./config.tpl", { var = value })
yamlencode(var.obj)
jsonencode(var.obj)
base64encode(var.x)
sha256(var.x)
```

## Workflow

```bash
terraform init        # download providers, configure backend
terraform plan        # preview changes
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
terraform apply       # plan + apply with confirmation
terraform destroy     # destroy all
terraform validate    # syntax check
terraform fmt -recursive  # format
terraform show        # show current state
terraform output      # show outputs
terraform state list  # list resources
```

## Interview Themes

- "Walk me through HCL"
- "Difference between resource and data source"
- "When for_each vs count"
- "What does create_before_destroy solve?"
- "Lifecycle ignore_changes — use case"
