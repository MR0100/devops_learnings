# L02/C05 — Filesystems & Storage

## Chapter Overview

Storage is where most production data lives. Understanding filesystems, LVM, RAID, and NFS is the difference between a 30-minute recovery and a 30-day rebuild.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-Block-Devices.md) | Block Devices, Partitions, Mounting | 1 hr |
| [T02](T02-LVM.md) | LVM (Physical Volumes, Volume Groups, Logical Volumes) | 1.5 hr |
| [T03](T03-Filesystems-Compared.md) | ext4 vs XFS vs Btrfs vs ZFS | 1.5 hr |
| [T04](T04-RAID.md) | RAID Levels & mdadm | 1 hr |
| [T05](T05-Network-Filesystems.md) | NFS, SMB, Network Filesystems | 1 hr |

## Key Concepts

### Block Devices
- `/dev/sd*`, `/dev/nvme*`, `/dev/vd*` (virtio)
- Use `lsblk` for tree view, `blkid` for UUIDs
- `parted`, `gdisk`, `fdisk` for partition tables (GPT preferred)
- Mount: `/etc/fstab` for persistent

### Filesystems
| FS | Strength | Weakness |
|---|---|---|
| ext4 | Mature, fast, well-understood | Limited features |
| XFS | Excellent for large files, parallel I/O | Cannot shrink |
| Btrfs | Snapshots, COW, subvolumes | Reputation for issues at scale |
| ZFS | Industrial-strength, snapshots, RAID-Z | Not in mainline kernel (license); high RAM use |

### LVM Layers
```
Physical Volumes (PVs)  → physical disks
       ↓
Volume Group (VG)        → pool of PVs
       ↓
Logical Volumes (LVs)    → carved out of VG
       ↓
Filesystems
```

Operations:
- `pvcreate /dev/sdb`
- `vgcreate vg0 /dev/sdb /dev/sdc`
- `lvcreate -L 100G -n data vg0`
- `lvextend -L +50G /dev/vg0/data` (then `resize2fs` / `xfs_growfs`)
- LVM snapshots for point-in-time backups

### RAID
| Level | Min Disks | Redundancy | Use Case |
|---|---|---|---|
| 0 | 2 | None | Speed, ephemeral data |
| 1 | 2 | Mirror | Boot, critical OS |
| 5 | 3 | 1-disk failure | Bulk storage (rebuild expensive) |
| 6 | 4 | 2-disk failure | Large arrays |
| 10 | 4 | Mirror + stripe | Databases, IOPS |

Software RAID via `mdadm`. Most cloud setups skip RAID (EBS handles redundancy at the SAN layer).

### NFS
- v3 (UDP/TCP, stateless) vs v4 (TCP, stateful, secure)
- `exportfs`, `/etc/exports`, mount options (`hard`, `soft`, `nfsvers=4.1`, `nconnect=`)
- Common production: NFSv4.1 with Kerberos

## Cloud Storage

| AWS | Azure | GCP |
|---|---|---|
| EBS gp3/io2 | Premium SSD | Persistent Disk SSD |
| EFS / FSx | Azure Files | Filestore |
| S3 / Glacier | Blob / Archive | GCS |

Covered deeper in L08 (AWS).

## Interview Themes

- "Walk me through extending a filesystem online."
- "Explain LVM snapshots."
- "Why is XFS preferred for large file workloads?"
- "Diagnose: NFS mount is hanging."
