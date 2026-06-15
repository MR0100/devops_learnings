# L08/C05 — S3 Deep Dive

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Buckets-Objects-Keys.md) | Buckets, Objects, Keys, Prefixes | 0.5 hr |
| [T02](T02-Storage-Classes.md) | Storage Classes & Lifecycle Policies | 1 hr |
| [T03](T03-Versioning-Object-Lock.md) | Versioning, Object Lock, MFA Delete | 1 hr |
| [T04](T04-Performance.md) | S3 Performance & Request Patterns | 1 hr |
| [T05](T05-S3-Security.md) | S3 Security (Block Public Access, Bucket Policies, KMS) | 1.5 hr |
| [T06](T06-Multipart-Transfer-Accel.md) | Multipart Upload, Transfer Acceleration | 0.5 hr |
| [T07](T07-Event-Notifications.md) | S3 Event Notifications & Triggers | 0.5 hr |
| [T08](T08-EFS-FSx.md) | EFS & FSx (File Storage) | 1 hr |

## Concepts

- **Bucket**: global namespace; per region
- **Object**: file + metadata; up to 5 TB
- **Key**: full object path within bucket (e.g., `logs/2026/06/09/web1.log`)
- **Prefix**: any leading substring of the key — affects performance partitioning
- **Region**: where the data physically lives

## Storage Classes

| Class | Use | First-byte | Min storage | Retrieval |
|---|---|---|---|---|
| Standard | Frequent | ms | none | none |
| Intelligent-Tiering | Variable | ms | none | none + per-object monitoring fee |
| Standard-IA | Infrequent, 30d+ | ms | 30 days | per-GB retrieval |
| One Zone-IA | Single AZ IA | ms | 30 days | retrieval fee |
| Glacier Instant | Archive ms retrieval | ms | 90 days | retrieval fee |
| Glacier Flexible | Archive | mins to hours | 90 days | bulk/std/expedited |
| Glacier Deep Archive | Coldest | 12+ hours | 180 days | std/bulk |

**Recommendation**: Intelligent-Tiering for new uncertain workloads; Standard for high-traffic; Standard-IA for backups; Glacier for compliance archives.

## Lifecycle Policies

```json
{
  "Rules": [{
    "ID": "Tier old logs",
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},
      {"Days": 90, "StorageClass": "GLACIER_IR"},
      {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
    ],
    "Expiration": {"Days": 2555}
  }, {
    "ID": "Cleanup incomplete uploads",
    "Status": "Enabled",
    "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}
  }]
}
```

**Don't forget**: abort incomplete multipart uploads — silent cost growth.

## Versioning

- Each PUT creates a new version
- DELETE adds a delete marker (object isn't gone)
- `s3:DeleteObjectVersion` is required to truly delete
- Required for: cross-region replication, Object Lock

### MFA Delete
- Requires MFA on the root user to delete versions
- Strong protection; enable for critical buckets

## Object Lock

WORM (Write-Once-Read-Many) protection — even root can't delete.

Two modes:
- **Governance** — overridable by privileged users
- **Compliance** — NO ONE can override (even AWS support)

Use: ransomware defense, compliance retention.

## Performance

### Throughput
- **3500 PUT/COPY/POST/DELETE/s per prefix**
- **5500 GET/s per prefix**
- Use random/distributed prefixes for high-throughput workloads
- AWS automatically partitions prefixes; performance scales

### Transfer Acceleration
- Uploads via nearest CloudFront PoP, then to S3
- ~50-500% throughput improvement for cross-region uploads
- Extra cost per GB

### Multipart Upload
- Required for objects > 5 GB
- Recommended for objects > 100 MB
- Parallel parts (up to 10,000)
- Resume on partial failure

```python
# Boto3 auto-uses multipart
s3 = boto3.client("s3")
config = TransferConfig(multipart_threshold=8*1024*1024, max_concurrency=10)
s3.upload_file("big.zip", "my-bucket", "key", Config=config)
```

## Security

### Block Public Access (BPA)

Account-level + bucket-level setting:
- BlockPublicAcls — reject public ACLs on objects
- IgnorePublicAcls — ignore existing public ACLs
- BlockPublicPolicy — reject public bucket policy
- RestrictPublicBuckets — public bucket = inaccessible

**Always enable all four** at account level unless you specifically need public.

### Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {"Bool": {"aws:SecureTransport": "false"}}
    },
    {
      "Sid": "DenyUnencrypted",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringNotEquals": {"s3:x-amz-server-side-encryption": "aws:kms"}
      }
    }
  ]
}
```

### Encryption

Server-side options:
- **SSE-S3** (AES-256) — default; AWS-managed keys
- **SSE-KMS** — customer-managed KMS keys
- **SSE-C** — customer-provided keys (rare)
- **DSSE-KMS** — dual-layer encryption (compliance)

S3 Bucket Keys: reduce KMS cost (caches data key)

Client-side encryption — your code encrypts before upload.

### Access Logging
- S3 → S3 server access logs
- CloudTrail data events (more powerful, expensive)

## Cross-Region Replication (CRR)

```
{
  "Role": "arn:aws:iam::...:role/replication-role",
  "Rules": [{
    "ID": "ReplicateAll",
    "Status": "Enabled",
    "Priority": 1,
    "Filter": {},
    "DeleteMarkerReplication": {"Status": "Disabled"},
    "Destination": {
      "Bucket": "arn:aws:s3:::my-bucket-replica",
      "StorageClass": "STANDARD_IA"
    }
  }]
}
```

- Versioning required on both buckets
- Async (typically seconds)
- Filter by prefix or tag
- Can replicate to another account

## Event Notifications

Triggers on object creation/deletion:
- → SNS
- → SQS
- → Lambda
- → EventBridge

Example: image uploaded → Lambda resizes → put thumbnail.

## File Storage (EFS & FSx)

S3 is object storage; when workloads need a **shared POSIX/SMB filesystem**, use file storage:

- **EFS**: elastic, multi-AZ NFS for Linux; thousands of concurrent clients (EC2/ECS/EKS/Lambda); IA + Archive tiers via lifecycle management.
- **FSx for Windows File Server**: SMB shares with Active Directory and Windows ACLs.
- **FSx for Lustre**: HPC/ML scratch, hundreds of GB/s, links to an S3 bucket.
- **FSx for NetApp ONTAP**: multiprotocol (NFS/SMB/iSCSI) with enterprise snapshots/dedup.
- **FSx for OpenZFS**: ZFS snapshots/clones over NFS at low latency.

Heuristic: single-attach block → **EBS**; objects/HTTP → **S3**; many writers + POSIX → **EFS**; Windows → **FSx Windows**; HPC → **FSx Lustre**.

## Common Mistakes

- Public buckets (data leaks)
- No lifecycle policy (cost growth)
- No versioning (accidental deletes)
- No bucket policy enforcing HTTPS
- Incomplete multipart uploads piling up
- Missing replication on critical buckets
- Logs into same bucket (loop)

## Interview Themes

- "How does S3 achieve 11 nines of durability?"
- "Choose storage class for a use case"
- "Compare SSE-S3 and SSE-KMS"
- "S3 performance — how to scale to 100K req/s?"
- "Walk me through a leaked-bucket incident"
- "EFS vs FSx vs EBS vs S3 — pick for a workload"
