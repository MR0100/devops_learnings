# L10/C09/T01 — Importing Brownfield Infrastructure

## Learning Objectives

- Bring existing resources under Terraform
- Apply at scale

## Brownfield

Existing infrastructure created manually / via console / other tools.

Bring under Terraform:
- Single source of truth
- IaC benefits
- Audit trail

## Strategy

1. Identify resources
2. Write Terraform block matching reality
3. Import to state
4. `terraform plan` — should show no changes
5. Refine until clean
6. Commit

Iterative.

## Single Resource

Old way (CLI):
```bash
terraform import aws_instance.web i-0abc123
```

Modern (import block, 1.5+):
```hcl
import {
  to = aws_instance.web
  id = "i-0abc123"
}

resource "aws_instance" "web" {
  # ... match existing
}
```

Apply imports.

## Workflow

```bash
# Add import block + resource block
terraform plan
# Shows what will be imported + diff

terraform apply
# Imports resource

terraform plan
# Should be clean (no changes)
```

## Identify Resource Attributes

```bash
aws ec2 describe-instances --instance-ids i-0abc123
```

Match all attributes in resource block.

For: avoid plan showing changes.

## Generate Config

```bash
terraform plan -generate-config-out=generated.tf
```

For import blocks: Terraform generates config.

```hcl
import {
  to = aws_instance.web
  id = "i-0abc123"
}
```

```bash
terraform plan -generate-config-out=generated.tf
```

Creates `generated.tf` with resource block.

Review; clean up.

## Mass Import

For many resources:
```hcl
import { to = aws_instance.web_1; id = "i-1" }
import { to = aws_instance.web_2; id = "i-2" }
import { to = aws_instance.web_3; id = "i-3" }
```

Or via script generating import blocks.

## Tools

### Terraformer
```bash
terraformer import aws --resources=ec2_instance,vpc --regions=us-east-1
```

Generates `.tf` + state for entire AWS account.

For: starting from scratch.

### former2
Web UI for AWS → Terraform / CFN / CDK.

For: occasional imports.

### Crossplane-style
Adopt resources without Terraform owning lifecycle.

## Refining

After import: plan may show:
```
~ aws_instance.web
    + tags = { ... }    # missing in code
    ~ instance_type = "t3.large" -> "t3.medium"   # mismatch
```

Update code to match reality.

Or apply intentional changes:
```hcl
resource "aws_instance" "web" {
  instance_type = "t3.large"   # intentional upgrade
}
```

## Module Imports

For resources inside module:
```hcl
import {
  to = module.network.aws_vpc.main
  id = "vpc-abc123"
}
```

Path through module.

## State Operations

After import:
```bash
terraform state list   # see imported
terraform state show aws_instance.web   # details
```

## Don't Import Everything

Some resources better managed elsewhere:
- App-specific state
- External tool managed (e.g., RDS via DMS)
- Auto-scaling group instances (just the ASG)

Pick boundaries.

## Per-Service Strategy

For huge migration:
- Per service / per team
- Not big-bang
- Test in non-prod first

## Caveat: State Already Has

Importing resource already managed elsewhere:
- Conflicts
- Race conditions
- Don't

Verify before import.

## Validation

After import:
- `terraform plan` clean
- `terraform refresh` no surprises
- Test small change works

## Cleanup

Remove import blocks after applied:
```hcl
# Remove
import {
  to = aws_instance.web
  id = "i-0abc123"
}

# Keep
resource "aws_instance" "web" {...}
```

For: tidiness.

## Common Issues

### Plan Shows Diff
Means code doesn't match reality.
- Check actual attributes
- Add missing fields
- Or `ignore_changes`

### Resource Has Different Attributes Than Documented
- Provider version differences
- API changes
- Hidden defaults

Update provider; re-check.

### Sensitive Fields
Password attribute imports as null (provider can't read).

For: set explicitly OR mark sensitive + ignore.

## Examples

### VPC
```hcl
import {
  to = aws_vpc.main
  id = "vpc-abc123"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main-vpc"
  }
}
```

### S3 Bucket
```hcl
import {
  to = aws_s3_bucket.data
  id = "my-data-bucket"
}

resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}
```

Need separate resources for versioning, encryption, etc. (modern provider).

### RDS
```hcl
import {
  to = aws_db_instance.main
  id = "my-db"
}

resource "aws_db_instance" "main" {
  identifier = "my-db"
  # many more fields ...
  
  lifecycle {
    ignore_changes = [password]   # don't have plaintext
  }
}
```

## Big Migration

Strategy for huge:
1. Inventory existing
2. Categorize (in scope, out of scope)
3. Generate config (Terraformer)
4. Refactor into modules
5. Import incrementally
6. Validate per resource
7. Tag as Terraform-managed

For 1000+ resources: weeks of work.

## Tagging

After import: tag resources:
```hcl
tags = {
  ManagedBy = "terraform"
  ImportedDate = "2024-06-09"
}
```

For: identify Terraform-managed.

## Drift After Import

Now Terraform-managed; any console change = drift.

For: enforce via:
- SCP (block console mods)
- Audit logs
- Periodic drift detection

## Anti-Patterns

- Import without writing matching code
- Import partial resources (some attrs missed)
- Big-bang import everything
- Skipping plan validation

## Best Practices

- Per-service migration
- Generate config; review
- Plan clean before commit
- Tag for tracking
- Lock down console after
- Drift detection
- Document migration

## Multi-Region Import

```hcl
provider "aws" {
  alias = "west"
  region = "us-west-2"
}

import {
  to = aws_instance.dr
  id = "i-west-123"
  provider = aws.west
}
```

## State Move After Import

```hcl
moved {
  from = aws_instance.imported_temp_name
  to = module.compute.aws_instance.web
}
```

Reorganize after import.

## Real Example

For team adopting Terraform:
1. Pick "shared services" account
2. Import VPCs, IAM, networking
3. Refactor into modules
4. Per app: gradually import
5. Lock console after migration
6. Maintain in IaC

Months of effort; long-term value.

## Quick Refs

```hcl
# Import block (modern)
import {
  to = TYPE.NAME
  id = "EXISTING_ID"
}

# Generate config
terraform plan -generate-config-out=generated.tf
```

```bash
# Imperative
terraform import TYPE.NAME ID

# Terraformer
terraformer import aws --resources=...

# State
terraform state list
terraform state show RESOURCE
```

## Interview Prep

**Mid**: "Import existing resources."

**Senior**: "Brownfield migration strategy."

**Staff**: "Adopt Terraform org-wide."

## Next Topic

→ [T02 — Recovering Lost State](T02-Lost-State.md)
