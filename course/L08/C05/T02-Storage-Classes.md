# L08/C05/T02 — Storage Classes & Lifecycle Policies

## Learning Objectives

- Pick storage class
- Automate transitions

## Storage Classes

| Class | Min Storage | Retrieval | $/GB/mo* | Use |
|---|---|---|---|---|
| Standard | 0 | instant | $0.023 | hot |
| Standard-IA | 30 days | instant | $0.0125 | infrequent |
| One Zone-IA | 30 days | instant | $0.01 | non-critical IA |
| Intelligent-Tiering | 0 | instant | base + small fee | unpredictable |
| Glacier Instant Retrieval | 90 days | ms | $0.004 | archive, rare access |
| Glacier Flexible | 90 days | min-hrs | $0.0036 | archive |
| Glacier Deep Archive | 180 days | 12+ hrs | $0.00099 | rarely-accessed cold |

*US-East-1 prices; approximate.

## Standard

Default. 11 9s durability; 99.99% availability. Replicates across 3+ AZs.

Use for: anything frequently accessed.

## Standard-IA

Lower cost; retrieval fee per GB.
- $0.01/GB retrieval
- Min 30-day storage (charged 30 days even if deleted earlier)
- Min 128 KB object (smaller charged as 128 KB)

Use: logs >30 days; backups recent.

## One Zone-IA

Like IA but one AZ. Cheaper; less durable (loses if AZ destroyed).

Use: secondary copies, easy-to-regenerate data.

## Intelligent-Tiering

S3 monitors access; auto-moves between Frequent and Infrequent tiers.

Costs: monitoring fee ($0.0025 per 1000 objects/mo) + per-tier storage.

Use: unknown access patterns. No retrieval fees.

Now includes Archive Instant and Archive tiers (auto-moves to Glacier-class).

## Glacier Tiers

### Instant Retrieval
- $0.004/GB; ms retrieval
- Min 90 days
- Use: occasional restore but fast

### Flexible
- $0.0036/GB
- Retrieval: minutes (Expedited) / hours (Standard) / 12+ hrs (Bulk)
- Min 90 days
- Use: backups; some recovery time OK

### Deep Archive
- $0.00099/GB (cheapest)
- Retrieval: 12-48 hours
- Min 180 days
- Use: legal hold, very long-term

## Retrieval Costs

Often forgotten:
- IA: $0.01/GB
- Glacier IR: $0.03/GB
- Glacier Flexible Bulk: $0.0025
- Glacier Deep Archive: $0.02/GB

For 1 TB monthly restore from IA: $10. From Glacier Deep: $20.

Plus request fees.

## Choosing

```
Access pattern → Class
Hot (daily) → Standard
Warm (weekly) → IA
Cold (monthly) → Glacier IR
Archive (yearly) → Glacier Flex or Deep
Unknown → Intelligent-Tiering
```

## Lifecycle Policies

Auto-transition or delete:
```yaml
Rules:
  - Id: ArchiveLogs
    Status: Enabled
    Filter:
      Prefix: logs/
    Transitions:
      - Days: 30
        StorageClass: STANDARD_IA
      - Days: 90
        StorageClass: GLACIER
      - Days: 365
        StorageClass: DEEP_ARCHIVE
    Expiration:
      Days: 2555    # 7 years
```

```bash
aws s3api put-bucket-lifecycle-configuration --bucket my-bucket --lifecycle-configuration file://lifecycle.json
```

## Lifecycle Concepts

### Transition
Move to cheaper class.

### Expiration
Delete after N days.

### Noncurrent Version
For versioned buckets: rules for old versions.
- Transition noncurrent → Glacier after 30
- Expire noncurrent after 365

### Incomplete Multipart
Cleanup unfinished uploads:
- AbortIncompleteMultipartUpload after 7 days

Common waste source.

## Math: Lifecycle Savings

Logs: 1 TB/month new; total 100 TB.

Without lifecycle:
- 100 TB × $0.023 = $2300/mo

