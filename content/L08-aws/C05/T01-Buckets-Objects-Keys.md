# L08/C05/T01 — Buckets, Objects, Keys, Prefixes

## Learning Objectives

- Use S3 model fluently
- Design key structure

## Hierarchy

```
S3 (service)
└── Bucket (region; globally-unique name)
    └── Object (key, data, metadata)
```

No real directories. "Folders" are key prefixes (`logs/2024/`).

## Bucket

Container. Global namespace; pick unique:
- 3-63 chars
- Lowercase, numbers, hyphens
- No underscores, dots (avoid; complicates HTTPS)
- Must NOT look like IP

Strategy: `<company>-<purpose>-<env>-<random>`:
- `acme-logs-prod-x4z9`
- `acme-images-staging-q2m1`

Or include account ID: `acme-data-123456789012-us-east-1`.

## Region

Bucket lives in one region:
- Data stays in region
- Cross-region: replication
- Latency: queries from outside region slow

## Object

Has:
- Key (path/name)
- Data (up to 5 TB)
- Metadata (user + system)
- Version ID (if versioning on)
- Storage class

## Key

UTF-8; up to 1024 chars.

```
logs/2024/06/09/server1.log
images/users/123/profile.jpg
backups/db/2024-06-09.dump
```

Prefixes (the leading parts) are how you "organize."

## Object URL

```
https://my-bucket.s3.us-east-1.amazonaws.com/logs/2024/06/09/server1.log
https://s3.us-east-1.amazonaws.com/my-bucket/logs/2024/06/09/server1.log
```

Virtual-hosted style (first): preferred. Bucket as subdomain.

## S3 Express / Directory Buckets

Newer (2023+): high-perf, single-AZ for low-latency.

For: ML training, analytics scratch. 50% lower latency; doesn't replicate cross-AZ.

Different bucket type: `--bucket my-bucket--use1-az5--x-s3`.

## Operations

### Upload
```bash
aws s3 cp file.txt s3://my-bucket/logs/file.txt
aws s3api put-object --bucket my-bucket --key logs/file.txt --body file.txt
```

### Download
```bash
aws s3 cp s3://my-bucket/logs/file.txt file.txt
```

### List
```bash
aws s3 ls s3://my-bucket/logs/
aws s3api list-objects-v2 --bucket my-bucket --prefix logs/
```

### Delete
```bash
aws s3 rm s3://my-bucket/logs/file.txt
aws s3 rm s3://my-bucket/logs/ --recursive  # all under prefix
```

### Sync
```bash
aws s3 sync ./local s3://my-bucket/path/
```

Incremental; uploads only changed.

## Metadata

System (set by S3):
- `Content-Type`
- `Content-Length`
- `Last-Modified`
- `ETag` (MD5 for non-multipart)
- `Cache-Control`

User-defined (`x-amz-meta-` prefix):
- `x-amz-meta-author`
- `x-amz-meta-version`

```bash
aws s3 cp file.txt s3://my-bucket/file.txt --metadata "author=alice,team=eng"
```

## Multipart Upload

For files >100 MB (recommended) or >5 GB (required):
- Split into parts
- Upload in parallel
- Resume on failure
- Better throughput

SDK / CLI handles automatically:
```bash
aws configure set default.s3.multipart_threshold 100MB
aws s3 cp big.tar s3://my-bucket/    # auto multipart
```

## Performance

Per-prefix limits:
- 3500 PUT/COPY/POST/DELETE per second
- 5500 GET/HEAD per second

For higher: spread across multiple prefixes.

Random hashes used to be needed; not anymore (2018+). S3 auto-spreads.

## Prefixes for Performance

Heavy traffic? Spread:
```
logs/server1/2024/06/09/...
logs/server2/2024/06/09/...
```

Or:
```
logs/2024/06/09/server1/...
```

Both perform similar (S3 spreads).

## Listing

`ListObjectsV2`: paginated; up to 1000 per page.

```bash
aws s3api list-objects-v2 --bucket my-bucket --prefix logs/ --max-keys 100
```

