# L07/C05/T03 — File Storage (EFS, Filestore, Azure Files)

## Learning Objectives

- Use shared filesystems in cloud
- Pick when needed

## File Storage

Shared filesystem accessible by many hosts simultaneously. Like NFS in the cloud.

## When You Need It

- Multiple instances read/write same data
- Container persistent volume across pods
- Legacy app expecting POSIX FS
- Shared scratch space

## When You Don't

- Single host (use EBS — cheaper, faster)
- App can use object storage (S3) — usually preferred
- Database (use block; FS not optimized)

Default to S3 if your app can. File storage is fallback for unfittables.

## EFS (AWS)

NFSv4 protocol. Auto-scaling; per-GB pricing.

```bash
# Mount
sudo mount -t nfs4 fs-xxxx.efs.us-east-1.amazonaws.com:/ /mnt/efs
```

Storage tiers:
- Standard: $0.30/GB/mo
- Standard-IA: $0.025/GB/mo (90 days no access → auto-transition)
- One Zone: $0.16/GB/mo (one AZ; cheaper)
- One Zone-IA: $0.0133/GB/mo

Throughput:
- Bursting: scales with size
- Provisioned: pay for specific MB/s
- Elastic (default): scales with workload

## FSx for Lustre (AWS)

High-perf parallel FS for HPC, ML training:
- Hundreds of GB/s throughput
- Linked with S3 (lazy load)
- Pay per GB + throughput tier

## FSx for Windows File Server / NetApp ONTAP / OpenZFS
Specialized; SMB protocol, advanced features. Less common.

## Filestore (GCP)

NFS-based; service tiers:
- Basic HDD ($0.20/GB)
- Basic SSD ($0.30)
- Zonal ($0.35)
- Enterprise (HA)
- High Scale (HPC)

## Azure Files

SMB or NFS. Tiers:
- Premium (SSD)
- Standard (HDD)

## EFS Performance

| Workload | Standard | Provisioned |
|---|---|---|
| Throughput baseline | scales with size | you pay for max |
| IOPS | up to 35k | higher with provisioned |
| Latency | low for small files | same |

For NFS: many small files = slow due to round-trips. Cache locally if possible.

## EFS Access

- VPC mount targets (one per AZ)
- Security groups control access
- IAM (newer): authenticate clients
- POSIX UID/GID for FS permissions

EFS Access Points: enforced UID/path/quota per mount.

## EFS in EKS

EFS CSI driver:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs-sc
provisioner: efs.csi.aws.com

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: efs-pvc
spec:
  storageClassName: efs-sc
  accessModes: [ReadWriteMany]
  resources:
    requests:
      storage: 10Gi
```

ReadWriteMany: multiple pods can mount simultaneously. Big advantage over EBS (1-pod limit).

## Pricing Models

EFS bills:
- Per GB stored
- Per GB transferred (bursting only)
- Provisioned throughput separately

For 100 GB:
- Standard: $30/mo
- IA (90+ day cold): $2.50/mo
- One Zone: $16/mo

For large datasets accessed sometimes: IA dominant.

## Backup

EFS backups via AWS Backup. Restore creates new EFS or restore in place.

## Performance Tuning

- Mount with `nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport`
- Larger I/O batches better
- Sequential > random for NFS
- Local cache (cachefilesd) for frequently-read

## Common Use Cases

- WordPress / CMS where many web instances share user-uploaded content
- ML training data shared across worker nodes
- Build artifacts shared across CI agents
- Container volume across replicas (rare; usually use S3 or DB)

## Performance Reality

EFS slower than EBS:
- Latency: ms vs sub-ms
- Throughput: scales with size; can lag EBS
- Small files: slow (NFS overhead)

For DB: don't use EFS. EBS or RDS.
For HPC: FSx Lustre.

## When To Avoid

- Database
- Latency-critical
- Small file heavy
- High IOPS need

Use EBS or block storage; or app-level state.

## File Storage Alternatives

For shared state, prefer:
- S3 if read/write decoupled
- Redis if low latency
- DB if structured
- Queue if ordered events

File storage = legacy or specialty.

## Common Mistakes

- EFS as DB volume (slow + expensive)
- Many small files (NFS round-trips kill perf)
- Bursting throughput exhausted (slow then)
- No backup

## Monitoring

- TotalIOBytes
- PercentIOLimit
- BurstCreditBalance
- PermittedThroughput

Alert if balance trending to 0.

## Migration

From on-prem NFS:
- DataSync (AWS) for copy
- Direct mount (slower; for live)

To EFS, expect re-tuning.

## Interview Prep

**Mid**: "EFS vs EBS — when each."

**Senior**: "WordPress on K8s — storage strategy."

**Staff**: "Shared state for stateful workloads — alternatives to FS."

## Next Topic

→ Move to [L07/C06 — Database Family](../C06/README.md)
