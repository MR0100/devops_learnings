# L02/C05/T02 — LVM (Physical Volumes, Volume Groups, Logical Volumes)

## Learning Objectives

- Explain the PV → VG → LV abstraction and why it beats raw partitions
- Build and grow a volume online with `pvcreate`/`vgcreate`/`lvcreate`/`lvextend` + `resize2fs`/`xfs_growfs`
- Use LVM snapshots for point-in-time backups and understand their COW cost

## Why LVM Exists

Raw partitions are rigid: their size and order are fixed on disk, and growing one means moving everything after it. LVM (Logical Volume Manager) inserts a virtualization layer between physical disks and filesystems. You pool disks into a group, then carve flexible, resizable volumes out of the pool — online, without repartitioning.

```
/dev/sdb  /dev/sdc  /dev/sdd        physical disks
   │         │         │
   ▼         ▼         ▼
  PV        PV        PV            pvcreate  (mark disk as LVM-managed)
   └────────┼─────────┘
            ▼
          VG  "vg0"                 vgcreate  (pool of free extents)
            │
   ┌────────┼────────┐
   ▼        ▼        ▼
  LV       LV       LV              lvcreate  (logical volumes)
 root     data      swap
   │        │
   ▼        ▼
 ext4     xfs                       mkfs + mount
```

The unit of allocation is the **physical extent (PE)**, default 4MiB. Every LV is an integer number of extents mapped (possibly non-contiguously) onto PVs.

## The Three Layers

| Layer | Command | What it is |
|---|---|---|
| Physical Volume (PV) | `pvcreate` | A disk/partition initialized with LVM metadata |
| Volume Group (VG) | `vgcreate` | A pool combining one or more PVs into free extents |
| Logical Volume (LV) | `lvcreate` | A virtual block device carved from the VG |

Inspect each layer:

```bash
pvs        # PV summary        | pvdisplay  (detailed)
vgs        # VG summary        | vgdisplay
lvs        # LV summary        | lvdisplay
pvscan / vgscan / lvscan       # rescan
```

```
# pvs
  PV         VG    Fmt  Attr PSize   PFree
  /dev/sdb   vg0   lvm2 a--  100.00g 50.00g
# vgs
  VG    #PV #LV #SN Attr   VSize   VFree
  vg0     2   3   0 wz--n- 199.99g 99.99g
# lvs
  LV    VG    Attr       LSize  Pool Origin
  data  vg0   -wi-ao---- 50.00g
```

## Building a Volume From Scratch

```bash
# 1. Initialize disks as PVs
pvcreate /dev/sdb /dev/sdc

# 2. Create a volume group from them
vgcreate vg0 /dev/sdb /dev/sdc

# 3. Carve a logical volume
lvcreate -L 100G -n data vg0          # by size
lvcreate -l 100%FREE -n data vg0      # by extents (use all free space)

# 4. Make a filesystem and mount
mkfs.xfs /dev/vg0/data                # device path: /dev/<vg>/<lv>
mkdir -p /data && mount /dev/vg0/data /data
```

The LV appears as both `/dev/vg0/data` and `/dev/mapper/vg0-data` (it's a device-mapper target — you'll see it as `dm-N` in `lsblk`).

## Growing a Volume Online (the headline feature)

Two steps: extend the LV, then grow the filesystem on top of it. Both work while mounted.

```bash
# Add a new disk to the pool first if the VG is full:
pvcreate /dev/sdd
vgextend vg0 /dev/sdd

# Extend the logical volume
lvextend -L +50G /dev/vg0/data        # add 50G
lvextend -l +100%FREE /dev/vg0/data   # consume all free extents

# Grow the filesystem to fill the LV
resize2fs /dev/vg0/data               # ext4 (online)
xfs_growfs /data                      # XFS — pass the MOUNTPOINT, not the device
```

`lvextend -r` does both at once (it calls the right resizer for the FS):

```bash
lvextend -r -L +50G /dev/vg0/data
```

| Filesystem | Grow command | Argument | Shrink? |
|---|---|---|---|
| ext4 | `resize2fs` | device | yes (offline) |
| XFS | `xfs_growfs` | **mount point** | **no — XFS can't shrink** |
| Btrfs | `btrfs filesystem resize` | mount point | yes |

This is the answer to "extend a filesystem online": `vgextend` (if needed) → `lvextend` → `resize2fs`/`xfs_growfs`, all without unmounting.

## Snapshots

An LVM snapshot is a copy-on-write (COW) point-in-time view of an origin LV. At creation it's nearly instant and consumes almost no space; as the origin changes, the **original** blocks are copied into the snapshot's COW area before being overwritten.

