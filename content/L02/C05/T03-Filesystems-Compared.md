# L02/C05/T03 — ext4 vs XFS vs Btrfs vs ZFS

## Learning Objectives

- Compare the four mainstream Linux filesystems on features, scaling, and failure modes
- Choose a filesystem for a given workload and justify it
- Create and tune each with `mkfs` and understand journaling vs copy-on-write

## The Short Version

| FS | Model | Strength | Weakness |
|---|---|---|---|
| ext4 | Journaling | Mature, fast, predictable, universally supported | Limited features; no built-in snapshots/checksums |
| XFS | Journaling | Excellent large-file & parallel I/O; scales to huge volumes | **Cannot shrink**; fewer repair options |
| Btrfs | Copy-on-write | Snapshots, subvolumes, checksums, compression, in-kernel | History of instability at scale; RAID5/6 still risky |
| ZFS | Copy-on-write | Industrial-grade integrity, snapshots, RAID-Z, send/recv | Out-of-tree (CDDL license); high RAM use (ARC) |

Rules of thumb: **ext4** is the safe default. **XFS** for big files and high parallel throughput (and the RHEL default). **Btrfs/ZFS** when you genuinely need snapshots, checksums, or built-in volume management — and you accept their operational weight.

## Journaling vs Copy-on-Write

This is the core architectural split.

**Journaling (ext4, XFS):** writes go to a journal first, then to their final location. After a crash, the journal is replayed to restore metadata consistency. ext4 journals metadata by default (`data=ordered`); full `data=journal` is safer but halves write throughput.

```
Journaling:   write → journal → checkpoint to final location → done
              crash recovery = replay the journal (metadata consistent)
```

**Copy-on-write (Btrfs, ZFS):** never overwrite live data. New data is written to free space, then a single atomic pointer swap publishes it. The old version stays intact until freed — which is exactly what makes snapshots and checksums cheap.

```
CoW:          write new block → update metadata tree → atomic root swap
              old blocks remain → free snapshots, no in-place corruption
```

CoW gives crash-consistency and instant snapshots but fragments more and can have higher latency under random overwrite (databases). Journaling is simpler and faster for in-place workloads.

## ext4 — the dependable default

```bash
mkfs.ext4 -L data /dev/vg0/data
mkfs.ext4 -m 1 /dev/sdb1               # reserve 1% for root (default 5%)
tune2fs -l /dev/sdb1                   # dump superblock info
tune2fs -m 0 /dev/sdb1                 # drop reserved blocks on a data disk
e2fsck -f /dev/sdb1                    # force a check (unmounted)
resize2fs /dev/vg0/data               # grow (online) or shrink (offline)
```

- Max filesystem: 1 EiB; max file: 16 TiB.
- Grows online, shrinks offline.
- `lazy_itable_init` makes `mkfs` instant but defers inode-table zeroing.
- Choice when you want boring, well-understood, fast, and recoverable.

## XFS — throughput and scale

```bash
mkfs.xfs -L data /dev/vg0/data
mkfs.xfs -d agcount=32 /dev/vg0/data  # more allocation groups → more parallelism
xfs_info /data                        # geometry
xfs_growfs /data                      # grow ONLY (pass mount point)
xfs_repair /dev/vg0/data              # repair (unmounted)
```

- **Allocation groups** let multiple CPUs allocate in parallel — why XFS shines on many-core, high-IOPS servers.
- Delayed allocation and extent-based layout keep large files contiguous → great sequential throughput.
- **Cannot shrink** — plan capacity carefully. Default on RHEL/CentOS and many database appliances.
- `xfs_repair` is your only fsck; keep backups because it can be aggressive.

## Btrfs — CoW with snapshots, in-kernel

```bash
mkfs.btrfs -L data /dev/sdb /dev/sdc  # multi-device natively
btrfs subvolume create /data/@home    # subvolumes
btrfs subvolume snapshot /data /data/.snap/2026-06-15
btrfs filesystem resize +50G /data    # grow or shrink online
btrfs scrub start /data               # verify checksums, self-heal if redundant
mount -o compress=zstd /dev/sdb /data # transparent compression
```

- Per-block checksums detect silent corruption; with redundancy it self-heals.
- Subvolumes + snapshots are first-class (Snapper, openSUSE rollback).
- **RAID 0/1/10 are considered stable; RAID 5/6 are still risky** ("write hole") — don't trust them for important data.
- Reputation for trouble at scale and on near-full disks; great for laptops, single-node servers, container hosts.

## ZFS — the integrity heavyweight

