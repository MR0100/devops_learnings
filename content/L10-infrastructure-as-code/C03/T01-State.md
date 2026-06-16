# L10/C03/T01 — What State Is & Why It Matters

## Learning Objectives

- Understand state purpose
- Manage state properly

## State

Terraform's record of what it manages. JSON file: `terraform.tfstate`.

Maps:
- Code → real-world resource
- Tracks attributes, dependencies, IDs

Without state: Terraform doesn't know what exists.

## Example

After `terraform apply`:
```json
{
  "version": 4,
  "resources": [
    {
      "type": "aws_instance",
      "name": "web",
      "instances": [{
        "attributes": {
          "id": "i-0abc123",
          "ami": "ami-xxx",
          "instance_type": "t3.micro",
          "private_ip": "10.0.1.5"
        }
      }]
    }
  ]
}
```

`aws_instance.web` → `i-0abc123`.

## Why State

### Map Code to Real Resources
Code: `aws_instance.web`. AWS: `i-0abc123`. State tracks.

### Performance
Without state: Terraform would query every resource every plan. Slow.
With state: cached.

### Metadata
Dependencies, providers, etc.

### Sensitive
Includes resource details that might be sensitive (IPs, ARNs).

## Operations

```bash
terraform state list                  # all resources
terraform state show aws_instance.web # specific
terraform state mv X Y                # rename
terraform state rm X                  # remove from state (not destroy)
terraform state pull                  # fetch state (raw)
terraform state push                  # push (rare)
```

## Local State

Default: `terraform.tfstate` in working dir.

Problems:
- Solo only (no team)
- Lost if machine dies
- No locking
- No encryption
- Not versioned

For anything beyond personal: use remote state.

## Remote State

Stored in shared backend:
- S3 + DynamoDB (most common)
- Terraform Cloud / HCP Terraform
- Azure Storage
- GCS
- Consul
- HTTP backend (custom)

Benefits:
- Team access
- Locking (no concurrent applies)
- History (versioning)
- Encryption
- Audit

## Sensitive in State

State contains:
- Resource attributes
- Sometimes secrets (DB passwords, API keys you set)

Protect:
- Encrypt at rest (KMS in S3 backend)
- Limit access (IAM)
- Don't commit (.gitignore)

Even random_password values in state.

## Locking

Prevents concurrent applies:
- DynamoDB for S3 backend
- TFC built-in
- Consul KV

Without locking: two engineers apply at same time → corrupt state.

```hcl
terraform {
  backend "s3" {
    bucket         = "my-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tflock"
    encrypt        = true
  }
}
```

## State Versioning

S3 backend with versioning enabled:
- Every state change = new version
- Restore on corruption

For other backends: their own versioning.

## State Drift

Resources changed outside Terraform:
- Manual console mod
- Other tool
- AWS-side change

Detected:
```bash
terraform plan
# Resource "aws_instance.web" modified outside Terraform
```

`refresh` updates state with current reality:
```bash
terraform plan -refresh-only
terraform apply -refresh-only
```

For: sync state to actual without modifying config.

## State Migration

Move between backends:
1. Update terraform block (new backend)
2. `terraform init -migrate-state`
3. Confirm; old state copied to new

For: switching from local to S3, S3 to TFC, etc.

## State Surgery (state mv)

Refactor without destroying:

Renamed resource:
```bash
# Code change: aws_instance.old → aws_instance.web
terraform state mv aws_instance.old aws_instance.web
```

Else Terraform thinks delete old + create new.

Module migration:
```bash
terraform state mv aws_instance.x module.compute.aws_instance.x
```

When moving into module.

## State rm

Remove from state (don't destroy):
```bash
terraform state rm aws_instance.web
```

For:
- Resource moved to manual / other tool
- Importing under different name later
- Mistakes (rare; carefully)

Real resource untouched.

## State pull / push

```bash
terraform state pull > current.json
# Manually edit (dangerous)
terraform state push current.json
```

For: emergency surgery; recovery.

Use sparingly; backup first.

## Backup

S3 with versioning: automatic.

Local state: backup `terraform.tfstate.backup` per apply. But machine fails: lost.

## State Format

Version field in state; Terraform handles migration on read.

Don't edit raw JSON manually unless emergency.

## Import

For resources created outside Terraform:
```bash
terraform import aws_instance.web i-0abc123
```

Adds to state. You must already have code block.

For complex bulk: `import` block (1.5+):
```hcl
import {
  to = aws_instance.web
  id = "i-0abc123"
}
```

Apply: imports.

## Multi-Workspace State

Workspaces: separate state per workspace.

State file: `terraform.tfstate.d/<workspace>/terraform.tfstate`.

For env separation without separate dirs.

## When State Goes Wrong

Symptoms:
- `terraform plan` shows nothing changed; AWS sees nothing
- Or shows everything as new; AWS already has
- Lock won't release
- Corrupt JSON

Solutions:
- Check backend
- Restore from version
- State refresh
- State surgery

Backup first.

## State Visualization

```bash
terraform state list
terraform graph | dot -Tsvg > graph.svg   # dependency graph
```

For understanding.

## Working with State

Treat state as precious:
- Backups
- Locking
- Versioning
- Access control
- Encryption

Loss / corruption = manual rebuild from scratch.

## Best Practices

- Remote backend (S3 + DynamoDB)
- Versioning enabled
- Encryption (KMS)
- IAM restrictive
- Audit access (CloudTrail)
- One state per workload (not 1 huge)
- Separate states per env (prod/staging/dev)

## Multiple State Files

Larger orgs: split:
- vpc.tfstate
- eks.tfstate
- app.tfstate

Use `terraform_remote_state` data source to reference outputs across.

## Common Mistakes

- Local state for team (chaos)
- No locking
- State committed to Git
- Same state for many envs
- Manual JSON edit
- No backup before surgery

## Comparison: Why Not CFN?

CloudFormation: state managed by AWS automatically.
Terraform: state managed by you.

Pros / cons:
- TF: any provider; complex state visible
- CFN: AWS-managed but only AWS

For multi-cloud: TF.

## Quick Refs

```bash
terraform state list
terraform state show aws_instance.web
terraform state mv aws_instance.old aws_instance.new
terraform state rm aws_instance.x
terraform state pull > backup.tfstate
terraform import aws_instance.x i-xxx
terraform plan -refresh-only
```

## Interview Prep

**Mid**: "What state does."

**Senior**: "Split state vs one big."

**Staff**: "State recovery from corruption."

## Next Topic

→ [T02 — Backends](T02-Backends.md)
