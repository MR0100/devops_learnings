# L02/C03/T04 — Slab Allocator & Buddy System

## Learning Objectives

- Understand the two-layer kernel memory allocator: buddy (pages) and slab (objects)
- Read `/proc/buddyinfo` and `/proc/slabinfo` to spot fragmentation and cache bloat
- Recognize slab-leak symptoms ("used RAM nobody owns") and dentry/inode cache growth
- Connect slab accounting to cgroup v2 container memory limits

## Two Layers

The kernel can't use `malloc`. It builds its own allocators, stacked:

```
  kmalloc() / kmem_cache_alloc()   ← drivers & subsystems ask here
            │   (objects: bytes to a few KB)
            ▼
     SLAB / SLUB allocator         ← carves pages into fixed-size object caches
            │   (asks for pages)
            ▼
       Buddy allocator             ← manages physical page frames
            │
            ▼
   physical RAM (4 KB page frames)
```

### Buddy Allocator
- Manages physical pages in **power-of-2 blocks** ("orders"): order-0 = 1 page (4 KB), order-1 = 2 pages, … order-10 = 1024 pages (4 MB)
- Satisfies `__get_free_pages(order)`; on free, merges a block with its sibling "buddy" if both are free (coalescing) to rebuild large contiguous blocks
- Per-zone (DMA, DMA32, Normal) and per-NUMA-node free lists
- Fragmentation is visible in `/proc/buddyinfo`:

```bash
cat /proc/buddyinfo
# Node 0, zone   Normal  4521 1832  642  201  88  31  12  4  1  0  0
#                        ^order0 ^o1                              ^o10
```
Lots of counts at low orders but zeros at high orders means **external fragmentation**: plenty of free RAM, but no contiguous block big enough for a large/huge-page allocation. Hugepage or large-DMA allocations then fail or stall on compaction.

### Slab Allocator
- Built on the buddy allocator; grabs pages and **slices them into many same-size objects**, keeping per-object free lists so allocating a 256-byte `dentry` is O(1) and avoids internal fragmentation
- Caches frequently-allocated kernel structures so they don't churn through the page allocator
- Variants: **SLUB** (default since ~2.6.23 — simpler, better multiprocessor scaling), SLAB (legacy), SLOB (tiny/embedded systems)

```bash
cat /proc/slabinfo        # raw per-cache stats (active/total objs, objsize)
slabtop                   # interactive, sorted live view
slabtop -o | head -20     # one-shot snapshot, biggest caches first
```

## Common Kmem Caches

| Cache | What it holds | Grows when |
|---|---|---|
| `kmalloc-N` | generic allocations of size N (kmalloc-8 … kmalloc-8k) | general kernel activity |
| `dentry` | directory entry cache (path-component lookups) | heavy `find`, `ls -R`, path-walking |
| `inode_cache` / `ext4_inode_cache` | in-memory file inodes | opening/stat-ing many files |
| `task_struct` | one per process/thread | high process/thread churn |
| `vm_area_struct` | one per memory mapping (VMA) | processes with many mmaps |
| `buffer_head` | block-device buffer metadata | filesystem I/O |

`dentry` and `inode_cache` together are the **VFS cache** — the usual suspect when "Slab" balloons.

## Symptoms of Slab Issues

### Bloating dentry/inode cache
A backup job, `find /`, or a container churning millions of short-lived files grows the dentry cache into many GB. It's *reclaimable* (counts as `SReclaimable`), so the kernel frees it under pressure — but it can look alarming and, in a cgroup, can push a container toward its limit before reclaim kicks in.

```bash
# See it
grep -E 'Slab|SReclaimable|SUnreclaim' /proc/meminfo
slabtop -o | grep -E 'dentry|inode'

# Force reclaim (diagnostic, not a fix)
sync; echo 2 > /proc/sys/vm/drop_caches    # 2 = slab/dentry/inode; 1 = pagecache; 3 = both

# Tune eviction aggressiveness (default 100)
sysctl -w vm.vfs_cache_pressure=200        # higher = evict VFS cache sooner
```

`drop_caches` is for diagnosis and benchmarking, never a recurring production cron — you're just throwing away cache the kernel would reclaim on demand anyway.

