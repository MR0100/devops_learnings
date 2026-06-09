# L10/C09 — Disasters & Recovery

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Importing-Brownfield.md) | Importing Brownfield Infrastructure | 1 hr |
| [T02](T02-Lost-State.md) | Recovering Lost State | 0.5 hr |
| [T03](T03-Big-Refactor.md) | The "Big Refactor" Without Downtime | 1 hr |

## Brownfield Import

Bringing existing cloud resources under Terraform.

### Strategy
1. Write the resource block(s) describing what exists
2. Import to state
3. Run `terraform plan` — should show no changes (or only what you want changed)
4. Refine the block until plan is empty
5. Commit

### Old way (CLI)
```bash
terraform import aws_instance.web i-abc123
```

### Modern (1.5+) — Import Blocks
```hcl
import {
  to = aws_instance.web
  id = "i-abc123"
}

resource "aws_instance" "web" {
  # ... attributes ...
}
```

Then:
```bash
terraform plan -generate-config-out=generated.tf
terraform apply
```

Terraform generates a starter resource block; you refine.

### Bulk Import Tools
- **terraformer** (Google) — generate TF + state from existing cloud
- **terracognita** — similar
- **driftctl** — detect unmanaged resources

### Patterns for Large Imports
- Import in small batches
- One module/dir at a time
- Verify plan is clean before next batch
- Document import in commit messages

### Common Issues
- Resource has properties not exposed in API (computed by cloud)
- Sensitive data in state after import
- Resource depends on other resources not yet imported
- Naming convention misalignment

## Recovering Lost State

### From Versioning
S3 backend with versioning enabled:
```bash
aws s3api list-object-versions --bucket my-tf-state --prefix prod/network/
aws s3api get-object --bucket my-tf-state --key prod/network/terraform.tfstate --version-id <ID> recovered.tfstate
```

### From TFC History
Terraform Cloud retains state history per workspace; restore via UI.

### Worst Case: Rebuild State by Import
- Slow, painful
- For each resource, run terraform import
- Or use terraformer to scrape entire account

## "Big Refactor" Without Downtime

Refactoring TF code shouldn't recreate resources. Use `terraform state mv` and `moved` blocks.

### Example: Move Resource into a Module

Before:
```hcl
resource "aws_s3_bucket" "data" { ... }
```

After:
```hcl
module "data_storage" {
  source = "./modules/storage"
  bucket_name = "..."
}
# inside module: resource "aws_s3_bucket" "this" { ... }
```

Without help, Terraform would destroy old + create new.

### Solution 1: `terraform state mv` (old way)
```bash
terraform state mv aws_s3_bucket.data module.data_storage.aws_s3_bucket.this
```

### Solution 2: `moved` blocks (1.1+)
```hcl
moved {
  from = aws_s3_bucket.data
  to   = module.data_storage.aws_s3_bucket.this
}
```

Now `terraform plan` shows the move; apply is a no-op.

### Rename a Resource
```hcl
moved {
  from = aws_s3_bucket.data_v1
  to   = aws_s3_bucket.data
}
```

### Split into Multiple States

1. Add `removed` block (1.7+) in source root:
```hcl
removed {
  from = aws_s3_bucket.data
  lifecycle { destroy = false }
}
```

2. In destination root, `import` block to bring it in:
```hcl
import {
  to = aws_s3_bucket.data
  id = "actual-bucket-name"
}
```

3. Apply both.

## Resource Replacement Without Recreating Dependent Resources

Sometimes you want to recreate a resource (e.g., AMI changed) without disrupting dependents.

```hcl
resource "aws_instance" "web" {
  ami = data.aws_ami.latest.id
  lifecycle {
    create_before_destroy = true
  }
}
```

Now new instance is created first; old destroyed after.

### Replace Triggered By
```hcl
resource "aws_instance" "web" {
  ami = ...
  lifecycle {
    replace_triggered_by = [aws_security_group.app.id]
  }
}
```

When SG changes, instance is replaced. Use rarely.

## Production-Safe Apply

```bash
# Always plan first
terraform plan -out=plan.tfplan

# Review the plan output
# Look for:
#  - Unexpected destroys
#  - Anything with prevent_destroy
#  - Lost resources

# Apply the saved plan (so nothing else can change between)
terraform apply plan.tfplan
```

## Disaster Recovery Drills

- Test "delete a stack and rebuild from code" quarterly in staging
- Verify outputs match expected
- Time it (RTO measurement)
- Document gaps

## Interview Themes

- "How do you import existing infra?"
- "State lost — recovery steps?"
- "Move a resource between modules without recreating"
- "moved vs removed vs import blocks"
- "Big refactor without downtime — strategy?"
