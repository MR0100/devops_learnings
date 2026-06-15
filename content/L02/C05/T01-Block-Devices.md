# L02/C05/T01 — Block Devices, Partitions, Mounting

## Learning Objectives

- Identify block devices and read their topology with `lsblk` and `blkid`
- Create GPT partition tables with `parted`/`gdisk` and understand alignment
- Mount filesystems persistently via `/etc/fstab` using UUIDs, and pick safe mount options

## What a Block Device Is

A block device exposes storage as fixed-size, randomly-addressable blocks (typically 512B or 4KB sectors). The kernel sits between the filesystem and the hardware via the block layer, which queues, merges, and schedules I/O.

```
Application
   ↓  read()/write()
VFS  (filesystem-agnostic)
   ↓
Filesystem  (ext4 / xfs / ...)
   ↓
Block layer  (I/O scheduler, queue)
   ↓
Device driver  (nvme / scsi / virtio)
   ↓
Hardware  (SSD / HDD / SAN volume)
```

Common device nodes:

| Pattern | Meaning |
|---|---|
| `/dev/sda`, `/dev/sdb` | SATA/SAS/SCSI disks (also USB) |
| `/dev/nvme0n1` | NVMe namespace 1 on controller 0 |
| `/dev/nvme0n1p2` | Partition 2 of that namespace |
| `/dev/vda`, `/dev/vdb` | virtio disks (KVM/cloud guests) |
| `/dev/xvda` | Xen virtual disks (older EC2) |
| `/dev/dm-0` | device-mapper (LVM, LUKS, multipath) |

Note the partition-naming quirk: SATA disks append a number (`sda1`), NVMe inserts a `p` (`nvme0n1p1`) because the device name already ends in a digit.

## Inspecting Devices

`lsblk` gives a tree of devices, partitions, and what's mounted where:

```bash
lsblk                                  # tree view
lsblk -f                               # + FSTYPE, UUID, MOUNTPOINT
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL
lsblk -d                               # disks only, no partitions
```

```
NAME        SIZE TYPE MOUNTPOINT
nvme0n1     100G disk
├─nvme0n1p1   1G part /boot
└─nvme0n1p2  99G part
  └─vg0-root 50G lvm  /
```

`blkid` prints filesystem UUIDs, labels, and types — the source of truth for fstab:

```bash
blkid                                  # all devices
blkid /dev/nvme0n1p1                   # one device
# /dev/nvme0n1p1: UUID="a1b2..." TYPE="ext4" PARTUUID="..."
```

Other useful tools: `fdisk -l` (list partition tables), `partprobe` (re-read the partition table without reboot), and `udevadm info --query=all --name=/dev/sda` (full udev attributes).

## Partition Tables: MBR vs GPT

| | MBR (msdos) | GPT |
|---|---|---|
| Max disk size | 2 TiB | 9.4 ZB (effectively unlimited) |
| Max primary partitions | 4 (extended workaround) | 128 by default |
| Redundancy | Single table | Primary + backup header/table |
| Checksums | None | CRC32 on headers and table |
| Firmware | BIOS | UEFI (BIOS works with a BIOS-boot partition) |

**Prefer GPT** for anything new. It's required above 2 TiB and survives header corruption via the backup at the end of the disk.

### Creating a GPT layout with parted

```bash
parted /dev/sdb -- mklabel gpt
parted /dev/sdb -- mkpart primary 1MiB 100%   # use whole disk, 1MiB-aligned
parted /dev/sdb print
```

Start at `1MiB`, not sector 1 — this guarantees alignment to 4K physical sectors and to SSD/SAN erase blocks. Misaligned partitions cause read-modify-write penalties on every I/O.

### Creating with gdisk (interactive, GPT-native)

```bash
gdisk /dev/sdb
# n  -> new partition (accept defaults for whole disk)
# t  -> change type code (8300 Linux fs, 8e00 LVM, fd00 RAID)
# w  -> write and exit
```

Verify alignment afterward:

```bash
parted /dev/sdb align-check optimal 1   # prints "1 aligned"
```

## Mounting

A mount attaches a filesystem to a directory (the mount point) in the unified VFS tree.

```bash
mkfs.ext4 /dev/sdb1                     # create a filesystem first
mount /dev/sdb1 /mnt/data               # one-time mount
mount -o ro,noatime /dev/sdb1 /mnt/data # with options
umount /mnt/data
mount | grep sdb1                       # what's mounted
findmnt /mnt/data                       # cleaner, tree-aware view
```

### Key mount options

