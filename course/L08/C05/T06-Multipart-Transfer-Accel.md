# L08/C05/T06 — Multipart Upload, Transfer Acceleration

## Learning Objectives

- Use multipart effectively
- Configure transfer acceleration

## Multipart Upload

Split big files; upload parts in parallel.

When:
- Files > 100 MB recommended
- Files > 5 GB REQUIRED (single PUT max)
- Up to 5 TB per object total

## Three Steps

1. **Initiate**: get upload ID
2. **Upload parts**: each part 5 MB to 5 GB; max 10,000 parts
3. **Complete**: assemble parts

```bash
# Auto via CLI / SDK
aws s3 cp big.tar s3://b/big.tar
```

SDK handles steps 1-3 automatically.

## Manual Multipart

```bash
# Initiate
aws s3api create-multipart-upload --bucket b --key big.tar
# Returns UploadId

# Upload parts
aws s3api upload-part --bucket b --key big.tar --part-number 1 --upload-id $UID --body part1.bin
aws s3api upload-part --bucket b --key big.tar --part-number 2 --upload-id $UID --body part2.bin

# Complete
aws s3api complete-multipart-upload --bucket b --key big.tar --upload-id $UID --multipart-upload '{
  "Parts": [
    {"PartNumber": 1, "ETag": "abc"},
    {"PartNumber": 2, "ETag": "def"}
  ]
}'
```

## Why Multipart

### Speed
Parallelism: 10 parts uploaded concurrently → ~10× faster.

### Resilience
Failed part: resend just that part; not whole file.

### Resume
Crash mid-upload: resume from last completed part.

### Required for >5 GB
Single PUT max 5 GB.

## Part Size

```
part_size = max(5 MB, total_size / 10000)
```

For 1 TB file: ~104 MB parts (10000 parts). For better parallelism: bigger parts (e.g., 500 MB, 2048 parts).

CLI default: 8 MB threshold; 8 MB chunks. Configure:
```bash
aws configure set default.s3.multipart_chunksize 64MB
aws configure set default.s3.multipart_threshold 100MB
```

## Concurrency

```bash
aws configure set default.s3.max_concurrent_requests 50
```

More concurrency = faster but more CPU / bandwidth.

## ETag

For non-multipart: MD5 of content.
For multipart: not MD5 of full file. Format: `MD5(concat(MD5(part1)..MD5(partN)))-N`.

```
abc123-10  (10 parts)
```

Not useful for integrity check across whole file.

For integrity: use SHA256 / CRC32 checksums on parts (S3 supports).

## Checksum

S3 supports per-part checksums:
- CRC32, CRC32C, SHA1, SHA256
- Verify integrity end-to-end

```bash
aws s3 cp file s3://b/ --checksum-algorithm SHA256
```

S3 stores; can verify on download.

## Abort

Cancel multipart in progress:
```bash
aws s3api abort-multipart-upload --bucket b --key big.tar --upload-id $UID
```

Releases part storage. ALWAYS abort failed uploads (or use lifecycle).

## Incomplete Multipart Cleanup

Lifecycle rule:
```yaml
AbortIncompleteMultipartUpload:
  DaysAfterInitiation: 7
```

Critical: forgotten incomplete uploads accumulate; storage cost grows.

## List Incomplete

```bash
aws s3api list-multipart-uploads --bucket b
```

Cleanup leftover.

## CLI Defaults

```ini
[default]
s3 =
    multipart_threshold = 100MB
    multipart_chunksize = 50MB
    max_concurrent_requests = 20
    max_queue_size = 10000
```

In `~/.aws/config`.

## Transfer Acceleration

Upload via CloudFront edge POPs → S3 region.

For: distant clients (Asia uploading to US bucket).

### Enable
```bash
aws s3api put-bucket-accelerate-configuration --bucket b --accelerate-configuration Status=Enabled
```

Endpoint:
```
https://b.s3-accelerate.amazonaws.com
```

CLI:
```bash
aws s3 cp file.bin s3://b/file.bin --endpoint-url https://s3-accelerate.amazonaws.com
```

### Cost
Extra: $0.04/GB uploaded.

### Benefit
50-500% faster for distant clients.

Test: AWS S3 Speed Test compares accelerated vs direct.

For close clients: no benefit; don't pay extra.

## Bucket Naming

Transfer Acceleration requires bucket name DNS-compatible:
- No dots (TLS cert wildcard issues)
- Standard lowercase, hyphens

## Multipart + Acceleration

Together: large files from distant clients = best perf.

CLI handles automatically.

## Single Region Within US

For US client → US bucket: small benefit. Don't enable.

For US client → EU bucket: big benefit. Enable.

## Performance Tuning Workflow

For slow uploads:
1. Multipart enabled? (>8 MB by default)
2. Concurrency? (`--max-concurrent-requests` higher)
3. Acceleration? (test for distant)
4. Network bandwidth? (saturated = the limit)
5. Same region as client?

## Snowball / Data Sync

For PB-scale: physical Snowball:
- AWS ships device
- Load data on-prem
- Ship back
- AWS loads into S3

Faster than 100 Mbps Internet for >50 TB.

DataSync: managed agent for ongoing on-prem → S3 sync.

## Egress Optimization

Downloads:
- Multipart download (range GETs in parallel)
- CloudFront for repeated content
- Transfer Acceleration for upload only (not download)

## S3 Express One Zone

For ultra-low latency:
- Single-AZ
- Sub-ms first byte
- High throughput
- For ML, analytics

Different bucket type; doesn't replicate; pricier per request but cheaper for high-RPS workloads.

## Bandwidth from EC2

Per-instance EBS / network bandwidth:
- m6i.large: ~10 Gbps to S3
- m6i.16xlarge: ~100 Gbps

For massive uploads: big instance + parallel.

## VPC Endpoint

S3 Gateway endpoint: avoid NAT cost; not faster (same backbone). But cheaper.

## Latency vs Throughput

- First byte latency: ~50-100 ms typical
- After connection: 100s of MB/sec per stream

For huge throughput: many streams.

## Monitoring

CloudWatch:
- BytesUploaded
- TotalRequestLatency
- FirstByteLatency
- 5xxErrors

For slow uploads: check FirstByteLatency.

## Common Mistakes

- No multipart for huge files (single PUT timeout)
- Tiny part sizes (too many parts; overhead)
- 8 MB parts for 5 TB file (62500 parts; over limit)
- No incomplete cleanup (storage leak)
- Acceleration for nearby clients (paying for no benefit)

## Calculation Example

10 GB file from London → US bucket:
- Without acceleration: ~10 Mbps Internet = ~2 hr
- With acceleration: ~50 Mbps via CloudFront = ~25 min

For nightly batch: significant.

## Best Practices

- Multipart auto-on (CLI default usually fine)
- Lifecycle cleanup incomplete
- Acceleration tested before adopting
- Bandwidth-appropriate instance for high-throughput
- Verify with checksums

## Quick Refs

```bash
# Acceleration
aws s3api put-bucket-accelerate-configuration --bucket b --accelerate-configuration Status=Enabled

# Use accelerated endpoint
aws s3 cp file s3://b/ --endpoint-url https://s3-accelerate.amazonaws.com

# Tune concurrency
aws configure set default.s3.max_concurrent_requests 50

# Manual multipart
aws s3api create-multipart-upload --bucket b --key big
```

## Interview Prep

**Mid**: "Why multipart."

**Senior**: "Optimize 100 GB upload."

**Staff**: "Global ingestion architecture."

## Next Topic

→ [T07 — S3 Event Notifications & Triggers](T07-Event-Notifications.md)