With lifecycle (30 days Standard, then IA, then Glacier):
- Recent month: 1 TB × $0.023 = $23
- Next 2 months IA: 2 TB × $0.0125 = $25
- Rest Glacier IR: 97 TB × $0.004 = $388
- Total: ~$436/mo

Save: ~$1900/mo = $22k/yr. With more aggressive Glacier Deep: even more.

## Transition Cost

Per-object transition fee. For many small objects: charge adds.

For huge buckets with many small files: transition cost can exceed savings short-term.

Calculate.

## Min Object Size

IA / One Zone-IA: 128 KB minimum (charged as 128 KB if smaller).

For lots of tiny objects: keep in Standard or use Intelligent-Tiering.

## Min Storage Duration

IA: 30 days. Delete sooner = still pay 30.
Glacier IR: 90 days.
Glacier Flex: 90 days.
Glacier Deep: 180 days.

For short-lived data: don't move to IA/Glacier.

## Inventory

Daily report of objects + storage class + size:
```
Bucket = my-bucket
Inventory = my-inventory
Output = S3 bucket (Parquet, ORC, CSV)
```

Query with Athena:
```sql
SELECT storage_class, SUM(size) FROM inventory GROUP BY storage_class
```

Understand distribution; optimize lifecycle.

## Tags-Based Lifecycle

```yaml
Filter:
  Tag:
    Key: AutoArchive
    Value: 'true'
```

Apps tag what to archive; lifecycle acts.

## Lifecycle and Versioning

For versioned buckets:
- Current version: NoncurrentVersionTransitions ignores
- Noncurrent: NoncurrentVersionTransitions applies
- Delete markers: cleanup expired markers (orphaned)

```yaml
NoncurrentVersionTransitions:
  - NoncurrentDays: 30
    StorageClass: GLACIER
NoncurrentVersionExpiration:
  NoncurrentDays: 365
```

## Patterns

### Hot/Warm/Cold (Logs)
- 0-30 days: Standard
- 30-90: IA
- 90-365: Glacier IR
- 365+: Glacier Deep

### Backup Retention
- 7 days Standard
- 30 days IA
- 1 year Glacier
- Delete

### User Uploads
- Standard always
- Or Intelligent-Tiering (varied access)

## Common Mistakes

- No lifecycle (paying full price forever)
- Aggressive Glacier on hot data (retrieval cost spike)
- Many small objects in IA (128 KB minimum)
- No incomplete multipart cleanup
- Lifecycle without versioning rule (current vs noncurrent)

## Best Practices

- Lifecycle policy day 1
- Cleanup incomplete multipart (week+)
- Match class to access pattern
- Calculate retrieval cost
- Use Intelligent-Tiering if unsure
- Inventory monthly review
- Tag for granular lifecycle

## Glacier Vault Lock

Original Glacier had Vault Lock for WORM compliance. S3 Glacier classes use Object Lock instead.

## Class Switching

You can switch classes via:
- Lifecycle (auto)
- Direct API (manual `CopyObject` with new class)

Direct: full request cost; lifecycle is per object via background.

## Monitoring

S3 Storage Lens: per-bucket / per-prefix breakdown by class.

CloudWatch metrics: BucketSizeBytes per StorageType.

## Replication and Class

CRR / SRR can change target class:
```
Source: Standard
Target: Standard-IA  (cheaper DR)
```

Save on DR.

## Quick Refs

```bash
# Apply lifecycle
aws s3api put-bucket-lifecycle-configuration --bucket b --lifecycle-configuration file://lc.json

# Get
aws s3api get-bucket-lifecycle-configuration --bucket b

# Copy with class
aws s3 cp src dst --storage-class GLACIER
```

## Interview Prep

**Mid**: "Lifecycle for logs."

**Senior**: "Cost optimization for 1 PB bucket."

**Staff**: "Tiered storage strategy enterprise-wide."

## Next Topic

→ [T03 — Versioning, Object Lock, MFA Delete](T03-Versioning-Object-Lock.md)