For massive buckets: use S3 Inventory (daily report).

## Versioning

Enabled per bucket:
```bash
aws s3api put-bucket-versioning --bucket my-bucket --versioning-configuration Status=Enabled
```

Once enabled: cannot disable (only suspend).

Each PUT creates version ID. DELETE adds delete marker.

Restore: copy old version.

## Object Lock

Write-Once-Read-Many. For compliance:
```bash
aws s3api put-object-lock-configuration --bucket my-bucket --object-lock-configuration ...
```

Modes:
- Governance (some can override)
- Compliance (NO ONE can delete)

Use: SOX, finance records.

## Sizing

- Smallest object: 0 bytes
- Largest single PUT: 5 GB
- Largest multipart: 5 TB
- Bucket: unlimited objects + size

For large objects: use multipart.

## ETag

For non-multipart: MD5 of content.
For multipart: MD5 of MD5s + part count. Not a checksum of full content.

Use for integrity check on non-multipart.

For better: SHA256 / CRC32 checksums (S3 supports).

## Object Tags

```bash
aws s3api put-object-tagging --bucket my-bucket --key file.txt --tagging "TagSet=[{Key=Owner,Value=alice}]"
```

For:
- Cost allocation
- IAM conditions
- Lifecycle policies

10 tags per object.

## Common Operations CLI

```bash
# Bucket size
aws s3 ls s3://my-bucket --recursive --human-readable --summarize

# Object count (small buckets)
aws s3 ls s3://my-bucket --recursive | wc -l

# For huge: S3 Storage Lens or Inventory

# Copy
aws s3 cp s3://src/path s3://dst/path

# Sync
aws s3 sync s3://src/ s3://dst/ --delete

# Presigned URL
aws s3 presign s3://my-bucket/file.txt --expires-in 3600
```

## Storage Classes

Covered T02.
- Standard
- Standard-IA
- One Zone-IA
- Glacier (Instant/Flexible/Deep)
- Intelligent-Tiering

Per-object choice.

## Encryption

Default (since 2023): SSE-S3 on all new buckets.

Override per object or bucket. Covered T05.

## Replication

Cross-region (CRR), same-region (SRR). Covered separately.

## Notifications

S3 events → SNS / SQS / Lambda. Covered T07.

```
ObjectCreated → process
ObjectDeleted → audit
```

## Cost Model

- Storage: per GB-month
- PUT: $0.005 per 1000
- GET: $0.0004 per 1000
- Egress: $0.09/GB to Internet
- Replication: storage in target + xregion bandwidth

For massive read traffic: GET cost adds up.

## Common Mistakes

- Underscore / dot in bucket name (TLS issues)
- 1000s of small files (overhead; use compression)
- No lifecycle policy
- Public bucket accidentally
- No versioning (data loss risk)
- Encryption "default" assumed but custom needed

## Best Practices

- Predictable naming
- Tags from day 1
- Lifecycle policy day 1
- Block Public Access on
- Versioning + lifecycle
- Encryption (KMS for sensitive)
- Tag for cost
- S3 Inventory for large buckets

## Quick Refs

```bash
# Upload / download / sync
aws s3 cp file.txt s3://my-bucket/logs/file.txt
aws s3 cp s3://my-bucket/logs/file.txt file.txt
aws s3 sync ./local s3://my-bucket/path/

# List a prefix (paginated)
aws s3api list-objects-v2 --bucket my-bucket --prefix logs/ --max-keys 100

# Bucket size / object count (small buckets)
aws s3 ls s3://my-bucket --recursive --human-readable --summarize

# Presigned URL (temporary access)
aws s3 presign s3://my-bucket/file.txt --expires-in 3600
```

## Interview Prep

**Junior**: "S3 vs EBS."

**Mid**: "Key design for hot prefix."

**Senior**: "Migration of 10 PB."

**Staff**: "Multi-account S3 data platform."

## Next Topic

→ [T02 — Storage Classes & Lifecycle Policies](T02-Storage-Classes.md)
