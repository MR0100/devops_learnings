# L26/C04/T02 — Intelligent Tiering

## Learning Objectives

- Use S3 Intelligent Tiering
- Auto-optimize

## Intelligent Tiering

S3 storage class:
- Monitors access
- Auto-moves between tiers
- No retrieval fees (between tiers)

## Tiers

- Frequent Access (default)
- Infrequent (30+ days no access)
- Archive Instant (90+ days)
- Archive (90+ days, opt-in)
- Deep Archive (180+ days, opt-in)

Auto-transitions.

## Cost

- Small monitoring fee
- Storage similar to underlying class

For: unknown patterns, intelligent saves cost.

## When

- Unknown access patterns
- Mixed access (some hot, some cold)
- Don't want lifecycle management

## When Not

- Known hot (Standard cheaper)
- Known cold (Glacier cheaper)
- Small objects (< 128 KB; not tiered)

## Setup

```bash
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket my-bucket \
  --id config-1 \
  --intelligent-tiering-configuration ...
```

Or per upload:
```bash
aws s3 cp file s3://bucket --storage-class INTELLIGENT_TIERING
```

## Default for New

```bash
# Set lifecycle to move all new objects to Intelligent
aws s3api put-bucket-lifecycle-configuration ...
```

For: future objects auto-tier.

## Monitoring Fee

$0.0025 per 1000 objects per month.

For 10M objects: $25/mo monitoring.

For: high-object-count buckets watch fee.

## Best Practices

- Default for new buckets
- Use unless known pattern
- Combine with lifecycle for very cold
- Monitor monitoring cost (huge object counts)

## Common Mistakes

- Use for known patterns (more expensive)
- Skip for small objects (no benefit)
- Forget monitoring fee at scale

## Real Examples

Many SaaS:
- Default Intelligent for user uploads
- Lifecycle for known logs

## Quick Refs

```bash
# Set class
aws s3 cp file s3://bucket --storage-class INTELLIGENT_TIERING

# Bucket config
aws s3api put-bucket-intelligent-tiering-configuration
```

## Interview Prep

**Mid**: "Intelligent Tiering."

**Senior**: "When use."

## Next Topic

→ [T03 — Snapshot Cleanup](T03-Snapshot-Cleanup.md)