### "Memory is used but no process owns it"
`top`/`ps` sum process RSS and come up far short of "used" RAM. The gap is often the kernel itself: `Slab` (plus `KernelStack`, `PageTables`) is real RAM consumed by kernel structures and is **not attributed to any process**. Always check `Slab` and `SUnreclaim` in `/proc/meminfo` before concluding "memory leak." A growing `SUnreclaim` (non-reclaimable slab) is the genuinely worrying case — that's a driver or subsystem leaking objects.

```bash
grep -E 'Slab|SReclaimable|SUnreclaim|KernelStack|PageTables' /proc/meminfo
```

## Cgroup Slab Accounting

In **cgroup v2**, kernel memory accounting is on by default: slab objects the kernel allocates *on behalf of a container* (dentries, inodes, `task_struct`, network buffers) count against that container's `memory.max`. Consequences:

- A container that opens huge numbers of files or creates many threads can hit its memory limit from slab alone — even if its userspace heap is small
- The OOM killer can fire inside a cgroup due to kernel-object pressure that's invisible in app-level memory metrics

```bash
cat /sys/fs/cgroup/<slice>/memory.stat | grep -E 'slab|kernel'
# slab_reclaimable, slab_unreclaimable, kernel_stack, etc.
cat /sys/fs/cgroup/<slice>/memory.current   # total charged, incl. kernel slab
```

This is the explanation for the classic "my container's app uses 200 MB but it OOMs at a 512 MB limit": the rest is kernel slab charged to the cgroup.

## Common Mistakes

- Running `echo 3 > /proc/sys/vm/drop_caches` on a cron in production — discards useful cache and hurts performance
- Treating reclaimable slab (`SReclaimable`) as a leak; the kernel frees it under pressure
- Sizing container memory limits from app RSS alone, ignoring kernel slab charged to the cgroup in v2
- Diagnosing hugepage allocation failures as "out of memory" when `/proc/buddyinfo` shows fragmentation, not exhaustion
- Cranking `vm.vfs_cache_pressure` very high on a metadata-heavy fileserver, thrashing the dentry cache

## Best Practices

- Use `slabtop -o` first to identify *which* cache is large before taking any action
- Distinguish `SReclaimable` (benign, reclaimable) from `SUnreclaim` (potential kernel leak) in triage
- Set container memory limits with headroom for kernel slab when workloads open many fds or spawn many threads
- Tune `vm.vfs_cache_pressure` only with evidence; the default 100 is right for most workloads
- For hugepage-dependent workloads, monitor `/proc/buddyinfo` high orders and consider `hugepagesz`/reservation at boot to dodge runtime fragmentation

## Quick Refs

```bash
slabtop -o | head -20                         # biggest slab caches now
cat /proc/slabinfo | sort -k3 -n | tail        # caches by active object count
grep -E 'Slab|SReclaimable|SUnreclaim' /proc/meminfo
cat /proc/buddyinfo                            # page fragmentation per zone/order
sync; echo 2 > /proc/sys/vm/drop_caches        # diagnostic: drop dentry/inode cache
cat /sys/fs/cgroup/<slice>/memory.stat | grep slab   # slab charged to a container
```

## Interview Prep

**Junior**: "What is the slab allocator?"
- A kernel allocator built on top of the page (buddy) allocator that carves pages into caches of fixed-size objects (dentries, inodes, `task_struct`) so the kernel can allocate and free them quickly.

**Mid**: "What's the difference between the buddy and slab allocators?"
- The buddy allocator hands out physical pages in power-of-2 blocks and coalesces them on free; the slab allocator sits above it, slicing those pages into same-size object caches with per-object free lists.

**Senior**: "`/proc/meminfo` shows 20 GB in `Slab`. What now?"
- `slabtop -o` to see which cache dominates — usually `dentry`/`inode_cache` from a filesystem walk; check `SReclaimable` vs `SUnreclaim` to tell benign reclaimable cache from a real kernel leak, and tune `vm.vfs_cache_pressure` only if eviction is genuinely too lazy.

**Staff**: "A container OOMs at its 512 MB limit but the app's RSS is only ~200 MB. Explain."
- In cgroup v2, kernel slab allocated on the container's behalf (dentries, inodes, `task_struct`, socket buffers) is charged to `memory.max`; a workload opening many files or spawning many threads accumulates slab that's invisible in app metrics — check `memory.stat`'s slab fields and size the limit with kernel-memory headroom.

## Next Topic

→ [T05 — Reading /proc/meminfo Like a Pro](T05-Meminfo.md)
