# L08/C05/T04 — S3 Performance & Request Patterns

## Learning Objectives

- Scale S3 throughput
- Avoid throttling

## Performance Targets

Per-prefix limits:
- 3500 PUT/COPY/POST/DELETE per second
- 5500 GET/HEAD per second

Per bucket: unlimited (sum across prefixes).

## Spreading Load

To exceed per-prefix limits: multiple prefixes:
```
data/server1/file1
data/server2/file1
data/server3/file1
```

Each `server*` prefix gets 3500/5500 RPS.

S3 auto-partitions and spreads internally; you don't manage.

## Multipart Upload

For large files (>100 MB recommended; required >5 GB).

- Split into parts (5 MB to 5 GB each; max 10,000 parts)
- Upload parts in parallel
- Faster total upload (parallelism)
- Resume on failure (resend only failed parts)

```bash
# Auto via CLI
aws s3 cp big.tar s3://b/big.tar
# Uses multipart if >8 MB by default

aws configure set default.s3.multipart_threshold 100MB
aws configure set default.s3.max_concurrent_requests 20
```

## Multipart Costs

- Each part = 1 PUT request
- Failed/abandoned parts: storage cost until cleanup
- Lifecycle: AbortIncompleteMultipartUpload after 7 days

## Transfer Acceleration

Upload via CloudFront edge POPs (closer to client) → forwarded to S3.

For distant clients: 50-500% faster.

```bash
aws s3api put-bucket-accelerate-configuration --bucket b --accelerate-configuration Status=Enabled

# Endpoint becomes b.s3-accelerate.amazonaws.com
aws s3 cp file.bin s3://b/file.bin --endpoint-url https://s3-accelerate.amazonaws.com
```

Costs extra: $0.04/GB.

Test before adopting: AWS S3 Speed Test.

## Range GET

Download portion:
```bash
aws s3api get-object --bucket b --key big.tar --range bytes=0-1048575 part1
```

For large files: parallel range GETs.

## CloudFront In Front

For repeated downloads (assets, videos):
- CloudFront caches at edge
- Origin (S3) hit once per cache miss
- Lower latency, less S3 load
- Cheaper than direct S3 egress at high volume

Configure origin = S3 bucket; cache behavior per content type.

## Origin Access Identity / Control

CloudFront → S3 should be private. Use OAC (Origin Access Control, newer) or OAI (Origin Access Identity, older).

S3 bucket policy: allow only OAC/OAI; block public.

## S3 Select

Query CSV / JSON / Parquet in objects without download:
```sql
SELECT s.country, s.total FROM s3object s WHERE s.year = 2024
```

```bash
aws s3api select-object-content --bucket b --key data.csv \
  --expression-type SQL \
  --expression "SELECT * FROM s3object WHERE _1 = 'x'" \
  --input-serialization '{"CSV": {}}' \
  --output-serialization '{"CSV": {}}' \
  output.csv
```

Saves data transfer; pushes filtering to S3.

For complex analytics: Athena (covered later).

## Cost

- $0.0008 per request (PUT/COPY/POST/LIST)
- $0.0004 per request (GET/SELECT/etc.)
- $0.005 per request for Glacier transitions

For high RPS: request cost dominates.

## Connection Reuse

Keep TCP connection alive; reduces TLS handshake cost.

SDKs do automatically.

## Parallelism

For many small files:
- Parallel uploads (CLI: `--max-concurrent-requests`)
- Spread across prefixes
- Async/concurrent code

For one big file: multipart parallel parts.

## Throttling

S3 returns 503 SlowDown if exceeding limits.

Strategies:
- Backoff + retry (SDKs handle)
- Spread to more prefixes
- Reduce concurrency
- File ticket if persistent (likely you need more partitions)

## Pre-Warming

For predictable spike: pre-warm bucket via gradual ramp.

Or use S3 Express (single-AZ; tens of thousands RPS per directory).

## S3 Express One Zone

High-perf bucket type (2023+):
- Single AZ
- 10× lower request latency
- Up to ~2M RPS per directory bucket
- More expensive per request

For: ML training, analytics, latency-critical.

Different bucket type; different API; doesn't replicate.

## Performance Tips

### Upload Path
```python
import boto3
from concurrent.futures import ThreadPoolExecutor

s3 = boto3.client("s3")

def upload(path):
    s3.upload_file(path, "my-bucket", path)

with ThreadPoolExecutor(max_workers=32) as ex:
    list(ex.map(upload, files))
```

### Read Heavy
- CloudFront if cacheable
- Use S3 Select to reduce data
- Range GET parts of large files
- Compress on disk (gzip)

### Latency-Sensitive
- Same region as compute
- VPC endpoint (lower hops)
- S3 Express for nanosecond/ms

## Logs as Use Case

App: 10k events/sec to S3.
- Don't write each event (10k PUT/sec = 27/day = $4400/mo just requests)
- Buffer in app; batch write (1000 events per file → 10 PUT/sec; $4.40)
- Or use Kinesis Firehose → batches automatically

Always batch writes.

## Read Caching

For frequently-read same objects:
- CloudFront (edge cache)
- ElastiCache (in-memory)
- App-level memoization

S3 itself doesn't cache (always reads from durable storage).

## Listing Performance

Listing big buckets: paginated; thousands per page.

For massive buckets: use S3 Inventory (daily report).

Athena query inventory: SELECT * FROM inventory WHERE last_modified > date.

## Anti-Patterns

- 100k tiny objects (overhead, request cost)
- Single huge prefix at limit (throttling)
- No multipart for large
- No CloudFront for distribution
- Range GETs sequential (parallel them)

## Best Practices

- Batch small writes
- Multipart for large
- CloudFront for distribution
- VPC endpoint for compute-side
- Compress data
- Right storage class
- S3 Inventory for huge buckets

## Monitoring

CloudWatch S3 metrics:
- BucketSizeBytes
- NumberOfObjects
- AllRequests
- 4xxErrors / 5xxErrors
- FirstByteLatency

Enable Request metrics (per prefix) for detail.

## Storage Lens

Org-wide S3 visibility:
- Usage trends
- Cost drivers
- Best practice violations

Free dashboard; advanced metrics paid.

## Backup / DR

Replication moves data; performance impact on source minimal (async).

For active-active: bidirectional replication.

## Common Mistakes

- Tiny files in cold storage (128 KB min fee)
- Not using multipart
- Listing huge bucket page by page
- Single concurrent upload
- No retry on 503

## Quick Refs

```bash
# Configure higher concurrency
aws configure set default.s3.max_concurrent_requests 50

# Multipart threshold
aws configure set default.s3.multipart_threshold 100MB
aws configure set default.s3.multipart_chunksize 50MB

# Sync many files
aws s3 sync ./local s3://b/path/ --storage-class STANDARD_IA
```

## Interview Prep

**Mid**: "S3 throughput limits."

**Senior**: "Optimize uploads at 100k/sec."

**Staff**: "Design S3 data lake for PB scale."

## Next Topic

→ [T05 — S3 Security (Block Public Access, Bucket Policies, KMS)](T05-S3-Security.md)
