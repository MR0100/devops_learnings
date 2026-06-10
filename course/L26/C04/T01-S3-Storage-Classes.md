# L26/C04/T01 — S3 Storage Class Analysis

## Learning Objectives

- Pick S3 class
- Save with tiering

## Classes

- Standard: hot
- Standard-IA: 30+ days
- One Zone-IA: cheaper IA
- Glacier Instant: archive fast retrieve
- Glacier Flexible: archive minutes-hours
- Glacier Deep Archive: archive 12+ hours

## Pricing (approx)

| | $/GB/mo |
|---|---|
| Standard | $0.023 |
| Standard-IA | $0.0125 |
| One Zone-IA | $0.01 |
| Glacier Instant | $0.004 |
| Glacier Flexible | $0.0036 |
| Glacier Deep | $0.00099 |

## Retrieval Costs

- Standard: free (charged transfer)
- IA: $0.01/GB retrieved
- Glacier: depends

## Class Analysis

```bash
aws s3api put-bucket-analytics-configuration \
  --bucket my-bucket \
  --id analytics-1 \
  --analytics-configuration ...
```

Auto-analyzes access patterns; recommends.

## Intelligent Tiering

```bash
aws s3api put-bucket-intelligent-tiering-configuration ...
```

Auto-move:
- Hot → IA after 30 days
- IA → Archive after 90 days

For: hands-off.

## Lifecycle

```json
{
  "Rules": [
    {
      "Status": "Enabled",
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"}
      ],
      "Expiration": {"Days": 365}
    }
  ]
}
```

For: defined policy.

## Multi-Region

Replicate to:
- Same region (One Zone-IA)
- Cross-region (DR)

For: cost vs DR.

## Object Size

Min object size for IA:
- 128 KB billed at minimum

Many small files: stay Standard.

## Examples

### Logs
- Recent: Standard (queries)
- Old: Glacier (rarely access)

### Backups
- Recent: Standard-IA
- Old: Deep Archive

### User Content
- Photos: Standard (frequent access)
- Old: IA

## Cost Calculator

```
1 TB hot Standard: $23/mo
1 TB cold Glacier Deep: $1/mo
```

20× difference.

## Best Practices

- Lifecycle policies
- Intelligent Tiering for unknown
- Class Analysis for guidance
- Min object size aware

## Common Mistakes

- All Standard (expensive)
- No lifecycle (grows forever)
- Wrong class for access pattern
- Retrieval cost ignored

## Quick Refs

```bash
# Lifecycle
aws s3api put-bucket-lifecycle-configuration

# Class
aws s3 cp file s3://bucket --storage-class GLACIER

# Analysis
aws s3api put-bucket-analytics-configuration

# Intelligent Tiering
aws s3api put-bucket-intelligent-tiering-configuration
```

## Interview Prep

**Mid**: "S3 classes."

**Senior**: "Lifecycle."

**Staff**: "Storage strategy."

## Next Topic

→ [T02 — Intelligent Tiering](T02-Intelligent-Tiering.md)
