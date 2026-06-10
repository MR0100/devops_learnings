# L10/C09/T02 — Recovering Lost State

## Learning Objectives

- Recover from lost state
- Prevent in future

## State Loss Scenarios

- State file deleted
- S3 bucket deleted (no versioning)
- Local state on lost machine
- Corruption (rare)

Without state: Terraform doesn't know about resources.

## Prevention

Before recovery: prevent.

### S3 Versioning
```hcl
resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

All state changes versioned. Restore from prior version.

### Backup
```bash
terraform state pull > backup-$(date +%s).tfstate
```

Manual backup before risky ops.

### MFA Delete
```bash
aws s3api put-bucket-versioning --bucket tfstate \
  --versioning-configuration Status=Enabled,MFADelete=Enabled \
  --mfa "arn:aws:iam::...:mfa/user 123456"
```

Prevents accidental delete.

### Cross-Region Replication
```hcl
resource "aws_s3_bucket_replication_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  
  rule {
    id = "replicate-to-west"
    destination {
      bucket = aws_s3_bucket.tfstate_replica.arn
    }
  }
}
```

For: regional disaster.

## Recovery Steps

### Option 1: Restore From Backup
```bash
aws s3 cp s3://backups/state-backup.tfstate ./terraform.tfstate
terraform state pull > /dev/null   # verify
terraform plan   # should show no changes if accurate
```

### Option 2: Restore S3 Version
```bash
# List versions
aws s3api list-object-versions --bucket tfstate --prefix prod/

# Restore specific
aws s3api copy-object \
  --bucket tfstate \
  --copy-source "tfstate/prod/terraform.tfstate?versionId=VERSION_ID" \
  --key prod/terraform.tfstate
```

### Option 3: Rebuild State

For completely lost state with resources still alive:
1. List existing cloud resources
2. Write Terraform code matching
3. Import each
4. Verify

Effort: hours-days depending on size.

Like brownfield import (T01).

## Rebuild Process

```bash
# For each resource type
aws ec2 describe-instances
aws s3 ls
aws rds describe-db-instances
# ... etc

# Generate import blocks
cat > imports.tf <<EOF
import { to = aws_instance.web; id = "i-abc" }
import { to = aws_s3_bucket.data; id = "my-data" }
# ...
EOF

# Generate config
terraform plan -generate-config-out=generated.tf

# Review + clean up
# Apply
terraform apply
```

## Lost State Implications

- Terraform thinks nothing exists
- Plan would create everything (DOUBLE)
- DON'T apply without import
- Risk of duplicate resources

For: stop; recover; verify; apply.

## Symptoms

```bash
terraform plan
# Plan: 47 to add, 0 to change, 0 to destroy.
# (When you know resources exist)
```

→ State lost.

## Verify Resources Exist

Before assuming worst:
```bash
aws ec2 describe-instances --instance-ids i-xxx
```

If exist + Terraform plans add: state issue.

## Force State Override

```bash
# Pull from S3 latest version
terraform state pull > current.tfstate

# Or manually
aws s3 cp s3://tfstate/prod/terraform.tfstate ./terraform.tfstate
terraform state push terraform.tfstate
```

## Lock Stuck

Sometimes lock state stuck:
```bash
terraform force-unlock LOCK_ID
```

Use ONLY if confident no apply running.

## Backup Procedure

Before risky:
```bash
# 1. Backup
terraform state pull > backup-pre-change.tfstate

# 2. Do risky thing
terraform state mv ...

# 3. If wrong, restore
terraform state push backup-pre-change.tfstate
```

Always backup state before surgery.

## State in Multiple Backends

Migrating backends:
```bash
# Old backend
terraform init   # connects to old
terraform state pull > state.json

# Change backend config
terraform init -migrate-state
```

Terraform helps migrate.

## TFC State

Terraform Cloud: built-in versioning + backups.

For: less manual.

## Best Practices

- S3 versioning enabled
- MFA delete on critical
- Cross-region replication
- Periodic backups
- Test recovery
- Document procedure

## State Corruption

Rare; symptoms:
- Plan fails parsing
- terraform validate fails

Recovery:
- Restore from backup
- Manual edit (dangerous; pull, edit JSON, push)

## DynamoDB Lock Lost

For S3 backend:
- DynamoDB locks
- If lost: just need to restart lock mechanism

Locks are short-lived; not critical to backup.

## Real Incident

Hypothetical:
- Engineer deletes S3 bucket (mistake)
- State gone (no replica)
- 50 resources in AWS, no IaC
- Recovery: 2 days of import + rebuild
- Production didn't drift (luckily)

Don't be this engineer.

## Prevention Checklist

- ☐ S3 versioning on state bucket
- ☐ MFA delete enabled
- ☐ Cross-region replication
- ☐ Bucket policy preventing delete
- ☐ Multiple admins for access
- ☐ Periodic state backup
- ☐ Procedure documented
- ☐ Recovery tested

## Multiple Engineer Risk

Two engineers apply simultaneously without DynamoDB lock → state corruption.

Always use lock:
```hcl
backend "s3" {
  bucket         = "tfstate"
  key            = "prod.tfstate"
  dynamodb_table = "tflock"
}
```

## State Splitting

For risk reduction:
- Per-workload state
- One workload state lost → only that workload affected
- vs single huge state for everything

## Recovery Drill

Annually:
1. Take prod state backup
2. Restore to test environment
3. Verify
4. Document timing

Without drill: assume recovery doesn't work.

## Quick Refs

```bash
# Versioning S3
aws s3api put-bucket-versioning --bucket NAME --versioning-configuration Status=Enabled

# List versions
aws s3api list-object-versions --bucket tfstate --prefix prod/

# Restore version
aws s3api copy-object --bucket tfstate \
  --copy-source "tfstate/prod/state?versionId=ID" \
  --key prod/state

# Pull current state
terraform state pull > backup.tfstate

# Push state
terraform state push backup.tfstate

# Force unlock
terraform force-unlock LOCK_ID
```

## Interview Prep

**Mid**: "State backup."

**Senior**: "Recover lost state."

**Staff**: "DR for Terraform state."

## Next Topic

→ [T03 — The "Big Refactor" Without Downtime](T03-Big-Refactor.md)