```bash
# Create a 10G snapshot of the data LV
lvcreate -L 10G -s -n data_snap /dev/vg0/data

# Mount it read-only and back it up
mount -o ro /dev/vg0/data_snap /mnt/snap
tar czf /backup/data.tar.gz -C /mnt/snap .
umount /mnt/snap

# Remove when done
lvremove /dev/vg0/data_snap
```

```
Origin LV ──── block X overwritten ────► new data
   │                                       
   └─ before overwrite, old X copied ──► Snapshot COW area
Snapshot read of X → served from COW; unchanged blocks → read from origin
```

**Critical**: size the snapshot for the write churn during its lifetime, not the data size. If the COW area fills, the snapshot is **dropped (invalidated)** — check `lvs` for the `Snap%` column. Snapshots also add write amplification (every first overwrite is doubled), so they're for short-lived backups, not permanent copies. Thin pools (`lvcreate --thin`) avoid the fixed-size trap by allocating COW space on demand.

## Thin Provisioning (briefly)

```bash
lvcreate -L 100G --thinpool tp vg0          # a thin pool
lvcreate -V 500G --thin -n vm1 vg0/tp       # 500G "virtual" LV from a 100G pool
```

Thin volumes report a size larger than physical backing and allocate on write. Powerful for overcommit and cheap snapshots — but **monitor pool usage**, because a full thin pool wedges all volumes that share it.

## Common Mistakes

- **Running `xfs_growfs` on the device path.** It takes the **mount point**; passing the device fails or no-ops.
- **Forgetting the second step.** `lvextend` alone gives the filesystem no new space — you still need `resize2fs`/`xfs_growfs` (or `lvextend -r`).
- **Undersizing a snapshot** so its COW area fills and the snapshot is silently invalidated mid-backup.
- **Treating snapshots as backups.** They live on the same VG/disks; lose the disk, lose both. They are a *consistency* tool, not durability.
- **Expecting to shrink XFS.** It can't shrink; plan capacity or use ext4/Btrfs if shrinking matters.

## Best Practices

- Leave free space in the VG so you can extend, snapshot, and recover without adding disks under pressure.
- Use `lvextend -r` to grow LV and FS atomically and avoid the two-step footgun.
- Name LVs by role (`data`, `wal`, `logs`) and keep one VG per failure/perf domain.
- For snapshot backups: snapshot → mount read-only → back up → remove promptly; size COW for write churn.
- Monitor thin-pool `Data%` / `Meta%` and snapshot `Snap%` with alerts well below 100%.

## Quick Refs

```bash
# Inspect
pvs ; vgs ; lvs
pvdisplay /dev/sdb ; vgdisplay vg0 ; lvdisplay /dev/vg0/data

# Build
pvcreate /dev/sdb /dev/sdc
vgcreate vg0 /dev/sdb /dev/sdc
lvcreate -L 100G -n data vg0          # or  -l 100%FREE
mkfs.xfs /dev/vg0/data

# Grow online
pvcreate /dev/sdd ; vgextend vg0 /dev/sdd
lvextend -r -L +50G /dev/vg0/data     # extends LV + FS together
# or manually:
lvextend -l +100%FREE /dev/vg0/data
resize2fs /dev/vg0/data               # ext4
xfs_growfs /data                      # XFS (mount point!)

# Snapshot
lvcreate -L 10G -s -n data_snap /dev/vg0/data
mount -o ro /dev/vg0/data_snap /mnt/snap
lvremove /dev/vg0/data_snap
```

## Interview Prep

**Junior**: "What are the three layers of LVM?"
- Physical Volumes (disks marked for LVM), Volume Groups (a pool of PVs), and Logical Volumes (resizable virtual disks carved from the VG).

**Mid**: "Walk me through extending a filesystem online."
- Add a disk with `pvcreate`/`vgextend` if the VG is full, `lvextend -L +50G` the volume, then `resize2fs` (ext4) or `xfs_growfs <mountpoint>` (XFS) — all while mounted; `lvextend -r` does both steps at once.

**Senior**: "Explain LVM snapshots and their failure mode."
- A snapshot is a COW point-in-time view: original blocks are copied to a fixed COW area before the origin overwrites them; if write churn exceeds the snapshot size the COW area fills and the snapshot is invalidated, so size it for churn and keep it short-lived.

**Staff**: "When would you choose thin provisioning, and what's the operational risk?"
- Use thin pools to overcommit capacity and get cheap, on-demand snapshots when actual usage is far below allocated; the risk is a full shared pool that wedges every thin volume at once, so it demands hard monitoring/alerting on pool data and metadata usage and an auto-extend or reserve policy.

## Next Topic

→ [T03 — ext4 vs XFS vs Btrfs vs ZFS](T03-Filesystems-Compared.md)
