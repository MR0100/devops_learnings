# L08/C05/T05 — S3 Security (Block Public Access, Bucket Policies, KMS)

## Learning Objectives

- Lock down S3 buckets
- Prevent leaks

## Block Public Access

Account + bucket level switches:
- BlockPublicAcls: reject any public ACL request
- IgnorePublicAcls: ignore existing public ACLs
- BlockPublicPolicy: reject public bucket policies
- RestrictPublicBuckets: even existing public ignored

Enable all 4 at account + bucket. Default since 2023.

```bash
aws s3api put-public-access-block --bucket b \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

Account-wide:
```bash
aws s3control put-public-access-block --account-id 123 --public-access-block-configuration ...
```

## Bucket Policy

Resource-based. Common patterns:

### Force HTTPS
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::b", "arn:aws:s3:::b/*"],
  "Condition": {"Bool": {"aws:SecureTransport": "false"}}
}
```

### Force Encryption
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::b/*",
  "Condition": {
    "StringNotEquals": {"s3:x-amz-server-side-encryption": "aws:kms"}
  }
}
```

### Specific Principal Only
```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::123:role/MyApp"},
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::b/*"
}
```

### Only Via VPC Endpoint
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::b", "arn:aws:s3:::b/*"],
  "Condition": {
    "StringNotEquals": {"aws:SourceVpce": "vpce-xxx"}
  }
}
```

## ACLs (Legacy)

Object ACLs: per-object permissions. Mostly deprecated.

Default: ACLs disabled on new buckets (since 2023). Use bucket policies.

## IAM Policy + Bucket Policy

Both can grant. For same-account: either is enough.
For cross-account: BOTH needed.

## Encryption At Rest

Three modes:

### SSE-S3
AWS-managed keys. Default since 2023. Free.
```bash
aws s3 cp file s3://b/file
# Auto-encrypted with SSE-S3
```

### SSE-KMS
KMS-managed key. More control:
- Per-key access policy (KMS key policy)
- Audit (CloudTrail KMS events)
- Bring Your Own Key (BYOK)
- AWS-managed key (free) or Customer-managed key ($1/mo + API calls)

```bash
aws s3 cp file s3://b/file --sse aws:kms --sse-kms-key-id alias/myKey
```

### SSE-C
Customer provides key in request. You manage key entirely.
Rare.

## Bucket Encryption Default

```bash
aws s3api put-bucket-encryption --bucket b --server-side-encryption-configuration '{
  "Rules": [{
    "ApplyServerSideEncryptionByDefault": {
      "SSEAlgorithm": "aws:kms",
      "KMSMasterKeyID": "alias/myKey"
    },
    "BucketKeyEnabled": true
  }]
}'
```

All new objects encrypted with KMS key. BucketKey reduces KMS API costs (per-bucket key vs per-object).

## Encryption In Transit

TLS required:
- Bucket policy Deny `aws:SecureTransport=false`
- All SDK / CLI uses HTTPS by default

## Client-Side Encryption

Encrypt before upload. KMS for key.
- App encrypts; S3 stores ciphertext
- S3 never sees plaintext or key

For: highest sensitivity, regulatory.

AWS Encryption SDK; CSE-KMS variants.

## Access Logging

Log all S3 requests:
```bash
aws s3api put-bucket-logging --bucket b --bucket-logging-status '{
  "LoggingEnabled": {
    "TargetBucket": "log-bucket",
    "TargetPrefix": "logs/b/"
  }
}'
```

Logs go to another S3 bucket (separate account for security).

Or use CloudTrail Data Events (more detailed; expensive).

## CloudTrail Data Events

Per-object operations logged. Cost: $0.10 per 100k events.

For sensitive buckets only. Use:
- Audit who accessed what
- Detect anomaly access
- Compliance evidence

## Macie

Scans S3 for PII:
- SSN, credit cards, PHI
- Reports findings

Cost: per GB scanned + per-object eval.

For: data classification, compliance.

## Cross-Account

Account A bucket; Account B role:

A's bucket policy:
```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::B:role/X"},
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::a/*"
}
```

B's role policy:
```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::a/*"
}
```

Both needed.

## KMS Key for Cross-Account

If SSE-KMS: KMS key policy must allow B's role too. Else B can't decrypt.

```json
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::B:role/X"},
    "Action": ["kms:Decrypt"],
    "Resource": "*"
  }]
}
```

## Bucket Ownership

ACLs disabled (default 2023+): bucket owner owns all objects.

ACLs enabled (legacy): uploader can own. Cross-account upload → other account owns object; bucket owner can't access.

## IP / Network Restrictions

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::b", "arn:aws:s3:::b/*"],
  "Condition": {
    "NotIpAddress": {"aws:SourceIp": ["192.168.0.0/16"]}
  }
}
```

Restrict to known IPs.

## Presigned URLs

Temporary signed URL anyone with URL can use:
```bash
aws s3 presign s3://b/file --expires-in 3600
```

For: upload from browser; share temporary access; download token.

Permissions inherited from signer's role.

## Access Points

Multiple "named endpoints" to bucket, each with own policy:
```bash
aws s3control create-access-point --account-id 123 --name my-ap --bucket b
```

Useful: many teams sharing bucket with different scopes.

## Object Lambda

Transform on retrieve. E.g., redact PII per consumer:
```
GetObject through Object Lambda → Lambda function → returns transformed
```

For: privacy, format conversion, watermarking.

## Best Practices

Day-one:
- Block Public Access account + bucket
- HTTPS-only policy
- Default encryption (SSE-KMS for sensitive)
- Versioning
- Server access logging
- CloudTrail data events for sensitive

Ongoing:
- Macie for PII detection
- Access Analyzer findings
- Audit bucket policies
- Lifecycle for noncurrent versions

## Common Mistakes

- Public bucket (most common breach)
- ACLs enabled (legacy)
- SSE-S3 when KMS needed
- KMS key policy missing
- No HTTPS enforcement
- Forgetting BlockPublicAccess at account

## Anti-Patterns

- One bucket; many teams; permissive
- Sharing buckets across accounts without strict policies
- KMS key without rotation
- Production data in dev bucket

## Tools

- Access Analyzer (alerts on external access)
- Macie (PII scan)
- Security Hub (aggregated findings)
- AWS Config (compliance rules)

## Quick Refs

```bash
# Block public
aws s3api put-public-access-block --bucket b --public-access-block-configuration BlockPublicAcls=true,...

# Encryption default
aws s3api put-bucket-encryption --bucket b --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"alias/myKey"}}]}'

# Bucket policy
aws s3api put-bucket-policy --bucket b --policy file://policy.json
```

## Interview Prep

**Mid**: "Lock down S3 — checklist."

**Senior**: "Cross-account S3 with KMS."

**Staff**: "S3 security at 1000-bucket scale."

## Next Topic

→ [T06 — Multipart Upload, Transfer Acceleration](T06-Multipart-Transfer-Accel.md)
