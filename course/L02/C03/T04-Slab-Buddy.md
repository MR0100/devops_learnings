# L02/C03/T04 — Slab Allocator & Buddy System

## Learning Objectives

- Understand how the kernel allocates memory
- Recognize slab leak symptoms
- Use slabtop to investigate

## Two Layers

### Buddy Allocator
- Manages physical pages in power-of-2 chunks
- Splits and coalesces to satisfy `__get_free_pages` requests
- Fragmentation visible in `/proc/buddyinfo`

```bash
cat /proc/buddyinfo
# Node 0, zone Normal  1234 567 89 ...
```

### Slab Allocator
- Higher-level allocator built on the buddy
- Caches small objects (dentries, inodes, kmalloc-N)
- Variants: SLAB (legacy), SLUB (default), SLOB (small systems)

```bash
cat /proc/slabinfo                  # detailed
slabtop                             # interactive view
slabtop -o | head -20
```

## Common Kmem Caches

| Cache | What |
|---|---|
| `kmalloc-N` | Generic allocations of size N |
| `dentry` | Directory entries (path lookups) |
| `inode_cache` | File inodes |
| `task_struct` | One per process |
| `vm_area_struct` | Memory mapping records |

## Symptoms of Slab Issues

### Bloating dentry cache
- Heavy `find` or filesystem walks → cache grows
- `echo 2 > /proc/sys/vm/drop_caches` clears it
- Tune `vm.vfs_cache_pressure` (default 100; raise to evict more)

### Memory shown "used" but processes aren't using it
- Kernel structures (slab) consume RAM and aren't counted as process memory
- Look at `Slab` and `SReclaimable` in `/proc/meminfo`

## Cgroup Slab Accounting

In cgroup v2, kmem accounting is on by default. Container memory limit includes kernel slab allocated on the container's behalf. This is why containers with many open files can hit memory limits unexpectedly.

## Interview Prep

**Mid**: "What is the slab allocator?"

**Senior**: "/proc/meminfo shows 20GB in Slab. What now?"
- `slabtop` to see which cache. Often `dentry` from a find. Drop caches or tune vfs_cache_pressure.

## Next Topic

→ [T05 — Reading /proc/meminfo Like a Pro](T05-Meminfo.md)
