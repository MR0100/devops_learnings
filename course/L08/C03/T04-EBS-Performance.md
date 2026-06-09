# L08/C03/T04 — EBS Types (gp3, io2, st1, sc1) and Performance

## Learning Objectives

- Pick EBS type for workload
- Tune for IOPS / throughput

## EBS Volume Types

| Type | Media | Max IOPS | Max Throughput | $/GB/mo | Use |
|---|---|---|---|---|---|
| gp3 | SSD | 16,000 | 1,000 MB/s | $0.08 | Default; balanced |
| gp2 | SSD | 16,000 | 250 MB/s | $0.10 | Legacy; replace with gp3 |
| io2 Block Express | SSD | 256,000 | 4,000 MB/s | $0.125 + IOPS | Critical DB |
| io2 | SSD | 64,000 | 1,000 MB/s | $0.125 + IOPS | Critical DB |
| io1 | SSD | 64,000 | 1,000 MB/s | $0.125 + IOPS | Legacy io |
| st1 | HDD | low | 500 MB/s seq | $0.045 | Big data, logs |
| sc1 | HDD | very low | 250 MB/s seq | $0.015 | Cold |
| standard | HDD | low | low | $0.05 | Legacy magnetic |

Pricing varies by region; check current.

## gp3 (Recommended Default)

- 3000 IOPS base; +$0.005/IOPS-month for more (up to 16k)
- 125 MB/s base throughput; +$0.04/MBps-month for more (up to 1000)
- Independent IOPS and throughput (vs gp2 linked to size)

Best general-purpose. Replace gp2.

```bash
aws ec2 modify-volume --volume-id vol-xxx --volume-type gp3 --iops 5000 --throughput 250
```

## gp2 (Legacy)

3 IOPS/GB; min 100, max 16k.
- 100 GB: 300 IOPS
- 1000 GB: 3000 IOPS

Burst up to 3000 IOPS using credits.

Migrate to gp3 (cheaper + decoupled IOPS).

## io2 Block Express

For latency-critical DBs:
- 1000 IOPS/GB (up to 256k)
- Sub-ms latency
- 99.999% durability

Used for SAP HANA, large Oracle/SQL Server.

## st1 / sc1 (HDD)

For sequential workloads:
- Big data (Hadoop)
- Log processing
- Backups

Cheap; not for random I/O (low IOPS).

## Performance Math

### IOPS
Operations per second. Each I/O up to 256 KB (for SSD).

App needs N IOPS at I/O size S: throughput = N × S.

E.g., 10k IOPS × 64 KB = 640 MB/s. Volume must support.

### Throughput
Bytes per second.

Some apps throughput-bound (analytics scans); others IOPS-bound (OLTP).

### Latency
- SSD: sub-ms
- io2 Block Express: lowest (microseconds)
- HDD: ms

## Instance Bandwidth

EBS bandwidth limited by instance:
- m6i.large: 10k IOPS / 600 MB/s max EBS
- m6i.4xlarge: 20k IOPS / 1.25 GB/s
- m6i.16xlarge: 80k IOPS / 5 GB/s

Big volume + small instance: bottleneck at instance.

## Multi-Volume

For more aggregate IOPS / throughput: stripe (RAID 0) multiple volumes.

E.g., 4× gp3 each at 3000 IOPS = 12k IOPS aggregate (instance permitting).

Care: snapshot coordination (multi-volume snapshots).

## Instance Store

NVMe SSD on host:
- Fastest (microseconds)
- 100s of thousands IOPS
- 10+ GB/s
- BUT: ephemeral; lost on stop/terminate
- Use: caches, scratch, ephemeral DB replicas

Instance types with attached: i3, i4i, m6id, c6id.

## Snapshots

Point-in-time backup; incremental; stored in S3.

```bash
aws ec2 create-snapshot --volume-id vol-xxx --description "daily"
```

Restore: create new EBS from snapshot.

For point-in-time fleet: use AWS Backup; coordinates multi-volume.

## Encryption

KMS-encrypted:
- At rest
- In transit between EBS infra and instance
- Snapshots also encrypted

Account-level default: enable.

Re-encrypt to different key: copy volume.

## Optimized for IOPS or Throughput

| Workload | Choice |
|---|---|
| OLTP DB (random small reads) | io2 Block Express |
| Analytics (sequential scans) | st1 or gp3 high throughput |
| Web app (small mostly cached) | gp3 default |
| Log writes | st1 |
| Cold archives | sc1 |

## Burst (gp2 specific)

gp2 < 1000 GB: burst to 3000 IOPS using credits.
- 100 GB: 300 IOPS baseline; burst to 3000 for 30 minutes
- Then throttle to 300

For spiky: burst saves.
For sustained: bigger volume or gp3.

Monitor `BurstBalance` metric.

## Monitor

CloudWatch:
- VolumeReadOps / WriteOps (IOPS)
- VolumeReadBytes / WriteBytes
- VolumeQueueLength (saturation indicator)
- VolumeIdleTime
- BurstBalance (gp2)

Alert on:
- Queue length high (waiting for IO)
- BurstBalance low (about to throttle)

## Performance Tuning Checklist

For slow DB on EBS:
1. Instance type? (check EBS bandwidth limit)
2. Volume type? (io2 for crit)
3. IOPS provisioned? (above app needs)
4. Throughput? (check MB/s)
5. Queue length? (yes → saturated)
6. Multi-volume RAID? (for >limits)
7. Filesystem tuning? (block size, mount options)

## Resize

Grow online:
```bash
aws ec2 modify-volume --volume-id vol-xxx --size 100 --iops 6000 --throughput 250
# Then in OS:
sudo growpart /dev/xvdf 1
sudo resize2fs /dev/xvdf1
```

Shrink: not supported. Create new smaller; copy data.

## Lifecycle

Data Lifecycle Manager (DLM):
- Daily snapshot
- Cross-region copy weekly
- Retention 30 days
- Auto-delete older

## Cost Comparison

For 500 GB DB volume:
- gp2: 500 × $0.10 = $50/mo (with 1500 IOPS limit)
- gp3 (3000 IOPS base): 500 × $0.08 = $40/mo
- gp3 (10000 IOPS): $40 + (7000 × $0.005) = $75/mo
- io2 (10000 IOPS): 500 × $0.125 + 10000 × $0.065 = $712.50/mo

gp3 best for most.

## Common Mistakes

- gp2 in 2025 (use gp3)
- Over-provisioned IOPS (paying for unused)
- Volume saturated; throughput pegged
- Snapshot bandwidth interferes with prod IO
- Big volume on tiny instance (bottlenecked)

## Best Practices

- Default gp3
- Monitor saturation
- DLM for backups
- Encrypt all
- Tag for cost tracking

## Quick Refs

```bash
# Describe
aws ec2 describe-volumes --volume-ids vol-xxx

# Modify
aws ec2 modify-volume --volume-id vol-xxx --volume-type gp3 --iops 5000

# Detach / attach
aws ec2 detach-volume --volume-id vol-xxx
aws ec2 attach-volume --volume-id vol-xxx --instance-id i-xxx --device /dev/sdf
```

## Interview Prep

**Mid**: "gp2 vs gp3."

**Senior**: "DB IOPS saturated — diagnose."

**Staff**: "Storage architecture for 100 TB DB."

## Next Topic

→ [T05 — Spot, Savings Plans, Reserved Instances](T05-Pricing.md)
