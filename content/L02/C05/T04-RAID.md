# L02/C05/T04 — RAID Levels & mdadm

## Learning Objectives

- Compare RAID levels on redundancy, capacity, and performance and pick one per workload
- Build, monitor, and recover a software array with `mdadm`
- Explain rebuild risk, the RAID5 write hole, and why cloud setups often skip RAID

## What RAID Is (and Isn't)

RAID (Redundant Array of Independent Disks) combines multiple disks into one logical device for **redundancy**, **performance**, or both. It survives *disk* failure — it is **not a backup**. RAID won't save you from `rm -rf`, ransomware, filesystem corruption, or a fire; it only tolerates hardware failure of member disks.

Two implementations:
- **Software RAID** — the kernel does it (`md` / `mdadm` on Linux). Portable, free, observable, no special hardware.
- **Hardware RAID** — a controller card with battery-backed cache. Offloads parity but ties the array to that controller model.

## RAID Levels

| Level | Min disks | Usable capacity | Survives | Read | Write | Use case |
|---|---|---|---|---|---|---|
| 0 (stripe) | 2 | 100% | nothing | fast | fast | Scratch, ephemeral, speed-only |
| 1 (mirror) | 2 | 50% | 1 disk | fast | ~1 disk | Boot, OS, critical small volumes |
| 5 (stripe+parity) | 3 | (n−1)/n | 1 disk | fast | slow (RMW) | Bulk storage, read-heavy |
| 6 (dual parity) | 4 | (n−2)/n | 2 disks | fast | slower | Large arrays, long rebuilds |
| 10 (1+0) | 4 | 50% | 1 per mirror | fast | fast | Databases, high IOPS |

```
RAID 0  stripe:   A1 A2 | A3 A4        no redundancy, max speed
RAID 1  mirror:   A1 A1 | A2 A2        full copy on each disk
RAID 5  parity:   A1 A2 Ap | Bp B1 B2  parity rotates; 1-disk loss OK
RAID 6  2 parity:  ... Ap Aq ...        2-disk loss OK
RAID 10 mirror+stripe: (A1 A1)(A2 A2)   stripe across mirrors
```

### Parity, write penalty, and the write hole

RAID 5/6 compute parity (XOR) so a missing disk can be reconstructed. The cost is a **write penalty**: a small write becomes read-old-data + read-old-parity + write-new-data + write-new-parity (4+ I/Os). The **write hole** is the danger that a power loss mid-stripe leaves data and parity inconsistent; mitigate with a journal/bitmap (`mdadm --consistency-policy`), a UPS, or BBU on hardware controllers.

### Rebuild risk — why RAID 5 is out of favor for big disks

Rebuilding RAID 5 reads **every block of every surviving disk**. On multi-TB drives that's hours-to-days of full-disk stress, and a second failure or even an unrecoverable read error (URE) during rebuild loses the array. With large drives, RAID 6 (or RAID 10) is the responsible choice.

## mdadm — Building an Array

```bash
# Create a RAID 5 across 3 disks
mdadm --create /dev/md0 --level=5 --raid-devices=3 /dev/sd{b,c,d}

# RAID 10 across 4 disks
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd{b,c,d,e}

# Then treat /dev/md0 as one block device:
mkfs.xfs /dev/md0
mount /dev/md0 /data
```

Persist the array so it assembles at boot:

```bash
mdadm --detail --scan >> /etc/mdadm/mdadm.conf   # (or /etc/mdadm.conf on RHEL)
update-initramfs -u                              # Debian/Ubuntu
```

## Monitoring and Status

```bash
cat /proc/mdstat                 # live status + rebuild progress bar
mdadm --detail /dev/md0          # state, devices, sync status
mdadm --monitor --scan --daemonise --mail=ops@example.com   # alert on failure
```

```
# /proc/mdstat during a rebuild
md0 : active raid5 sdd[3] sdc[1] sdb[0]
      209584128 blocks super 1.2 level 5, 512k chunk
      [3/2] [UU_]                       # _ = missing/rebuilding member
      [===>.................]  recovery = 18.4% (...) finish=42.1min
```

`[UU_]` means two members up, one down/rebuilding. `[UUU]` is healthy.

## Replacing a Failed Disk

```bash
# 1. Mark the failed disk and remove it from the array
mdadm /dev/md0 --fail /dev/sdc --remove /dev/sdc

# 2. Physically swap the drive, partition it to match, then add it back
mdadm /dev/md0 --add /dev/sdc

# 3. Watch the rebuild
watch cat /proc/mdstat
```