| Option | Effect |
|---|---|
| `defaults` | rw, suid, dev, exec, auto, nouser, async |
| `noatime` | Don't update access times — big I/O win, safe for most workloads |
| `relatime` | Update atime only if older than mtime (kernel default) |
| `nodiratime` | Skip atime updates on directories |
| `ro` / `rw` | Read-only / read-write |
| `nodev`, `nosuid`, `noexec` | Harden mounts (use on `/tmp`, `/home`, data volumes) |
| `discard` | Inline TRIM (prefer a periodic `fstrim.timer` instead) |
| `nofail` | Don't fail boot if the device is absent (network/optional disks) |
| `X-mount.mkdir` | Auto-create the mount point |

## Persistent Mounts via /etc/fstab

`/etc/fstab` is read at boot (and by `mount -a`). Six fields per line:

```
# <device>            <mountpoint>  <fstype>  <options>          <dump> <pass>
UUID=a1b2-c3d4-...     /data         ext4      defaults,noatime    0      2
UUID=e5f6-...          /             xfs       defaults            0      1
/dev/vg0/swap          none          swap      sw                  0      0
```

- **Field 5 (dump):** almost always `0`.
- **Field 6 (fsck pass):** `1` for root, `2` for other ext filesystems, `0` to skip (XFS/Btrfs check at mount, so use `0`).

Always reference filesystems by **UUID** (or LABEL), never `/dev/sdb1`. Device names are assigned at discovery time and can reorder across reboots, swapping your `/data` and `/var` disks.

```bash
blkid -s UUID -o value /dev/sdb1        # grab the UUID for fstab
mount -a                                # test fstab without rebooting
systemctl daemon-reload                 # systemd generates units from fstab
```

A typo in fstab can leave the box unbootable. Use `nofail` on non-critical disks and always run `mount -a` before you reboot.

## Common Mistakes

- **Referencing `/dev/sdX` in fstab.** Reboots reorder devices; use UUID/LABEL.
- **Forgetting to grow the filesystem after growing the partition.** A bigger partition does nothing until `resize2fs`/`xfs_growfs` runs (covered in T02).
- **`umount` "target is busy".** A process or shell has a file open or a CWD inside; find it with `lsof +D /mnt/data` or `fuser -vm /mnt/data`.
- **Misaligned partitions.** Starting at sector 63/2048 by hand instead of `1MiB` — silent throughput loss on SSDs/SAN.
- **Editing fstab with no `nofail` test.** A bad line plus a fsck pass of `1` halts boot in emergency mode.

## Best Practices

- Use **GPT** for all new disks; reserve a 1MiB BIOS-boot partition only if you need legacy boot.
- Mount data volumes with `noatime` and harden where possible (`nodev,nosuid`).
- Prefer a periodic `fstrim.timer` over the `discard` mount option for SSDs.
- Label or UUID everything; keep a comment per fstab line documenting purpose.
- After partitioning, run `partprobe` (or reboot) and `align-check optimal` before putting data on it.

## Quick Refs

```bash
# Inspect
lsblk -f                                 # tree + FS + UUID + mount
blkid /dev/sdb1                          # UUID / TYPE / LABEL
findmnt /data                            # what's mounted there
fdisk -l /dev/sdb                        # list partition table

# Partition (GPT)
parted /dev/sdb -- mklabel gpt
parted /dev/sdb -- mkpart primary 1MiB 100%
parted /dev/sdb align-check optimal 1
partprobe /dev/sdb

# Format + mount
mkfs.ext4 /dev/sdb1
mount -o noatime /dev/sdb1 /data
umount /data
fuser -vm /data                          # who's holding it open

# Persist
blkid -s UUID -o value /dev/sdb1
# add to /etc/fstab:  UUID=... /data ext4 defaults,noatime,nofail 0 2
mount -a
```

## Interview Prep

**Junior**: "What's the difference between a disk and a partition?"
- A disk is the whole block device (`/dev/sdb`); a partition is a logical slice of it (`/dev/sdb1`) defined by the partition table.

**Mid**: "Why reference filesystems by UUID in fstab instead of `/dev/sdb1`?"
- Device names are assigned at discovery time and can reorder across reboots or hardware changes; the UUID is stored in the filesystem superblock and is stable, so mounts stay correct.

**Senior**: "A new partition seems slow. How do you check alignment?"
- `parted /dev/sdb align-check optimal 1` — misalignment to the 4K physical sector or SSD erase block forces read-modify-write on every write; fix by recreating the partition starting at `1MiB`.

**Staff**: "Design a partition/mount scheme for a database host that survives a wrong-disk-order reboot and a bad fstab edit."
- GPT labels per role, UUID-based fstab entries, `nofail` on data volumes with fsck pass `0`/`2`, separate volumes for data/WAL/logs mounted `noatime`, and a `mount -a` smoke test plus a serial console for recovery — so reordering can't cross-mount and a typo drops to emergency mode without bricking boot.

## Next Topic

→ [T02 — LVM](T02-LVM.md)
