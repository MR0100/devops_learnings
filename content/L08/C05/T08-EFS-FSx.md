# L08/C05/T08 — EFS & FSx (File Storage)

## Learning Objectives

- Choose between EFS and the FSx family
- Know when file storage beats EBS or S3

## The Three Storage Shapes

AWS storage falls into three access models:

- **Block (EBS)**: a raw volume attached to one instance (or a few with Multi-Attach io2). You put a filesystem on it. Lowest latency, single-AZ.
- **Object (S3)**: HTTP key/value store, virtually unlimited, 11 nines durability, no POSIX semantics.
- **File (EFS, FSx)**: a shared POSIX/SMB filesystem many clients mount at once over the network.

Reach for file storage when multiple instances or containers need to share the same files with normal filesystem semantics.

## Amazon EFS

Fully managed, elastic **NFSv4** filesystem for Linux.

- Multi-AZ by default (Regional) — mount targets per AZ; survives an AZ loss.
- Elastic capacity: grows and shrinks automatically, pay per GB used, no provisioning.
- Thousands of concurrent clients (EC2, ECS, EKS, Lambda).
- POSIX permissions, access points for per-app entry directories.

### EFS Storage Classes

- **Standard** and **One Zone** (single-AZ, cheaper, less resilient).
- **Infrequent Access (IA)** and **Archive** tiers, with **Lifecycle Management** moving cold files automatically. **Elastic Throughput** scales throughput to demand; **Provisioned Throughput** sets a fixed floor.

### When EFS

- Shared content/config across an Auto Scaling group or fleet
- Container persistent volumes shared across pods (EKS/ECS)
- Lambda needing a large shared writable filesystem
- CMS, web roots, home directories, shared build artifacts (Linux)

## Amazon FSx

Managed third-party / high-performance filesystems. Four flavors:

| FSx variant | Protocol | Best for |
|---|---|---|
| FSx for Windows File Server | SMB | Windows/AD shares, .NET apps, Windows home dirs |
| FSx for Lustre | Lustre (POSIX) | HPC, ML training, analytics; S3-linked scratch |
| FSx for NetApp ONTAP | NFS, SMB, iSCSI | Multiprotocol, snapshots, dedup, on-prem ONTAP migration |
| FSx for OpenZFS | NFS | ZFS features (snapshots, clones) on Linux at low latency |

### FSx for Windows File Server

- Native SMB shares with Active Directory integration and Windows ACLs.
- DFS namespaces, shadow copies, Multi-AZ option.
- The right answer whenever the question says "Windows file share" or "SMB."

### FSx for Lustre

- Massively parallel, sub-millisecond, hundreds of GB/s throughput.
- **Links to an S3 bucket**: lazy-loads objects on access and writes results back — ideal as a fast scratch layer over a data lake.
- Use for ML training, genomics, EDA, media rendering, and other HPC.

### FSx for NetApp ONTAP

- Multiprotocol (NFS + SMB + iSCSI) from one filesystem.
- Enterprise data management: snapshots, cloning, compression/dedup, SnapMirror replication.
- Best for lift-and-shift of on-prem NetApp workloads needing mixed clients.

### FSx for OpenZFS

- ZFS snapshots and instant clones with very low latency over NFS.
- Good for dev/test copies, content management, and Linux workloads wanting ZFS semantics.

## Choosing: EFS vs FSx vs EBS vs S3

| Need | Choose |
|---|---|
| One instance, lowest latency block volume | EBS |
| Unlimited objects, HTTP, web/static, backups, data lake | S3 |
| Shared Linux POSIX filesystem, elastic, multi-AZ | EFS |
| Windows/SMB + Active Directory share | FSx for Windows |
| HPC/ML scratch backed by S3, extreme throughput | FSx for Lustre |
| Multiprotocol + enterprise data management | FSx for NetApp ONTAP |
| ZFS snapshots/clones on Linux, low latency | FSx for OpenZFS |

