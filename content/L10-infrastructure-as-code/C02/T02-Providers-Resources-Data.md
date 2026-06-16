# L10/C02/T02 — Providers, Resources, Data Sources

## Learning Objectives

- Configure providers
- Use resources + data sources

## Provider

Plugin that wraps an API:
- AWS
- Azure
- GCP
- Kubernetes
- GitHub
- Helm
- Random
- ~3000 community providers

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

## Provider Auth

For AWS:
1. `aws configure` profile
2. Env vars (`AWS_ACCESS_KEY_ID`, ...)
3. IAM role (EC2 instance profile)
4. AWS SSO

Don't put creds in `.tf` files.

## Multiple Providers

```hcl
provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

resource "aws_instance" "east" {
  ami = "..."
}

resource "aws_instance" "west" {
  provider = aws.west
  ami = "..."
}
```

For multi-region.

Or multi-account:
```hcl
provider "aws" {
  alias  = "prod"
  assume_role {
    role_arn = "arn:aws:iam::PROD:role/Deploy"
  }
}
```

## Provider Versions

Constraints:
```hcl
required_providers {
  aws = {
    version = "~> 5.0"      # 5.x but not 6
    version = ">= 5.0, < 6"  # same
    version = "= 5.10.0"     # exact
  }
}
```

Lock to prevent breakage.

## Lock File

`.terraform.lock.hcl` records exact provider versions. Commit it.

```bash
terraform init -upgrade   # update
```

## Resources

Things Terraform manages:
```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxx"
  instance_type = "t3.micro"
}
```

`aws_instance`: type (from AWS provider).
`web`: local name (Terraform-only; not in AWS).

Each resource:
- Created on apply
- Tracked in state
- Updated on plan changes
- Destroyed on remove

## Arguments vs Attributes

Arguments: inputs (you set).
Attributes: outputs (computed).

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxx"       # argument
  instance_type = "t3.micro"      # argument
}

# Access computed
output "id" {
  value = aws_instance.web.id     # attribute
}

output "ip" {
  value = aws_instance.web.private_ip
}
```

Docs list both.

## Data Sources

Read-only: query existing infrastructure.

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "web" {
  ami = data.aws_ami.amazon_linux.id
  ...
}
```

vs hardcoding AMI ID.

## Common Data Sources

```hcl
# Account info
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Existing VPC
data "aws_vpc" "main" {
  tags = {Name = "main-vpc"}
}

# Latest AMI
data "aws_ami" "amazon_linux_2023" {...}

# Existing subnet
data "aws_subnets" "private" {
  filter {
    name   = "tag:Type"
    values = ["private"]
  }
}

# Secrets Manager secret
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/db"
}
```

## Reading from Other Tools

Data sources connect to:
- Manual / external setup
- Other Terraform states (remote state)
- API responses

```hcl
# Other state
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "tfstate"
    key    = "vpc/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_subnet" "app" {
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
}
```

For modular Terraform across multiple state files.

## Meta-Arguments

Available on all resources:

### depends_on
Force order:
```hcl
resource "aws_instance" "web" {
  ...
  depends_on = [aws_security_group.web]
}
```

Usually implicit (via references); explicit when needed.

### count
```hcl
resource "aws_instance" "web" {
  count = 3
  ami   = "ami-xxx"
}
# Access: aws_instance.web[0]
```

### for_each
```hcl
resource "aws_instance" "named" {
  for_each = {
    web = "ami-1"
    db  = "ami-2"
  }
  ami = each.value
}
# Access: aws_instance.named["web"]
```

### provider
```hcl
resource "aws_instance" "west" {
  provider = aws.west
  ami      = "..."
}
```

### lifecycle
```hcl
resource "aws_instance" "web" {
  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
    ignore_changes        = [tags]
  }
}
```

## Lifecycle

**create_before_destroy**: build new before tearing old (avoid downtime on replace).

**prevent_destroy**: error if destroy attempted. Safety guard.

**ignore_changes**: don't drift-update specified attributes (e.g., tags managed by AWS Org).

**replace_triggered_by**: force replace when another resource changes.

## Importing Existing

For resources created outside Terraform:
```bash
terraform import aws_instance.web i-0abc1234
```

Adds to state. You still need matching resource block in code.

For complex: use `terraform plan` to verify match.

## Resource Naming

Use snake_case for local name:
```hcl
resource "aws_instance" "web_server" {}
```

Don't include type:
```hcl
# BAD
resource "aws_instance" "web_instance" {}

# GOOD
resource "aws_instance" "web" {}
```

## Module Outputs

Modules expose attributes via outputs:
```hcl
# module/vpc/outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}

# root
module "vpc" {
  source = "./modules/vpc"
}

# Use
subnet_id = module.vpc.vpc_id
```

## Provider Initialization

```bash
terraform init
```

Downloads providers (defined in required_providers); creates lock file.

Re-run after provider changes.

## Provider Specifically

Some providers require config:
- AWS: region, access keys
- Kubernetes: kubeconfig
- GitHub: token
- Datadog: API key

Sensitive: use env vars or `terraform.tfvars` (gitignored).

## Aliases (Multi-Provider)

```hcl
provider "kubernetes" {
  alias = "cluster_a"
  host  = data.aws_eks_cluster.a.endpoint
}

provider "kubernetes" {
  alias = "cluster_b"
  host  = data.aws_eks_cluster.b.endpoint
}

resource "kubernetes_deployment" "in_a" {
  provider = kubernetes.cluster_a
  ...
}
```

For: deploy to multiple K8s clusters.

## Provider Required Block

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}
```

Explicit > implicit.

## Common Resources

```hcl
aws_vpc, aws_subnet, aws_internet_gateway, aws_nat_gateway, aws_route_table
aws_security_group, aws_security_group_rule
aws_instance, aws_launch_template, aws_autoscaling_group
aws_lb, aws_lb_target_group, aws_lb_listener
aws_s3_bucket, aws_s3_object
aws_iam_role, aws_iam_policy, aws_iam_role_policy_attachment
aws_lambda_function, aws_lambda_permission
aws_dynamodb_table, aws_rds_cluster, aws_db_instance
aws_eks_cluster, aws_eks_node_group
```

## Best Practices

- Use data sources over hardcoding
- Lock provider versions
- Default tags via provider
- Meaningful local names
- Lifecycle blocks where needed
- Import existing resources properly

## Common Mistakes

- Hardcoded ARNs / IDs (use data sources)
- No version lock (provider upgrade breaks)
- Manual changes (drift)
- Same resource managed in multiple places (conflict)
- Forgot data source dependency

## Quick Refs

```bash
terraform init               # download providers
terraform providers          # list providers
terraform providers lock     # lock platform
terraform import aws_x.y id  # import existing
```

## Interview Prep

**Mid**: "Resource vs data source."

**Senior**: "Multi-region with aliases."

**Staff**: "Provider design for org."

## Next Topic

→ [T03 — Variables, Locals, Outputs](T03-Variables-Locals-Outputs.md)
