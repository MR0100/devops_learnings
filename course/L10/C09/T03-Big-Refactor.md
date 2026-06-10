# L10/C09/T03 — The "Big Refactor" Without Downtime

## Learning Objectives

- Refactor large Terraform safely
- Use moved blocks

## Common Refactors

- Extract module from inline
- Reorganize resources between modules
- Rename resources
- Split monolith into smaller states
- Restructure repo

Risk: destroy + create = downtime + data loss.

## Tools

### moved Block
```hcl
moved {
  from = aws_instance.web
  to   = aws_instance.web_new
}
```

Terraform records: same resource, new name.

No destroy/create.

### removed Block (1.7+)
```hcl
removed {
  from = aws_instance.deleted
  lifecycle {
    destroy = false
  }
}
```

Remove from state without destroying.

For: hand off to another module / state.

### State Operations
```bash
terraform state mv X Y
terraform state rm X
```

Manual; pre-moved-block era.

## Rename Resource

```hcl
# Old
resource "aws_instance" "web" {...}

# New
resource "aws_instance" "web_server" {...}

moved {
  from = aws_instance.web
  to   = aws_instance.web_server
}
```

Apply: rename in state; no actual change.

## Move into Module

```hcl
# Before
resource "aws_vpc" "main" {...}

# After
module "network" {
  source = "./modules/network"
}

moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}
```

Apply: moves to module path; no recreate.

## Move Between Modules

```hcl
moved {
  from = module.old.aws_instance.web
  to   = module.new.aws_instance.web
}
```

## Move Across States (Cross-State)

Can't use moved block.

Use:
```bash
# Source state
terraform state pull > source.tfstate
terraform state rm aws_instance.web

# Target state
terraform state pull > target.tfstate
# Manually edit or:
terraform state push target.tfstate

terraform import aws_instance.web INSTANCE_ID
```

Or: remove from source, import into target.

Risky; backup states.

## Convert to for_each

```hcl
# Before
resource "aws_instance" "web_1" {...}
resource "aws_instance" "web_2" {...}
resource "aws_instance" "web_3" {...}

# After
resource "aws_instance" "web" {
  for_each = toset(["web_1", "web_2", "web_3"])
  ...
}

moved {
  from = aws_instance.web_1
  to   = aws_instance.web["web_1"]
}
moved {
  from = aws_instance.web_2
  to   = aws_instance.web["web_2"]
}
moved {
  from = aws_instance.web_3
  to   = aws_instance.web["web_3"]
}
```

## Split State

For huge state → smaller:
1. Identify boundaries
2. Create new state file (new dir)
3. Move resources via state operations
4. Verify

```bash
# In source dir
terraform state mv aws_vpc.main module.network.aws_vpc.main
terraform state pull > backup-1.tfstate

# Remove from source
terraform state rm aws_vpc.main

# Push to target backend
# (manually edit + push, or use migration tooling)
```

## Split Tool

```bash
# Custom: write script
terraform state list | grep '^module.network' | while read addr; do
  terraform state mv "$addr" "<target-backend>.$addr"
done
```

Complex; test extensively.

## Big Refactor Process

1. Plan changes
2. Backup state
3. Add `moved` blocks
4. Plan — should show 0 destroys, 0 creates
5. Apply
6. Verify resources untouched
7. Remove `moved` blocks (cleanup)
8. Commit

For each step: incremental.

## Verify No Changes

```bash
terraform plan
# Plan: 0 to add, 0 to change, 0 to destroy.
```

Critical. If shows destroy/create: moved wrong; fix.

## Test in Non-Prod

For prod refactor:
- Apply in dev first
- Verify
- Then staging
- Then prod

Same patterns; build confidence.

## Lifecycle: prevent_destroy

```hcl
resource "aws_db_instance" "main" {
  lifecycle {
    prevent_destroy = true
  }
}
```

Refactor mistake: try to destroy → error. Saves data.

For: critical resources during refactor.

## Documentation

Per refactor:
- Why
- What changes
- Validation steps
- Rollback plan

For: team understanding + audit.

## Common Mistakes

- No `moved` block (destroys + recreates)
- moved wrong path (no effect)
- No state backup
- Big-bang refactor (too much)
- No staging test

## Best Practices

- Incremental refactor
- moved blocks for in-state
- Backup before
- Plan must be 0/0/0 after moved
- Test in non-prod
- prevent_destroy on critical
- Document changes

## Multi-Stage Refactor

For huge change:
1. Add moved blocks
2. Apply (no-op for resources)
3. Refactor code
4. Apply (real changes)
5. Cleanup moved blocks

Phased; safer.

## State Refactor + Provider Changes

Sometimes both:
- Provider upgrade (AWS 4 → 5)
- Refactor resources

Do separately:
1. Upgrade provider
2. Verify
3. Refactor
4. Verify

Not simultaneously.

## Common Refactor: Extract Module

Before:
```hcl
resource "aws_vpc" "main" {...}
resource "aws_subnet" "public" {count = 3; ...}
resource "aws_subnet" "private" {count = 3; ...}
# ... + IGW, NAT, route tables ...
```

After:
```hcl
module "vpc" {
  source = "./modules/vpc"
  cidr   = "10.0.0.0/16"
  azs    = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

moved {
  from = aws_vpc.main
  to   = module.vpc.aws_vpc.main
}

moved {
  from = aws_subnet.public[0]
  to   = module.vpc.aws_subnet.public[0]
}

# ... many moved blocks ...
```

Plan should be: 0 destroy, 0 create.

## Generate moved

For many resources:
```bash
# Script
for addr in $(terraform state list); do
  echo "moved {"
  echo "  from = $addr"
  echo "  to   = module.X.$addr"
  echo "}"
done
```

Adjust paths; review.

## In-Place Refactor

For rename:
```hcl
moved {
  from = aws_s3_bucket.data
  to   = aws_s3_bucket.application_data
}
```

Same dir; same state.

## Cross-State Refactor

Moving to different state file:
1. Backup both states
2. Remove from source
3. Import into target

Or use Terraform Cloud's API.

Risky; test extensively.

## Rollback

If something goes wrong:
1. Stop
2. Restore state from backup
3. Identify issue
4. Plan fix
5. Re-try carefully

For: prevention > recovery.

## Tooling

For huge refactors:
- terraform-state-mv-helper
- Custom scripts
- Terraform Cloud API

For most: native moved blocks suffice.

## Production Refactor

1. Plan thoroughly
2. Schedule maintenance window (just in case)
3. Backup state
4. Backup data
5. Apply with monitoring
6. Verify
7. Lock down for stabilization

Even with moved blocks: cautious.

## Quick Refs

```hcl
moved {
  from = OLD_ADDRESS
  to   = NEW_ADDRESS
}

removed {
  from = OLD_ADDRESS
  lifecycle {
    destroy = false
  }
}
```

```bash
# State ops
terraform state mv X Y
terraform state rm X
terraform state pull > backup.tfstate
terraform state push backup.tfstate
```

## Interview Prep

**Mid**: "Rename Terraform resource."

**Senior**: "Extract module without recreate."

**Staff**: "Big refactor with downtime tolerance."

## Next Topic

→ Move to [L11 — Configuration Management](../../L11/README.md)