Quick heuristics: many writers + POSIX → EFS; Windows → FSx Windows; HPC → FSx Lustre; single attach → EBS; objects/HTTP → S3.

## Mounting

```bash
# EFS via the helper (TLS, IAM auth supported)
sudo mount -t efs -o tls fs-0123456789abcdef0:/ /mnt/efs

# EFS via plain NFS
sudo mount -t nfs4 -o nfsvers=4.1 fs-0123456789abcdef0.efs.us-east-1.amazonaws.com:/ /mnt/efs

# FSx Windows (SMB) from Windows
net use Z: \\amznfsxxxxxx.corp.example.com\share
```

In Kubernetes, use the EFS CSI driver (`efs.csi.aws.com`) or the FSx CSI driver for persistent volumes.

## Performance Notes

- **EFS** throughput scales with usage (Elastic) or a provisioned floor; latency is higher than EBS because it is networked — fine for shared files, not for a database's hot data path.
- **FSx for Lustre** delivers the highest throughput/IOPS; size the deployment type (scratch vs persistent) to your durability and speed needs.
- File storage is for sharing and scale-out, not for replacing a local SSD on a latency-critical single instance.

## Security

- Encryption at rest (KMS) and in transit (TLS for EFS, SMB/Kerberos for FSx Windows).
- EFS access controlled by mount-target security groups, POSIX permissions, access points, and optional IAM authorization and file-system policies.
- FSx Windows uses Active Directory + Windows ACLs; ONTAP/OpenZFS use export policies and standard NFS/SMB controls.

## Common Mistakes

- Using EFS where EBS is right (single instance, latency-sensitive) — networked file latency hurts databases
- Choosing EFS for a Windows/SMB workload (EFS is NFS/Linux) — use FSx for Windows
- Forgetting a mount target in every AZ the clients run in (EFS mounts fail in AZs without one)
- Skipping lifecycle management, so cold data stays on the expensive Standard tier
- Treating FSx for Lustre scratch filesystems as durable — scratch does not replicate
- Mount-target security group not allowing NFS (2049) / SMB (445) from the clients

## Best Practices

- Match the model: EBS for single-attach block, S3 for objects, EFS/FSx for shared files
- EFS lifecycle policies + IA/Archive tiers to cut cost on cold data
- Use EFS access points to give each app a scoped root and enforce POSIX identity
- FSx for Lustre linked to S3 as a fast scratch layer over your data lake
- One mount target per AZ; reference client SGs rather than CIDRs
- Encrypt at rest and in transit; for FSx Windows, integrate with AWS Managed Microsoft AD
- Right-size FSx throughput/capacity and pick Multi-AZ for production Windows shares

## Quick Refs

```bash
# Create an EFS filesystem (elastic, encrypted)
aws efs create-file-system --encrypted --performance-mode generalPurpose \
  --throughput-mode elastic --tags Key=Name,Value=app-shared

# Add a mount target in an AZ
aws efs create-mount-target --file-system-id fs-0123456789abcdef0 \
  --subnet-id subnet-aaaa --security-groups sg-efs

# Apply a lifecycle policy (move to IA after 30 days)
aws efs put-lifecycle-configuration --file-system-id fs-0123456789abcdef0 \
  --lifecycle-policies TransitionToIA=AFTER_30_DAYS

# Create an FSx for Lustre filesystem linked to S3
aws fsx create-file-system --file-system-type LUSTRE --storage-capacity 1200 \
  --subnet-ids subnet-aaaa \
  --lustre-configuration ImportPath=s3://my-data-lake/,DeploymentType=SCRATCH_2
```

## Interview Prep

**Junior**: "EFS vs EBS vs S3 — what's the difference?"

**Mid**: "A fleet behind an ASG needs to share files — what do you use and why?"

**Senior**: "Pick the right FSx variant for a Windows AD share vs an ML training job."

**Staff**: "Design shared storage for an EKS platform spanning Linux and Windows workloads with cost tiering."

## Next Topic

→ Move to [L08/C06 — Databases on AWS](../C06/README.md)
