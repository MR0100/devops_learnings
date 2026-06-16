# L09/C02/T04 — Storage (GCS, Persistent Disk, Filestore)

## Learning Objectives

- Choose GCP storage
- Compare to AWS / Azure

## GCS (Cloud Storage)

= S3:
```bash
gcloud storage buckets create gs://my-bucket --location=us-central1
gcloud storage cp file.txt gs://my-bucket/
```

Globally unique bucket name.

## Storage Classes

- **Standard**: hot
- **Nearline**: 30+ days
- **Coldline**: 90+ days
- **Archive**: 365+ days

Retrieval costs increase with cold; storage decreases.

## Location Types

- **Region**: single region (e.g. us-central1)
- **Dual-region**: two regions (geo-redundant)
- **Multi-region**: continent (e.g. us, eu)

Higher level = HA + cost.

## Lifecycle

```json
{
  "lifecycle": {
    "rule": [
      {"action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
       "condition": {"age": 30}},
      {"action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
       "condition": {"age": 365}},
      {"action": {"type": "Delete"},
       "condition": {"age": 2555}}
    ]
  }
}
```

Auto-tier and delete.

## Object Versioning

```bash
gcloud storage buckets update gs://my-bucket --versioning
```

Each write creates version. Like S3.

## IAM + ACLs

- IAM: bucket-level (recommended)
- ACLs: per-object (legacy)

Uniform bucket-level access:
```bash
gcloud storage buckets update gs://my-bucket --uniform-bucket-level-access
```

Disables ACLs; IAM only. Cleaner.

## Signed URLs

```bash
gcloud storage sign-url gs://my-bucket/file.txt --duration=1h
```

For: temp access to private objects.

= S3 presigned URL.

## Encryption

At rest: Google-managed default.

CMEK (customer-managed via Cloud KMS):
```bash
gcloud storage buckets create gs://my-bucket --default-encryption-key=KMS_KEY
```

For: compliance / control.

## Object Lifecycle Hooks

- Pub/Sub on object create
- Cloud Functions trigger
- For: event-driven processing

```bash
gcloud storage buckets notifications create gs://my-bucket \
  --topic=my-topic --event-types=OBJECT_FINALIZE
```

## Retention Lock / Hold

```bash
gcloud storage buckets update gs://my-bucket --retention-period=365d
```

WORM. Can't delete during retention.

For: compliance.

## Persistent Disk (PD)

= EBS:
```bash
gcloud compute disks create my-disk \
  --zone=us-central1-a \
  --size=100GB \
  --type=pd-ssd
```

Types:
- **pd-standard**: HDD
- **pd-balanced**: balanced SSD
- **pd-ssd**: high perf SSD
- **pd-extreme**: extreme IOPS
- **hyperdisk**: customizable IOPS / throughput

## Hyperdisk

Newer:
- Separate provisioned IOPS / throughput
- Better economics for high perf
- Multi-attach (some types)

## PD Snapshots

```bash
gcloud compute snapshots create my-snap --source-disk=my-disk --source-disk-zone=us-central1-a
```

Incremental; cross-region replicable.

For: backup.

## Regional PD

```bash
gcloud compute disks create my-disk \
  --region=us-central1 \
  --replica-zones=us-central1-a,us-central1-b
```

Replicated across 2 zones. For HA.

## Filestore

= EFS / Azure Files:
```bash
gcloud filestore instances create my-fs \
  --zone=us-central1-a \
  --tier=BASIC_HDD \
  --file-share=name="data",capacity=1TB \
  --network=name="default"
```

NFS shared across VMs.

Tiers:
- Basic HDD
- Basic SSD
- Zonal (high perf)
- Regional (HA)
- Enterprise (HA + SMB)

## NetApp

Cloud NetApp Volumes:
- Premium NFS/SMB
- Multi-protocol
- Enterprise features

For: lift-and-shift, demanding workloads.

## Object vs Block vs File

```
GCS:      object (HTTP); S3-like
PD:       block (mounted); EBS-like
Filestore: file (NFS); EFS-like
```

## Data Transfer

### Storage Transfer Service
GCS ↔ S3, on-prem ↔ GCS.

### Transfer Appliance
Physical box for huge data.

### gsutil/gcloud
CLI parallel uploads.

## Performance

| | IOPS | Latency | Throughput |
|---|---|---|---|
| GCS | per object | tens of ms | high (parallel) |
| pd-ssd | high | ~1 ms | high |
| Hyperdisk | very high | <1 ms | very high |
| Filestore | per share | low ms | high |

## Costs

- GCS Standard: ~$0.02/GB/mo
- GCS Archive: ~$0.0012/GB/mo
- pd-ssd: ~$0.17/GB/mo
- pd-standard: ~$0.04/GB/mo
- Filestore: $0.16+/GB/mo

Egress: per GB out.

## Comparison

| GCP | AWS | Azure |
|---|---|---|
| GCS | S3 | Blob |
| PD | EBS | Managed Disk |
| Filestore | EFS | Files |
| Hyperdisk | io2 Block Express | Premium SSD v2 |
| Transfer Service | DataSync | Data Box / Migrate |

## Best Practices

- Multi-region GCS for critical
- Lifecycle policies
- CMEK if regulated
- Uniform bucket-level access
- Regional PD for HA
- Versioning on
- Pub/Sub on object events

## Common Mistakes

- ACLs (use IAM)
- No lifecycle (cost grows)
- pd-ssd everywhere
- No versioning (lost on accident)
- Public buckets

## Public Bucket Check

```bash
gcloud storage buckets get-iam-policy gs://my-bucket | grep allUsers
```

If allUsers: PUBLIC. Audit.

## Quick Refs

```bash
# GCS
gcloud storage buckets create / cp / rm
gcloud storage objects list

# PD
gcloud compute disks create / list
gcloud compute snapshots create

# Filestore
gcloud filestore instances create / list
```

## Interview Prep

**Junior**: "GCP storage types."

**Mid**: "Storage class lifecycle."

**Senior**: "Hyperdisk vs PD."

**Staff**: "Multi-region storage architecture."

## Next Topic

→ [T05 — Networking (VPC, Cloud Load Balancing, Cloud Armor)](T05-Networking.md)
