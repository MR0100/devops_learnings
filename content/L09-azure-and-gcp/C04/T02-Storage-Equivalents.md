# L09/C04/T02 — Storage Equivalents

## Learning Objectives

- Map storage across clouds
- Pick by use case

## Object Storage

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | S3 | Cloud Storage (GCS) | Blob Storage |
| Bucket-level | yes | yes | Container in Storage Account |
| Global naming | yes | yes | unique per Storage Account |
| Versioning | yes | yes | yes |
| Lifecycle | yes | yes | yes |
| Lock / WORM | Object Lock | Bucket Lock | Immutable Blob |
| Public access block | yes | yes | yes |

## Storage Classes

| Tier | AWS | GCP | Azure |
|---|---|---|---|
| Hot | Standard | Standard | Hot |
| 30d | Standard-IA | Nearline | Cool |
| 90d | One Zone-IA | Coldline | Cold |
| Archive | Glacier Instant | Archive | Archive |
| Deep | Glacier Deep | Archive | Archive |

Pricing patterns similar.

## Block Storage

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | EBS | Persistent Disk | Managed Disk |
| High-perf SSD | io2 Block Express | Hyperdisk Extreme | Premium SSD v2 |
| Standard SSD | gp3 | pd-ssd / pd-balanced | Standard SSD |
| HDD | st1, sc1 | pd-standard | Standard HDD |
| Multi-attach | io2 multi-attach | Hyperdisk Balanced (some) | Shared Disks |
| Snapshot | yes | yes | yes |
| Encryption | yes | yes | yes |

## File Storage

| | AWS | GCP | Azure |
|---|---|---|---|
| NFS | EFS | Filestore | Azure Files (NFS) |
| SMB | FSx for Windows | Filestore Enterprise | Azure Files (SMB) |
| HPC | FSx Lustre | Filestore High Scale | Azure HPC Cache |
| Enterprise | FSx NetApp ONTAP | NetApp Volumes | NetApp Files |

## Hybrid

| | AWS | GCP | Azure |
|---|---|---|---|
| Cache to cloud | Storage Gateway | Storage Transfer | Data Box Gateway |
| Edge to cloud | DataSync | Transfer Service | Data Box |
| Physical | Snowball | Transfer Appliance | Data Box |

## Backup

| | AWS | GCP | Azure |
|---|---|---|---|
| Backup mgr | AWS Backup | Backup and DR | Azure Backup |
| EC2 snapshot | EBS Snapshot | PD Snapshot | Disk Snapshot |
| Cross-region | yes | yes | yes |

## Cost (per GB/mo)

| Tier | AWS S3 | GCP GCS | Azure Blob |
|---|---|---|---|
| Hot | $0.023 | $0.020 | $0.021 |
| 30d | $0.0125 | $0.010 | $0.010 |
| 90d | $0.004 | $0.004 | $0.0036 |
| Archive | $0.001-0.004 | $0.0012 | $0.0033 |

Standard pricing varies; check live.

## Egress (per GB)

- AWS: $0.05-0.09
- GCP: $0.08-0.12 (Premium); $0.05+ (Standard)
- Azure: $0.05-0.087

For data heavy: significant.

## API Compatibility

- S3 API: many tools support
- GCS: native + interoperability mode (S3-like)
- Azure Blob: native; ADLS Gen2

For cross-cloud: tools speak S3 commonly.

## Object Storage Patterns

### Static Hosting
- S3 + CloudFront
- GCS + Cloud CDN
- Blob + Azure CDN / Front Door

### Data Lake
- S3 (Lake Formation)
- GCS (Data Lake Storage)
- ADLS Gen2 (hierarchical)

### Backup
- All support lifecycle to archive
- Cross-region replication

## Block Storage Patterns

### Database
- io2 / Hyperdisk / Premium SSD v2 for high IOPS
- gp3 / pd-ssd / Premium SSD for general

### Bulk Storage
- st1 / pd-standard / Standard HDD

## File Storage Patterns

### Shared App State
- EFS / Filestore / Azure Files
- For VM clusters needing NFS

### HPC
- FSx Lustre / Filestore High Scale / HPC Cache

## Performance Tiers

### Object (sequential read)
- S3: high throughput, multipart upload
- GCS: similar
- Blob: similar

For: parallel uploads.

### Block (IOPS)
- io2 Block Express: 256K IOPS
- Hyperdisk Extreme: 350K IOPS
- Premium SSD v2: high

For high IOPS: latest tier.

### File
- Cluster-throughput driven
- HPC tiers scale to GB/s

## Encryption

All: at rest by default.
- AWS: KMS / SSE-S3 / SSE-C
- GCP: Google-managed / CMEK / CSEK
- Azure: Microsoft-managed / CMK / customer-provided

For compliance: CMK.

## Cross-Region Replication

All support:
- AWS: S3 CRR
- GCP: Multi-region / dual-region buckets
- Azure: GRS / RA-GZRS

For DR.

## Compliance

- HIPAA, PCI, FedRAMP: supported across all
- Sovereign clouds: AWS GovCloud, Azure Gov, GCP Assured Workloads

## Best Practices

- Lifecycle policies (auto-tier)
- Versioning + soft delete
- Encryption with CMK if regulated
- Private Endpoints (no Internet)
- Public access block on
- Multi-region replication for critical

## Common Mistakes

- Public bucket (data leak)
- No lifecycle (cost grows)
- Single-AZ for critical (no HA)
- Cross-cloud replication (egress cost)
- No backup of data (object stores aren't backup)

## Quick Refs

```
Object: S3 / GCS / Blob
Block: EBS / PD / Managed Disk
File: EFS / Filestore / Azure Files
Archive: Glacier Deep / Archive / Archive
HPC: FSx Lustre / Filestore High Scale / HPC Cache
```

## Interview Prep

**Junior**: "Map storage."

**Mid**: "When each tier."

**Senior**: "Storage cost optimization."

**Staff**: "Multi-region storage architecture."

## Next Topic

→ [T03 — Database Equivalents](T03-Database-Equivalents.md)