The array stays **online and degraded** throughout — that's the whole point of redundancy. Keep a **hot spare** so rebuild starts automatically:

```bash
mdadm --create /dev/md0 --level=6 --raid-devices=4 --spare-devices=1 /dev/sd{b,c,d,e,f}
```

Run periodic **scrubs** to catch bad blocks before a rebuild needs them:

```bash
echo check > /sys/block/md0/md/sync_action
cat /sys/block/md0/md/mismatch_cnt
```

## RAID + LVM, and the Cloud Reality

A common production stack is **mdadm RAID → LVM → filesystem**: RAID gives redundancy, LVM gives flexible resizing, the filesystem sits on top. You can also reverse them, but RAID-under-LVM is the usual order.

In the cloud, **you usually don't run RAID at all**. EBS, Persistent Disk, and Azure Managed Disks already replicate at the storage backend (the SAN/distributed layer), so mirroring on top is redundant cost. RAID 0 across volumes is occasionally used purely for throughput/IOPS aggregation, and you grow capacity by resizing the managed volume — not by adding parity disks. Reach for mdadm on bare metal and on-prem, rarely in IaaS.

## Common Mistakes

- **Treating RAID as backup.** It tolerates disk failure only — keep real, off-host backups.
- **RAID 5 on large modern drives.** URE-during-rebuild and long rebuild windows make a second failure likely; use RAID 6 or 10.
- **No monitoring.** A degraded array runs silently until the *second* disk dies; run `mdadm --monitor` with email/alerts.
- **Forgetting to persist the config** (`mdadm.conf` + initramfs) so the array doesn't assemble after reboot.
- **Ignoring the write hole** on RAID 5/6 without a UPS, bitmap journal, or BBU.

## Best Practices

- Choose by need: RAID 1 for OS/boot, RAID 10 for databases/IOPS, RAID 6 for large bulk arrays; avoid RAID 5 on big disks.
- Always configure a hot spare and `mdadm --monitor` alerting; test that alerts actually fire.
- Schedule periodic scrubs (`check`) to surface latent bad blocks before rebuild relies on them.
- Stack RAID → LVM → filesystem for redundancy plus flexible resizing.
- In the cloud, lean on the provider's replicated volumes; only use RAID 0 for throughput, never for durability.

## Quick Refs

```bash
# Create
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd{b,c,d,e}
mdadm --create /dev/md0 --level=6  --raid-devices=4 --spare-devices=1 /dev/sd{b,c,d,e,f}

# Persist
mdadm --detail --scan >> /etc/mdadm/mdadm.conf
update-initramfs -u

# Monitor
cat /proc/mdstat
mdadm --detail /dev/md0
mdadm --monitor --scan --daemonise --mail=ops@example.com

# Replace a failed disk
mdadm /dev/md0 --fail /dev/sdc --remove /dev/sdc
mdadm /dev/md0 --add /dev/sdc

# Scrub
echo check > /sys/block/md0/md/sync_action
cat /sys/block/md0/md/mismatch_cnt
```

## Interview Prep

**Junior**: "What does RAID protect against, and what doesn't it?"
- It protects against the failure of member disks (keeping the volume online); it does not protect against accidental deletion, corruption, malware, or site loss — that's what backups are for.

**Mid**: "RAID 5 vs RAID 10 — when do you pick each?"
- RAID 5 maximizes usable capacity for read-heavy bulk storage but has a write penalty and risky rebuilds; RAID 10 mirrors then stripes for high IOPS and fast, low-risk rebuilds, so it's the pick for databases despite costing 50% capacity.

**Senior**: "Why has RAID 5 fallen out of favor for large drives?"
- Rebuilds read every block of every surviving disk, which on multi-TB drives takes many hours of full-disk stress where a single unrecoverable read error or a second disk failure destroys the array — so RAID 6 or 10 is used instead.

**Staff**: "Walk through recovering a degraded mdadm array, and why you'd skip RAID in the cloud."
- Confirm with `/proc/mdstat`, `--fail`/`--remove` the bad disk, hot-swap and `--add` a matching replacement, let it rebuild online while the array serves degraded, and rely on a pre-configured hot spare and scrubs to reduce the window; in IaaS you skip RAID because EBS/PD/Managed Disks already replicate at the backend, so you resize managed volumes instead of paying for redundant parity, using RAID 0 only to aggregate throughput.

## Next Topic

→ [T05 — NFS, SMB, Network Filesystems](T05-Network-Filesystems.md)
