# L07/C05/T02 — Block Storage (EBS, Persistent Disk, Managed Disks)

## Learning Objectives

- Pick the right block storage
- Tune for IOPS and throughput

## Block Storage

Raw blocks; attach to one VM at a time (usually); like a hard drive.

OS sees it as `/dev/sdX`; formats with filesystem; mounts as POSIX FS.

## EBS (AWS)

Persistent block storage. Survives instance stop/terminate (depends on setting).

Volume types:

| Type | IOPS | Throughput | Use | $/GB/mo |
|---|---|---|---|---|
| gp3 (SSD) | up to 16k | 1 GB/s | general default | $0.08 |
| gp2 (older SSD) | 3-16k | up to 250 MB/s | older default | $0.10 |
| io2 Block Express | 256k | 4 GB/s | latency-critical DB | $0.125 + IOPS |
| io1 | 64k | 1 GB/s | legacy | similar |
| st1 (HDD) | low | 500 MB/s seq | big data, logs | $0.045 |
| sc1 (cold HDD) | very low | 250 MB/s seq | infrequent | $0.015 |

Default: gp3. Tune IOPS/throughput independently.

## Persistent Disk (GCP)

- pd-standard (HDD)
- pd-balanced (SSD-balanced)
- pd-ssd (high SSD)
- pd-extreme (extreme SSD)

Performance scales with size (small disks = low IOPS).

## Azure Managed Disks

- Standard HDD
- Standard SSD
- Premium SSD
- Premium SSDv2
- Ultra Disk

## Performance Model

| Type | Latency | IOPS | Throughput |
|---|---|---|---|
| HDD | ms | 100s | 200 MB/s |
| Standard SSD | sub-ms | 1000s | 500 MB/s |
| Premium SSD | sub-ms | 10000s | 1 GB/s |
| Extreme/io2 | sub-ms | 100k+ | 4 GB/s |
| NVMe local | microseconds | 1M+ | 12 GB/s |

For DB: SSD minimum. High-traffic: premium / io2.

## Sizing

Volume size determines max IOPS (often):
- AWS gp3: independent (purchase IOPS up to 16k)
- AWS gp2: 3 IOPS per GB; max 16k at 5333 GB
- AWS io2: max 1000 IOPS per GB

To get higher throughput, sometimes you must make volume larger. Check docs.

## Snapshots

Point-in-time backup. Incremental (first full; subsequent only changes). Stored in object storage (S3 internally).

```bash
aws ec2 create-snapshot --volume-id vol-xxx
```

Restore: create new EBS from snapshot. Different AZ OK.

Cross-region: copy snapshot to another region.

Retention: cost. Use Data Lifecycle Manager (DLM) for policies.

## Attach / Detach

One volume → one instance (except Multi-Attach for io1/io2).

```bash
aws ec2 attach-volume --volume-id vol-xxx --instance-id i-xxx --device /dev/sdf
```

OS sees device; mount:
```bash
mkfs.ext4 /dev/xvdf
mount /dev/xvdf /data
```

For new volume: format. For existing: just mount.

## Encryption

EBS volumes can be encrypted (KMS). Recommended; default-on can be configured at account level.

Transit also encrypted (within EBS infrastructure).

Encrypted snapshots required for encrypted volumes.

## Multi-Attach

io1/io2 can attach to multiple instances simultaneously. App must coordinate (clustered FS like GFS2 or app-level). Niche use case.

## Instance Store

NVMe SSD directly on host. NOT block service; tied to instance lifecycle.
- Fastest I/O (microseconds)
- Lost on stop/terminate
- Use: cache, tmp, scratch, ephemeral data

E.g., `i3en.2xlarge` has ~5 TB instance store.

## RAID

Stripe multiple EBS volumes for more aggregate IOPS/throughput. But:
- Snapshots become coordinated (use EBS Multi-Volume Snapshot)
- More complex
- Usually one large gp3 is enough

For HPC / big DB: RAID 0 across many volumes.

## Filesystem Choices

- ext4: general default
- XFS: large files; high throughput
- Btrfs / ZFS: features (snapshot, compression); use cautiously on EBS

## Resize

Grow volume online:
```bash
aws ec2 modify-volume --volume-id vol-xxx --size 100
# Then resize filesystem
sudo resize2fs /dev/xvdf      # ext4
sudo xfs_growfs /data         # XFS
```

Shrink: not supported. Create new smaller; copy.

## Costs

- Storage: per GB-month
- IOPS: extra for io1/io2 above base
- Throughput: gp3 includes 125 MB/s; charge more for more
- Snapshots: per GB-month of changed data
- Cross-AZ data: free (but I/O contention)

## Lifecycle

DLM policy:
- Daily snapshot
- Keep last 7
- Cross-region copy weekly
- Delete older

Saves money; ensures recoverability.

## Common Mistakes

- Over-provisioned IOPS (paying for unused)
- Single-AZ critical data (use snapshot/cross-region)
- gp2 when gp3 cheaper
- No backup
- Encrypted snapshots in one region only

## Detaching Procedure

1. Stop app writing
2. Unmount in OS
3. Detach via API
4. Attach elsewhere
5. Mount

For unclean: data loss risk. Always umount first.

## Monitoring

CloudWatch:
- VolumeReadOps, VolumeWriteOps (IOPS)
- VolumeReadBytes, VolumeWriteBytes (throughput)
- VolumeQueueLength (queued I/O — high = saturating)
- BurstBalance (gp2 credits)

Alert on saturation.

## Block vs Object vs File

| | Block | Object | File |
|---|---|---|---|
| Interface | Raw blocks | HTTP API | NFS / SMB |
| Mount | Yes (1 host) | No | Yes (many hosts) |
| Size | TB | EB | TB-PB |
| Latency | sub-ms | ms | ms |
| Use | DB, OS | Backup, lake | Shared FS |

EBS = block. S3 = object. EFS = file.

## Interview Prep

**Mid**: "EBS volume types — when each."

**Senior**: "DB IOPS saturated — diagnose."

**Staff**: "Storage strategy for 50 TB OLTP DB."

## Next Topic

→ [T03 — File Storage (EFS, Filestore, Azure Files)](T03-File-Storage.md)
