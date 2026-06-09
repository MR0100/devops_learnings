# L10/C03/T02 — Backends

## Learning Objectives

- Configure remote state backend
- Pick backend

## Backends

Where Terraform state lives.

## Local (Default)

```hcl
# No backend block needed
```

State in `terraform.tfstate` locally.

For: solo, learning, demos.

NOT for: teams, production.

## S3 + DynamoDB

Most common AWS pattern.

```hcl
terraform {
  backend "s3" {
    bucket         = "my-tfstate"
    key            = "prod/vpc/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tflock"
    encrypt        = true
  }
}
```

- S3: stores state
- DynamoDB: locks
- Encrypted (KMS)
- Versioned (S3 versioning)

## Setup

```bash
# S3 bucket (manual or via Terraform; chicken-egg)
aws s3 mb s3://my-tfstate
aws s3api put-bucket-versioning --bucket my-tfstate --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket my-tfstate --server-side-encryption-configuration '{...}'

# DynamoDB
aws dynamodb create-table --table-name tflock --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST
```

Bootstrap once; reuse forever.

## Chicken-and-Egg

For first time: create S3/DDB manually OR via local Terraform; then migrate.

Or use bootstrap pattern: Terraform module to create state backend resources.

## Key Naming

```
s3://my-tfstate/
├── prod/
│   ├── vpc/terraform.tfstate
│   ├── eks/terraform.tfstate
│   └── app/terraform.tfstate
├── staging/
└── dev/
```

Per workload, per env.

## Multiple Workspaces

```hcl
backend "s3" {
  bucket = "my-tfstate"
  key    = "vpc/terraform.tfstate"
  ...
}
```

With workspaces:
```
s3://my-tfstate/env:/prod/vpc/terraform.tfstate
s3://my-tfstate/env:/staging/vpc/terraform.tfstate
```

`env:/<workspace>/` prefix added.

## Terraform Cloud / HCP Terraform

```hcl
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "prod-vpc"
    }
  }
}
```

HashiCorp-hosted:
- State managed
- Runs in cloud
- VCS integration
- Policy enforcement
- Variable sets
- Team management

Free tier; paid for larger teams.

## Azure Storage

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate"
    storage_account_name = "tfstate12345"
    container_name       = "state"
    key                  = "prod.terraform.tfstate"
  }
}
```

For Azure-native; locking via blob lease.

## GCS

```hcl
terraform {
  backend "gcs" {
    bucket = "tfstate"
    prefix = "terraform/state"
  }
}
```

For GCP-native.

## Consul

```hcl
terraform {
  backend "consul" {
    address = "consul.example.com"
    path    = "tf/state"
  }
}
```

For Consul shops.

## Kubernetes

```hcl
terraform {
  backend "kubernetes" {
    secret_suffix    = "state"
    config_path      = "~/.kube/config"
  }
}
```

State in K8s Secret. For K8s-native.

## HTTP Backend

Custom REST endpoint:
```hcl
backend "http" {
  address = "https://tfstate.example.com/state"
  lock_address = "https://tfstate.example.com/state/lock"
  unlock_address = "https://tfstate.example.com/state/lock"
}
```

For: custom state server, GitLab managed Terraform state.

## Encryption

S3: server-side encryption (SSE-S3 or SSE-KMS).
GCS: default encryption.
Azure: encrypted by default.
TFC: encrypted at rest.

For sensitive: KMS / customer-managed.

## Access Control

IAM (S3 backend):
```json
{
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ],
    "Resource": "arn:aws:s3:::tfstate/*"
  }, {
    "Effect": "Allow",
    "Action": [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ],
    "Resource": "arn:aws:dynamodb:*:*:table/tflock"
  }]
}
```

Plus KMS key permission if SSE-KMS.

## Backend Configuration

Static (recommended):
```hcl
backend "s3" {
  bucket = "my-tfstate"
  ...
}
```

Variables NOT allowed in backend config (chicken-egg).

For dynamic: `-backend-config` flag:
```bash
terraform init -backend-config="bucket=$ENV-tfstate"
```

Or file:
```bash
terraform init -backend-config=prod.tfbackend
```

## Workspace per Env vs Backend per Env

### Workspaces
Same backend; different workspaces. One bucket; many states.

```bash
terraform workspace new prod
terraform apply -workspace=prod
```

Simple but shared bucket / shared IAM.

### Backend per Env
Different bucket / DDB / config per env.

```bash
# Production: separate backend
terraform init -backend-config=prod.tfbackend
```

Better isolation. Per-env access control.

For prod: separate backend recommended.

## Switching Backends

```hcl
# Old
backend "local" {}

# New
backend "s3" {...}
```

```bash
terraform init -migrate-state
```

Asks: copy state? Yes.

Old state file remains; review then delete.

## CI / CD Integration

CI runs:
```bash
terraform init
terraform plan -out=plan
# Save plan
# Approval
terraform apply plan
```

State persists in backend; CI ephemeral.

## State File Anatomy

```json
{
  "version": 4,
  "terraform_version": "1.7.0",
  "serial": 42,
  "lineage": "abc-uuid",
  "outputs": {...},
  "resources": [...]
}
```

`serial`: increment per change. `lineage`: identifies state lineage; changes if state recreated.

## Locking Detail

DynamoDB item:
```
{
  "LockID": "my-tfstate/prod/vpc/terraform.tfstate",
  "Info": "{...}"
}
```

Acquired before write; released after.

If process killed: stale lock. Force unlock:
```bash
terraform force-unlock LOCK_ID
```

Use carefully (only if sure no other apply running).

## Backups

S3 versioning: built-in.
Manual:
```bash
terraform state pull > backup-$(date +%s).tfstate
```

Before risky surgery.

## Cost

S3: storage + requests. State file < 1 MB; pennies.
DynamoDB: PAY_PER_REQUEST; pennies.
TFC: free tier; paid for larger teams.

Negligible.

## Common Mistakes

- Local state for team
- No locking (race conditions)
- State committed to Git (security; conflicts)
- No backup of S3 bucket
- DynamoDB without billing-mode PAY_PER_REQUEST (provisioned wastes)
- Single state for whole org (bottleneck)

## Best Practices

- Remote backend (S3+DDB or TFC)
- Versioning + encryption
- Restrictive IAM
- One state per workload (not monolith)
- Per-env backend (better isolation)
- Backup before surgery
- Document backend choices

## Migration Plan

From local to S3:
1. Add backend block
2. `terraform init -migrate-state`
3. Verify
4. Delete local `terraform.tfstate`
5. Commit backend config

From S3 to TFC:
1. `terraform login`
2. Add cloud block
3. `terraform init -migrate-state`
4. Verify in TFC
5. Delete S3 state (or keep as backup)

## When Pick TFC

- Want managed runs
- VCS integration native
- Variable sets across workspaces
- Sentinel policies
- Audit / RBAC

When pick S3:
- Already in AWS
- Cost-sensitive
- Custom runner needed
- Multi-cloud not TFC-centric

## Quick Refs

```bash
# Init backend
terraform init

# Migrate
terraform init -migrate-state

# Reconfigure (without migration)
terraform init -reconfigure

# Backend config from file
terraform init -backend-config=prod.tfbackend

# Force unlock
terraform force-unlock LOCK_ID
```

## Interview Prep

**Mid**: "Why remote state."

**Senior**: "Backend per env vs workspaces."

**Staff**: "State strategy for 50 workloads."

## Next Topic

→ [T03 — State Locking & Concurrency](T03-State-Locking.md)
