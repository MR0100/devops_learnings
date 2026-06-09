# L07/C05/T01 — Object Storage (S3, GCS, Blob Storage)

## Learning Objectives

- Use object storage correctly
- Pick storage class

## Object Storage

Flat namespace of "objects" (files + metadata) in "buckets". Accessed via HTTP API. Vs filesystems (POSIX, hierarchical, mutable) and block (raw blocks).

## Key Traits

- Massively scalable (exabyte)
- 11 9s durability (99.999999999%) — practically never lose
- High availability (99.99% multi-AZ)
- HTTP API (GET, PUT, DELETE)
- Eventual consistency historically; now strong (S3 since 2020)
- No file-system semantics (no rename; no append; no partial write)

## Use Cases

- Static web sites
- Backups
- Data lake (parquet, csv files)
- Media (images, video)
- Logs
- Software distribution
- Container images (via Registry, but registry stores in S3)
- Application uploads

## S3 (AWS)

```bash
# Upload
aws s3 cp file.txt s3://my-bucket/path/file.txt

# Download
aws s3 cp s3://my-bucket/path/file.txt file.txt

# List
aws s3 ls s3://my-bucket/

# Sync
aws s3 sync ./local s3://my-bucket/path/
```

Bucket: globally unique name; in one region.
Object: identified by `s3://bucket/key`.

## Storage Classes (S3)

| Class | Use | $/GB/mo (us-east-1) | Min storage | Retrieval |
|---|---|---|---|---|
| Standard | hot | $0.023 | 0 days | instant |
| Standard-IA | infrequent | $0.0125 | 30 days | instant |
| One Zone-IA | non-critical | $0.01 | 30 days | instant |
| Glacier Instant Retrieval | archive | $0.004 | 90 days | ms |
| Glacier Flexible | archive | $0.0036 | 90 days | minutes-hours |
| Glacier Deep Archive | cold archive | $0.00099 | 180 days | 12+ hours |
| Intelligent-Tiering | auto | base + small fee | 0 | instant |

Pick based on access frequency. Lifecycle policies auto-transition.

## Lifecycle Policy

```yaml
Rules:
  - Id: Archive
    Status: Enabled
    Filter:
      Prefix: logs/
    Transitions:
      - Days: 30
        StorageClass: STANDARD_IA
      - Days: 90
        StorageClass: GLACIER
    Expiration:
      Days: 365
```

Automate cost reduction.

## Versioning

Keep old versions on overwrite/delete:
```bash
aws s3api put-bucket-versioning --bucket b --versioning-configuration Status=Enabled
```

Recover deleted/overwritten. Cost: more storage.

MFA Delete: require MFA to permanently delete (anti-ransomware).

## Replication

Cross-Region Replication (CRR): async copy to another bucket (DR).
Same-Region Replication (SRR): for compliance, log aggregation.

```yaml
Replication:
  Role: arn:aws:iam::...:role/...
  Rules:
    - Status: Enabled
      Destination:
        Bucket: arn:aws:s3:::backup-bucket
        StorageClass: STANDARD_IA
```

Cost: storage in both + replication API calls.

## Access Control

### Bucket Policy (Resource-based)
```json
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::123:role/MyRole"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

### IAM Policy (User-based)
```json
{
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

### Public Access Block
Default: blocked. Don't disable unless serving public website.

### Presigned URLs
Temporary, signed URL anyone can use:
```python
url = s3.generate_presigned_url("get_object", Params={"Bucket":"b","Key":"k"}, ExpiresIn=3600)
```

Useful: upload directly from browser; bypass your server.

## Encryption

- **SSE-S3**: AWS-managed key; default on (2023+)
- **SSE-KMS**: KMS key; audit; rotation
- **SSE-C**: customer-provided key (rare)
- **Client-side**: encrypt before upload

Use SSE-KMS for sensitive; SSE-S3 for general.

## Performance

- 5500 GET / 3500 PUT per prefix per second
- For more: split by prefix (parallel)
- Multi-part upload for >100 MB (parallel parts)
- Transfer Acceleration: upload via CloudFront edge (faster across continents)

## Consistency

Strong read-after-write (since Dec 2020). Read after PUT returns latest. Read after DELETE returns 404. No more eventual surprise.

## Costs

- Storage: per class
- Requests: per 1000 (PUT $0.005, GET $0.0004)
- Egress: $0.09/GB to Internet; free to same region
- Lifecycle transitions: per object
- Replication: storage in target + API + xregion bandwidth

For massive read traffic: cost dominated by GETs and egress.

## Bucket Naming

Globally unique; lowercase; 3-63 chars; no underscore.

Strategy: `<company>-<purpose>-<env>-<random>`:
`acme-logs-prod-x4z2`

Or include account: `acme-logs-123456789012-us-east-1`.

## S3 Select / Object Lambda

S3 Select: query CSV/JSON within objects without download.
S3 Object Lambda: transform on retrieve (e.g., redact PII per consumer).

## Event Notifications

S3 events → SNS, SQS, Lambda, EventBridge:
- Object created
- Object deleted
- Multipart upload completed

Drive workflows (process uploaded files).

## Inventory Reports

Daily/weekly CSV listing all objects + metadata. For:
- Auditing
- Replication tracking
- Bulk operations input

## Batch Operations

Apply to many objects:
- Copy
- Set tags
- Invoke Lambda per object

Useful for migrations, bulk metadata updates.

## GCS (GCP)

Similar:
- Standard, Nearline, Coldline, Archive
- Strong consistency
- IAM + bucket policies
- Object versioning
- Lifecycle
- gsutil / gcloud CLI

Differences:
- Multi-region buckets (data replicated across many regions)
- Pricing structure slightly different

## Azure Blob Storage

Three tiers: Hot, Cool, Archive.
Containers (= buckets).
Blob types: Block (general), Append (logs), Page (VHDs).

## Common Mistakes

- Public buckets accidentally (use Public Access Block)
- No lifecycle (paying full price forever)
- One huge bucket vs partitioned (perf limits)
- No versioning (lose on delete)
- Encryption on but key broken
- Egress not modeled (huge bills)

## Data Lake Architecture

```
Raw zone (S3 Standard) - unprocessed ingest
↓
Transformed zone (S3 Standard) - clean parquet
↓
Curated zone (S3 IA) - business views
```

Query with Athena (SQL on S3 parquet).

## Best Practices

- Enable versioning for important data
- Lifecycle policy from day 1
- Block public access
- Encrypt with KMS
- CloudTrail for audit
- Replicate for DR
- Tags for cost tracking
- Use STS-based access for apps

## Interview Prep

**Junior**: "S3 vs EBS."

**Mid**: "Lifecycle policy design for logs."

**Senior**: "S3 cost optimization."

**Staff**: "Data lake on S3 — architecture."

## Next Topic

→ [T02 — Block Storage](T02-Block-Storage.md)
