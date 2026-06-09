# L10/C03/T04 — terraform state Commands (mv, rm, import, replace)

## Learning Objectives

- Perform state surgery
- Refactor safely

## Commands

```bash
terraform state list
terraform state show <address>
terraform state mv <src> <dst>
terraform state rm <address>
terraform state pull > file.tfstate
terraform state push file.tfstate
terraform state replace-provider <from> <to>
terraform import <address> <id>
terraform apply -replace=<address>
```

## list

All managed:
```bash
terraform state list
# aws_vpc.main
# aws_subnet.public[0]
# aws_subnet.public[1]
# module.eks.aws_eks_cluster.this
# ...
```

Filter:
```bash
terraform state list | grep eks
```

## show

Specific resource:
```bash
terraform state show aws_instance.web
# id           = "i-0abc..."
# ami          = "ami-..."
# instance_type = "t3.micro"
# ...
```

For inspection.

## mv (Rename / Refactor)

Renamed in code:
```hcl
# Old: aws_instance.old_name
# New: aws_instance.web
```

```bash
terraform state mv aws_instance.old_name aws_instance.web
```

Else Terraform: delete old + create new (downtime).

## mv into Module

```bash
terraform state mv aws_instance.web module.compute.aws_instance.web
```

Refactoring into module without recreate.

## mv from Module to Root

```bash
terraform state mv module.compute.aws_instance.web aws_instance.web
```

## mv for_each Key Change

```hcl
# Old: for_each = { web = "..." }
# New: for_each = { app = "..." }
```

```bash
terraform state mv 'aws_instance.x["web"]' 'aws_instance.x["app"]'
```

## rm (Remove from State)

```bash
terraform state rm aws_instance.web
```

Removes from state; real resource NOT destroyed.

Use cases:
- Moved to manual / other tool
- Resource will be re-imported under new name
- Erroneous in state (rare)

After: `terraform plan` shows it as new (if still in code).

## import

Existing resource not in state:
```bash
terraform import aws_instance.web i-0abc123
```

Adds to state. Code block must exist.

Doesn't generate config (you write).

For complex: see if `import` block (1.5+) works.

## import block (Modern)

```hcl
import {
  to = aws_instance.web
  id = "i-0abc123"
}
```

```bash
terraform plan       # shows what'll be imported
terraform apply      # imports
```

Adds to state during apply.

Also generates config (with `-generate-config-out`):
```bash
terraform plan -generate-config-out=generated.tf
```

For mass migration.

## replace (modern taint)

Force resource replacement:
```bash
terraform apply -replace=aws_instance.web
```

Equivalent to deprecated `terraform taint`.

For: refresh a resource (re-running provisioner; fixing issue).

## pull / push

```bash
terraform state pull > current.tfstate
# Edit (DANGEROUS)
terraform state push current.tfstate
```

For: emergency surgery, recovery.

Backup first. Test on copy.

## replace-provider

Change provider:
```bash
terraform state replace-provider hashicorp/aws registry.terraform.io/hashicorp/aws
```

For provider source change.

## Refactoring Workflow

For module extraction:

1. Create module dir with resources moved.
2. In root: `module "x" {}` block.
3. State move:
   ```bash
   terraform state mv aws_instance.web module.x.aws_instance.web
   ```
4. `terraform plan` → no changes.
5. Commit.

## Refactoring count → for_each

```hcl
# Old: count = 3
# New: for_each = { web = ..., db = ..., api = ... }
```

```bash
terraform state mv 'aws_instance.x[0]' 'aws_instance.x["web"]'
terraform state mv 'aws_instance.x[1]' 'aws_instance.x["db"]'
terraform state mv 'aws_instance.x[2]' 'aws_instance.x["api"]'
```

## Moved Block (Modern)

```hcl
moved {
  from = aws_instance.old_name
  to   = aws_instance.web
}
```

Apply: Terraform records move; no manual `state mv` needed.

For multi-engineer: source of truth.

Module re-org:
```hcl
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

## Removed Block (1.7+)

```hcl
removed {
  from = aws_instance.web
  lifecycle {
    destroy = false
  }
}
```

Removes from state without destroy. Code-driven version of `terraform state rm`.

## Refresh

```bash
terraform refresh
# or
terraform plan -refresh-only
terraform apply -refresh-only
```

Re-reads cloud state; updates Terraform state. Useful for drift sync.

## Backup Strategy

Before risky surgery:
```bash
terraform state pull > backup-$(date +%s).tfstate
```

Restore (rare):
```bash
terraform state push backup-1234.tfstate
```

## State Inspection

`terraform state show resource.name` for details.

To check if resource managed:
```bash
terraform state list | grep -q aws_instance.web && echo managed || echo not-managed
```

## Common Scenarios

### Resource Deleted in Console
- AWS resource gone
- Terraform state thinks it exists
- Plan: delete from state OR re-create

Choose:
- `terraform state rm` + remove from code
- Or apply (Terraform creates new)

### Resource Created Manually
- AWS resource exists
- Terraform state doesn't know
- Code mismatch: plan would create duplicate

Solution:
- Write code matching
- `terraform import`

### Two Resources Conflict
- Created via Terraform
- Created via console (same key)
- Terraform tries create; AWS errors duplicate

Solution: import the duplicate; remove or merge.

### Module Reorganization
Moving resources between modules:
- `moved` block; or `terraform state mv`

### Workspace Migration
Apply same code in new workspace:
```bash
terraform workspace new prod
terraform import ...    # for each existing
```

Or migrate state file.

## State Versioning

S3 backend versioned: every change new version. Recoverable.

## Risk Levels

| Operation | Risk |
|---|---|
| list | Safe |
| show | Safe |
| mv | Low (with backup) |
| rm | Medium |
| import | Low |
| pull/push | High |
| replace | Low |
| force-unlock | High (if applies running) |

Always backup before high-risk.

## Common Mistakes

- `state rm` then forget code (becomes orphan)
- `state mv` with typo (corruption)
- No backup
- Pushing edited state with typos
- import with wrong ID
- Forgetting code matches imported resource

## Best Practices

- Backup before surgery
- Test in sandbox
- `terraform plan` after each step
- `moved` block over `state mv` (code source of truth)
- `import` block over CLI import
- Document complex refactors

## Quick Refs

```bash
# Inspect
terraform state list
terraform state show <addr>

# Refactor
terraform state mv <src> <dst>

# Import
terraform import <addr> <id>
# Or in code:
# import { to = ... id = "..." }

# Remove
terraform state rm <addr>

# Replace
terraform apply -replace=<addr>

# Backup
terraform state pull > backup.tfstate
```

## Interview Prep

**Mid**: "state mv use case."

**Senior**: "Refactor into module without recreate."

**Staff**: "Import 1000 resources."

## Next Topic

→ [T05 — State Drift Detection](T05-State-Drift.md)
