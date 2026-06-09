# L10/C03 — Terraform State

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-What-State.md) | What State Is & Why It Matters | 1 hr |
| [T02](T02-Backends.md) | Backends (S3 + DynamoDB, Terraform Cloud, GCS, Azure Storage) | 1 hr |
| [T03](T03-State-Locking.md) | State Locking & Concurrency | 0.5 hr |
| [T04](T04-State-Commands.md) | terraform state Commands (mv, rm, import, replace) | 1 hr |
| [T05](T05-Drift-Detection.md) | State Drift Detection | 0.5 hr |

## What State Is

The `.tfstate` file maps Terraform's resource references (`aws_instance.web`) to real cloud resources (`i-abc123`).

Without state:
- Terraform can't know "is this instance already created?"
- Every plan would be "create all" or "delete all"

With state:
- Terraform compares desired (code) vs actual (state) vs real (refresh via API)
- Computes diff
- Applies only needed changes

### What's in State
- Resource attributes (most cloud-returned data)
- Resource dependencies
- Provider config
- Outputs

> **State files contain sensitive data.** Database passwords, IAM access keys (in some cases), Lambda env vars. Treat as a secret.

## Backends

State stored locally is a disaster for teams. Use a remote backend.

### S3 + DynamoDB (AWS Most Common)
```hcl
backend "s3" {
  bucket         = "my-tf-state"
  key            = "prod/network/terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "tf-lock"
  encrypt        = true
}
```

Best practices:
- Versioning enabled on bucket
- Block Public Access
- Bucket policy + IAM
- DynamoDB table: `LockID` (string) partition key
- Encryption: SSE-S3 or SSE-KMS
- Bucket replication for DR

### Terraform Cloud / Enterprise
```hcl
cloud {
  organization = "myorg"
  workspaces { name = "prod-network" }
}
```

Adds: web UI, run history, policy as code (Sentinel), variable sets.

### GCS (GCP)
```hcl
backend "gcs" {
  bucket = "my-tf-state"
  prefix = "prod/network"
}
```

GCS has object versioning + locking via GCS object generations.

### Azure Storage
```hcl
backend "azurerm" {
  resource_group_name  = "tf-state-rg"
  storage_account_name = "tfstate"
  container_name       = "tfstate"
  key                  = "prod.tfstate"
}
```

Uses blob lease for locking.

## State Locking

Prevents concurrent `apply` from corrupting state.

- S3 backend: DynamoDB lock
- GCS backend: object generation
- Azure backend: blob lease
- TFC: native

If a lock is stuck:
```bash
terraform force-unlock <LOCK_ID>
```

(Investigate why first.)

## State Commands

### Move a resource (no recreate)
```bash
terraform state mv aws_instance.old aws_instance.new
terraform state mv module.old.aws_instance.x module.new.aws_instance.x
```

Use when refactoring module structure.

### Remove from state (not from cloud!)
```bash
terraform state rm aws_instance.x
```

Use when:
- Resource managed externally now
- Migrating to another stack (rm here, import there)

### Import existing resources
```bash
terraform import aws_instance.web i-abc123
```

Brings existing cloud resource under Terraform management. Must have matching `resource` block in code.

Modern (`import` block, Terraform 1.5+):
```hcl
import {
  to = aws_instance.web
  id = "i-abc123"
}
```

Plan + apply imports — better than CLI.

### Replace (force recreate)
```bash
terraform apply -replace=aws_instance.web
# old: terraform taint aws_instance.web; terraform apply
```

### List & Show
```bash
terraform state list
terraform state show aws_instance.web
terraform state pull > state.json
```

## State Drift

Drift = real infra differs from state's view (someone changed it manually).

### Detect
```bash
terraform plan -refresh-only
terraform plan        # always refreshes by default; drift shows as diff
```

### Strategies
- Run `terraform plan` daily in CI, alert on drift
- Use Terraform Cloud drift detection
- Use AWS Config / GCP Asset Inventory to detect changes outside Terraform
- Enforce IAM permissions that prevent manual changes to TF-managed resources
- Education + tooling: make TF the easiest way to make changes

## Disasters & Recovery

### Lost State
- If versioning enabled, restore from S3 version
- TFC has state history
- Worst case: re-import every resource (painful)

### Corrupt State
- Restore from version
- Or manually edit (last resort) — use `terraform state pull > backup.json`; edit; `push`

### Migrating Backends
```bash
# Move state to new backend
terraform init -migrate-state
```

## Sensitive Data in State

State contains secrets. Mitigate:
- Encryption at rest (KMS)
- IAM strict on state bucket
- Don't put secrets in TF (use external secrets, generate at apply time)
- Mark variables and outputs `sensitive = true`

## Interview Themes

- "Why does Terraform need state?"
- "What goes wrong with local state?"
- "How does state locking work?"
- "Walk through importing existing infra"
- "How do you detect drift?"
- "State file contains secrets — what do you do?"
