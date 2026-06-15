# L07/C05 — Storage Family

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Object-Storage.md) | Object Storage (S3, GCS, Blob Storage) | 1 hr |
| [T02](T02-Block-Storage.md) | Block Storage (EBS, Persistent Disk, Managed Disks) | 1 hr |
| [T03](T03-File-Storage.md) | File Storage (EFS, Filestore, Azure Files) | 0.5 hr |

## Object Storage

The default for unstructured data. Practically infinite scale, very high durability.

### Properties
- HTTPS REST API access
- Eventual consistency historically (S3 is now strongly consistent since 2020)
- Per-object metadata
- Versioning
- Lifecycle (tier or expire)
- Server-side encryption (SSE-S3, SSE-KMS, SSE-C, customer-managed)
- Event notifications (Lambda triggers, SQS, etc.)

### S3 Storage Classes

| Class | Use | Cost |
|---|---|---|
| Standard | Frequent access | $$$ |
| Intelligent-Tiering | Variable / unknown | $$ + per-1000-objects |
| Standard-IA | Infrequent (30d+) | $ |
| One Zone-IA | Single AZ, IA | $ |
| Glacier Instant | Archive, ms retrieval | ¢ |
| Glacier Flexible | Archive, mins-hrs retrieval | ¢¢ |
| Glacier Deep Archive | Archive, 12h+ retrieval | ¢ (cheapest) |

### Performance
- ~3500 PUT/s and ~5500 GET/s per *prefix* on S3
- Use prefixes to scale (object keys with diverse prefixes spread across partitions)
- Multipart upload for objects > 100 MB (parallelism)

### Cross-Region Replication
- Per-bucket or per-prefix rule
- Source and dest buckets must have versioning enabled
- Async; replication lag typically seconds

### Best Practices
- Block Public Access at account + bucket level
- Bucket policy + IAM (defense in depth)
- VPC Endpoint (Gateway, free) for in-VPC access
- Use AES-256 SSE at minimum; KMS for compliance
- S3 Object Lock for immutable backups (compliance, ransomware)
- Lifecycle: tier old objects, delete incomplete multipart uploads

## Block Storage

Mounted as a block device (looks like a disk).

### Types (AWS EBS)

| Type | IOPS | Throughput | Use |
|---|---|---|---|
| gp3 | 3000 baseline (provisionable to 16K) | 125 MB/s (to 1000) | General-purpose default |
| gp2 | scales with size (legacy) | scales with size | Legacy |
| io2 | up to 256K | high | High-IOPS DB |
| io2 Block Express | up to 256K | up to 4000 MB/s | Critical DB |
| st1 | low | high throughput | Big data, log warehouse |
| sc1 | low | low | Cold |

### Properties
- AZ-scoped (cannot mount cross-AZ)
- Multi-attach (io2) — limited use
- Snapshot to S3 (per-region, replicable cross-region)
- Encryption per volume (KMS)

### Common Mistakes
- Picking gp2 (use gp3, cheaper and faster)
- Snapshot retention unbounded (cost growth)
- Not encrypting (always encrypt by default)
- Using EBS for shared storage (use EFS instead)

## File Storage

NFSv4 / SMB protocols. Multiple instances can mount the same filesystem RW.

### EFS (AWS)
- Pay per GB stored + IO operations + throughput mode
- Throughput modes: bursting (default), elastic, provisioned
- Storage classes: Standard, IA (auto-tier old files)
- Use: shared content for ECS/EKS/EC2 fleets

### FSx (AWS)
- FSx for Windows: SMB
- FSx for Lustre: HPC
- FSx for NetApp ONTAP: enterprise NFS/SMB
- FSx for OpenZFS

### GCP Filestore, Azure Files
Equivalent NFS/SMB services.

### When File Storage
- Shared content (CMS uploads, ML datasets)
- Legacy apps expecting POSIX FS
- WORM compliance (NetApp SnapLock)
- Avoid for: high-throughput single-writer (use block); web assets (use object + CDN)

## Comparison Quick Reference

| | Object | Block | File |
|---|---|---|---|
| Access | HTTPS REST | OS block device | NFS/SMB |
| Shared mount | N/A (HTTPS) | One-instance (mostly) | Many-instance |
| Latency | ms (vs μs for disk) | sub-ms (NVMe) | ms |
| Scale | unlimited | per-volume size cap | huge |
| Cost | ¢/GB | ¢/GB/mo | ¢/GB/mo (higher) |
| Use | unstructured, large | DB, OS, app data | shared FS |

## Interview Themes

- "Compare object, block, file storage"
- "How does S3 achieve 11 nines of durability?" (replicas across AZs)
- "Why is S3 'eventual consistency' a thing — and now isn't?"
- "Choose storage for: logs / DB / shared ML dataset / video uploads"
- "Performance tune EBS gp3 for high-IOPS"
