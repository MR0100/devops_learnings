# L08/C05/T03 — Versioning, Object Lock, MFA Delete

## Learning Objectives

- Enable versioning
- Use Object Lock for compliance

## Versioning

Keep all versions of objects:
```bash
aws s3api put-bucket-versioning --bucket b --versioning-configuration Status=Enabled
```

PUT same key: new version; old preserved.
DELETE: adds delete marker; old versions remain.

## Once Enabled

Cannot disable. Only Suspend (stops new versions; existing remain).

Plan before enabling.

## Listing Versions

```bash
aws s3api list-object-versions --bucket b --prefix file.txt
{
  "Versions": [
    {"Key": "file.txt", "VersionId": "abc", "IsLatest": true},
    {"Key": "file.txt", "VersionId": "def", "IsLatest": false}
  ],
  "DeleteMarkers": [...]
}
```

## Retrieving Specific Version

```bash
aws s3api get-object --bucket b --key file.txt --version-id def
```

## Restoring

To make old version current: copy it over:
```bash
aws s3 cp s3://b/file.txt s3://b/file.txt --version-id def
```

Creates new version with content of `def`.

Or delete the current (becomes a delete marker on top), revealing previous version.

## Cost

Each version: stored separately. Forgetting → bloat.

Lifecycle:
```yaml
NoncurrentVersionTransitions:
  - NoncurrentDays: 30
    StorageClass: GLACIER_IR
NoncurrentVersionExpiration:
  NoncurrentDays: 365
ExpiredObjectDeleteMarker: true
```

Move old versions cheap; delete after retention.

## Use Cases

- Ransomware protection (versions survive ransomware delete)
- Accidental delete recovery
- Audit (immutable historical record)
- App with editing (revisions)

## Versioning + Replication

CRR/SRR copies versions:
- New version in source → new version in target
- Delete marker in source → delete marker in target (if configured)

For backup: replicate versions; protect target with separate access.

## MFA Delete

For high-stakes buckets: require MFA to permanently delete version or change versioning state.

```bash
aws s3api put-bucket-versioning --bucket b \
  --versioning-configuration Status=Enabled,MFADelete=Enabled \
  --mfa "arn:aws:iam::123:mfa/alice 123456"
```

Once enabled: ALL delete-version ops need MFA. Painful but secure.

Only root can configure MFA delete.

## Object Lock (WORM)

Write-Once-Read-Many. For compliance:
- SOX, HIPAA, FINRA
- Cannot delete or overwrite

Two modes:
- **Governance**: some users (with permission) can override
- **Compliance**: NO ONE can delete, including root

Plus:
- Retention until date
- Legal hold

## Enable Object Lock

Must be enabled at bucket creation:
```bash
aws s3api create-bucket --bucket b --object-lock-enabled-for-bucket
```

Versioning automatically on.

## Setting Retention

Per object:
```bash
aws s3api put-object-retention --bucket b --key file --retention 'Mode=COMPLIANCE,RetainUntilDate=2026-12-31T00:00:00Z'
```

Default bucket retention:
```bash
aws s3api put-object-lock-configuration --bucket b --object-lock-configuration '{
  "ObjectLockEnabled": "Enabled",
  "Rule": {
    "DefaultRetention": {
      "Mode": "COMPLIANCE",
      "Years": 7
    }
  }
}'
```

All new objects: 7-year compliance lock.

## Legal Hold

Indefinite hold; override retention until removed:
```bash
aws s3api put-object-legal-hold --bucket b --key file --legal-hold 'Status=ON'
```

Use: pending lawsuit.

## Compliance vs Governance

Governance:
- User with `s3:BypassGovernanceRetention` can delete
- Useful for accidental over-protection

Compliance:
- NO ONE can delete
- Even root
- Period must elapse
- For strictest

Choose carefully; you can't reduce later.

## Lifecycle vs Object Lock

Object Lock prevents:
- Delete
- Overwrite

Lifecycle still works:
- Transition (move class)
- But Expire blocked until lock expires

## Backup Strategy

For DR / ransomware:
1. Versioning enabled
2. Cross-account replication (separate access)
3. Object Lock on backup bucket
4. MFA delete on backup
5. Tested restore quarterly

Defense in depth against malicious deletes.

## Common Mistakes

- Versioning without lifecycle (bloat)
- MFA delete on shared bucket (broken workflows)
- Object Lock Compliance too aggressive (stuck with bad data)
- Lifecycle expiration assumed but lock prevents

## Anti-Ransomware

Patterns:
- Versioning + Object Lock on critical
- Cross-account backup
- Separate IAM roles for backup
- MFA delete

Attacker compromises one account; backup separate.

## Object Lock Cost

Same storage cost. No extra fee for lock metadata.

Compliance bucket cleanup: cannot until expiration. Plan retention.

## ETag and Versioning

ETag per version. After overwrite, new version, new ETag.

Use for cache invalidation: ETag changes = content changed.

## Versioning vs Backup

Versioning ≠ backup. Versions in same bucket; bucket-level disaster still loses data.

Backup = replicate to separate (account, region, provider).

## Pre-Signed URLs

Pre-signed URLs respect versioning:
```bash
aws s3 presign s3://b/file.txt --version-id abc
```

URL for specific version.

## Audit

CloudTrail data events: log object operations (per object). Optional; expensive.

Object-level events: PutObject, GetObject, DeleteObject visible.

## Common Operations

```bash
# Enable versioning
aws s3api put-bucket-versioning --bucket b --versioning-configuration Status=Enabled

# List versions
aws s3api list-object-versions --bucket b --prefix file

# Get specific
aws s3api get-object --bucket b --key file --version-id xyz file.bak

# Delete version permanently (with auth)
aws s3api delete-object --bucket b --key file --version-id xyz

# Disable delete marker (un-delete latest)
aws s3api delete-object --bucket b --key file --version-id <delete-marker-id>
```

## Best Practices

- Versioning on critical buckets
- Lifecycle for noncurrent versions
- Object Lock on compliance-sensitive
- MFA delete on tier-0
- Cross-account replication for backup
- Test restore process

## Object Lock + Cross-Region Replication

Source bucket Object Lock → target bucket inherits if configured.

Replicate locks to DR bucket.

## Interview Prep

**Mid**: "Versioning use cases."

**Senior**: "Anti-ransomware S3."

**Staff**: "Compliance Object Lock for SOX."

## Next Topic

→ [T04 — S3 Performance & Request Patterns](T04-Performance.md)