```bash
zpool create tank mirror /dev/sdb /dev/sdc     # pool + mirror vdev
zpool create tank raidz2 sdb sdc sdd sde       # RAID-Z2 (2-disk parity)
zfs create tank/data                           # dataset (acts like a FS)
zfs set compression=lz4 tank/data
zfs snapshot tank/data@before-upgrade          # instant snapshot
zfs send tank/data@snap | ssh host zfs recv backup/data   # replication
zpool status ; zpool scrub tank                # health + integrity scrub
```

- End-to-end checksums, self-healing, RAID-Z without the RAID5 write hole, native snapshots, send/receive replication.
- The **ARC** cache uses lots of RAM (rule of thumb ~1GB per TB; ECC RAM recommended).
- **Not in the mainline kernel** — CDDL license conflicts with GPL; installed as a DKMS/out-of-tree module. This is the headline "weakness."
- Choice for storage servers, NAS, and anywhere data integrity is paramount and you can give it RAM.

## Picking One

| Workload | Pick | Why |
|---|---|---|
| General server, "just works" | ext4 | Mature, fast, easy recovery |
| Large files, many cores, high IOPS, RHEL | XFS | Parallel allocation, extent layout |
| Need snapshots/rollback on a single node | Btrfs | In-kernel CoW + subvolumes |
| Storage server / NAS, integrity-critical | ZFS | Checksums, self-heal, RAID-Z, replication |
| Database (in-place random writes) | ext4 / XFS | Journaling avoids CoW fragmentation; pair with LVM for snapshots |

## Common Mistakes

- **Choosing XFS then needing to shrink.** XFS has no shrink path — you'd have to back up, recreate smaller, restore.
- **Trusting Btrfs RAID5/6** for important data — the write hole is unresolved.
- **Running ZFS without enough RAM** (or without ECC) and blaming ZFS for memory pressure.
- **Passing the device to `xfs_growfs`** instead of the mount point.
- **Assuming filesystem snapshots are backups** — they're on the same disks; you still need off-host copies (ZFS `send` / tar of an LVM snapshot).

## Best Practices

- Default to **ext4**; reach for XFS on big-file/high-parallel or RHEL boxes.
- Use **Btrfs/ZFS** only when their features earn their operational cost, and scrub on a schedule.
- Keep databases on journaling FS (ext4/XFS) and get snapshots from LVM or the storage layer.
- Always pair a filesystem choice with a tested backup/restore, not just snapshots.
- Mount with `noatime`; for ZFS/Btrfs enable compression (`lz4`/`zstd`) — it's usually a net win.

## Quick Refs

```bash
# ext4
mkfs.ext4 -L data /dev/vg0/data
tune2fs -l /dev/sdb1 ; resize2fs /dev/vg0/data ; e2fsck -f /dev/sdb1

# XFS
mkfs.xfs -L data /dev/vg0/data
xfs_info /data ; xfs_growfs /data ; xfs_repair /dev/vg0/data   # grow only

# Btrfs
mkfs.btrfs -L data /dev/sdb
btrfs subvolume snapshot /data /data/.snap/now
btrfs scrub start /data ; btrfs filesystem resize +50G /data

# ZFS
zpool create tank raidz2 sdb sdc sdd sde
zfs create tank/data ; zfs set compression=lz4 tank/data
zfs snapshot tank/data@now ; zpool scrub tank ; zpool status
```

## Interview Prep

**Junior**: "Which filesystem is the safe default on Linux and why?"
- ext4 — it's mature, fast, universally supported, and easy to recover with `e2fsck`, so it's the low-risk choice unless a workload needs specific features.

**Mid**: "Why is XFS preferred for large file / high-throughput workloads?"
- XFS uses extent-based allocation and multiple allocation groups so many CPUs can allocate in parallel, keeping large files contiguous and delivering high sequential and parallel throughput on many-core, high-IOPS systems.

**Senior**: "Contrast journaling and copy-on-write, and where each hurts."
- Journaling (ext4/XFS) writes a metadata journal then updates data in place — fast for random overwrites but no free snapshots; CoW (Btrfs/ZFS) writes new blocks and atomically swaps pointers — cheap snapshots and integrity checking but more fragmentation and latency under heavy random overwrite like databases.

**Staff**: "You need data-integrity guarantees and replication for a multi-TB store. ZFS or Btrfs, and what's the catch?"
- ZFS for production integrity at scale — checksums with self-healing, RAID-Z without the RAID5 write hole, and `zfs send`/`recv` replication — but it's out-of-tree (CDDL) so it's a DKMS module, it wants substantial (ideally ECC) RAM for the ARC, and Btrfs RAID5/6 isn't trustworthy enough to be the alternative for the same job.

## Next Topic

→ [T04 — RAID Levels & mdadm](T04-RAID.md)
