# L26/C04/T03 — Snapshot Cleanup

## Learning Objectives

- Clean up old snapshots
- Save storage cost

## Snapshots

- EBS
- RDS
- DynamoDB
- Others

Each: incremental.
Accumulates.

## Cost

EBS snapshot: $0.05/GB/month.

For 100 TB snapshots: $5000/mo.

For: significant.

## Audit

```bash
aws ec2 describe-snapshots --owner-ids self
```

Find:
- Orphaned (volume deleted)
- Old (no longer needed)
- AMI-referenced (don't delete)

## Lifecycle

### EBS via Data Lifecycle Manager (DLM)

```bash
aws dlm create-lifecycle-policy ...
```

Retention rules:
- Keep last 7 daily
- Keep last 4 weekly
- Keep last 12 monthly

For: auto retention.

### Manual

```bash
aws ec2 delete-snapshot --snapshot-id snap-xyz
```

Verify not referenced:
- AMI
- Pending share

## RDS Snapshots

```bash
aws rds describe-db-snapshots
aws rds delete-db-snapshot --db-snapshot-identifier snap-xyz
```

Auto-snapshots: by retention.
Manual: deleted explicitly.

## Cross-Region Copies

For DR:
- Cross-region snapshot copies
- Extra cost
- Keep policy

## Tags

Tag snapshots:
- Created-by
- Service
- Env

For: attribution + selective cleanup.

## Audit Script

```python
import boto3

ec2 = boto3.client('ec2')
old = []
for snap in ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']:
    age = (now - snap['StartTime']).days
    if age > 30:
        old.append(snap['SnapshotId'])

print(f"Old snapshots: {len(old)}")
```

For: cleanup candidates.

## Best Practices

- DLM for automated
- Tag everything
- Quarterly audit
- Cross-region only if needed
- Verify before delete

## Common Mistakes

- No lifecycle (accumulate forever)
- Delete AMI's snapshot (AMI broken)
- No DR snapshots (no backup)

## Quick Refs

```bash
# Find
aws ec2 describe-snapshots --owner-ids self

# Delete
aws ec2 delete-snapshot --snapshot-id X

# DLM
aws dlm create-lifecycle-policy
```

## Interview Prep

**Mid**: "Snapshot management."

**Senior**: "Cost optimization."

## Next Topic

→ Move to [L26/C05 — Networking Cost Traps](../C05/README.md)
