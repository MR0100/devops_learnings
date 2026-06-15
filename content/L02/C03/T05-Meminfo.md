# L02/C03/T05 — Reading /proc/meminfo Like a Pro

## Learning Objectives

- Interpret every important field in /proc/meminfo
- Reason about memory pressure from these numbers
- Build accurate "available memory" mental models

## The Key Fields

```
MemTotal:       64421996 kB   Total RAM available
MemFree:         1234567 kB   Truly free (do not use as "available"!)
MemAvailable:   45678912 kB   Realistic for new allocations
Buffers:          543210 kB   Buffer cache (block I/O metadata)
Cached:         42345678 kB   Page cache (file content)
SwapCached:        12345 kB   Swap pages also in RAM
Active:         30000000 kB   Recently used pages (likely keep)
Inactive:       12000000 kB   Candidates for reclaim
Active(anon):   20000000 kB   Anonymous pages active
Inactive(anon):  3000000 kB   
Active(file):   10000000 kB   File-backed pages active
Inactive(file):  9000000 kB
Unevictable:           0 kB   Pinned (e.g., mlock'd)
Mlocked:               0 kB
SwapTotal:       4194300 kB
SwapFree:        4194300 kB
Dirty:               123 kB   Modified, not yet written back
Writeback:             0 kB   Currently being written
AnonPages:      20000000 kB   Anonymous (heap, stack, anon mmap)
Mapped:          5000000 kB   Mapped files (mmap + libs)
Shmem:           1500000 kB   /dev/shm + tmpfs
Slab:            2000000 kB   Kernel object cache
SReclaimable:    1500000 kB   Slab that can be freed
SUnreclaim:       500000 kB   Slab pinned
KernelStack:       50000 kB   Kernel stacks of all threads
PageTables:       300000 kB   Page tables
CommitLimit:    40000000 kB   Max committable (depends on overcommit)
Committed_AS:   25000000 kB   Total committed across processes
HugePages_Total:       0
HugePages_Free:        0
Hugepagesize:       2048 kB
```

## MemFree vs MemAvailable

**Don't use MemFree** to determine if you can allocate more memory. A healthy system has MemFree near zero because the kernel uses unused RAM for page cache (which is reclaimable).

**MemAvailable** is the kernel's estimate of how much you could allocate without swapping. Use it.

## Active vs Inactive

The kernel maintains LRU-like lists:
- Active: recently referenced; less likely to be reclaimed
- Inactive: candidates for reclaim

Pages move active → inactive on time; inactive → reclaimed when memory needed.

## Anonymous vs File-Backed

- **Anonymous**: heap, stack, anonymous mmap. To free, must swap.
- **File-backed**: mmap'd files (libs, executables, mmap'd data). Can be dropped (clean) or written back (dirty) then freed.

## Dirty / Writeback

- Dirty pages: modified, must be written to disk before reclaim
- High Dirty = potential write storm coming
- Tuned by `vm.dirty_*` sysctls

## CommitLimit / Committed_AS

If `Committed_AS` exceeds `CommitLimit`, no more allocations allowed in strict overcommit mode (mode 2). In default mode (0), some leeway.

```
CommitLimit = SwapTotal + (RAM × overcommit_ratio/100)
```

## Practical Reading Patterns

### Healthy System
- MemFree low
- Cached high
- MemAvailable healthy (>30% of MemTotal)
- Swap usage minimal
- Dirty bounded

### Memory-Stressed System
- MemFree very low
- MemAvailable low
- Cached shrinking
- Swap usage growing
- Direct reclaim activity (check `/proc/pressure/memory`)

### Memory Leak Pattern
- AnonPages or Slab growing without bound
- MemAvailable falling steadily
- Eventually OOM

## Reading in Containers

`/proc/meminfo` in a container shows the **host's** values (unless cgroup v2 with `memory.peak`/`memory.current` mounted appropriately). To see your container's actual usage:

```bash
# cgroup v2
cat /sys/fs/cgroup/memory.current
cat /sys/fs/cgroup/memory.max
cat /sys/fs/cgroup/memory.stat

# cgroup v1
cat /sys/fs/cgroup/memory/memory.usage_in_bytes
cat /sys/fs/cgroup/memory/memory.limit_in_bytes
```

JVMs and Go runtimes that read `/proc/meminfo` directly can be tricked into thinking they have host RAM. Use container-aware flags (`-XX:+UseContainerSupport` in JVM, `GOMEMLIMIT` in Go).

## Common Mistakes

- **Treating `MemFree` as available memory** — free is just unallocated; the kernel deliberately uses spare RAM for page cache. Use **`MemAvailable`** for "what an app can get without swapping."
- **Panicking at low free + high cache** — reclaimable page cache (Cached/Buffers) is returned on demand; it is *not* a leak or a shortage.
- **Reading `/proc/meminfo` inside a container** — it reports the *host's* totals; per-container truth lives in `memory.current`/`memory.max` under cgroup.
- **Ignoring `Committed_AS` vs `CommitLimit`** — committed memory exceeding the limit (under strict overcommit) is the real warning sign, not low MemFree.
- **Confusing high `Dirty` with a problem** — dirty pages awaiting writeback are normal; only sustained, growing Dirty under I/O stalls indicates trouble.

## Best Practices

- **Build alerts on `MemAvailable`, not `MemFree`** — it accounts for reclaimable cache and is the kernel's own estimate of usable memory.
- **Track the deltas over time** — a steady rise in `AnonPages`/`Mapped` with flat cache points to a real leak; snapshot periodically and diff.
- **Distinguish anon from file-backed pressure** — growing `Active(anon)` that can't be reclaimed leads to swap/OOM; growing `Active(file)` is usually just hot cache.
- **In containers, read cgroup stats** — `memory.current`, `memory.max`, and `memory.stat` reflect the real limit and breakdown; combine with container-aware runtime flags.
- **Watch `Committed_AS` against `CommitLimit`** under strict overcommit to catch allocation exhaustion before `fork()`/`malloc` start failing.

## Quick Refs

**Fields that actually matter**

| Field | Meaning |
|---|---|
| `MemTotal` / `MemFree` | Total RAM / completely unused |
| `MemAvailable` | Estimate of allocatable memory (free + reclaimable) — **use this** |
| `Buffers` / `Cached` | Block-device metadata / page cache (reclaimable) |
| `Active`/`Inactive` (`anon`/`file`) | Reclaim hotness, split by anon vs file-backed |
| `Dirty` / `Writeback` | Modified pages pending / being flushed to disk |
| `AnonPages` / `Mapped` | Process anonymous memory / mmapped files |
| `CommitLimit` / `Committed_AS` | Overcommit ceiling / total promised |
| `SwapTotal` / `SwapFree` | Swap capacity / unused |

```bash
cat /proc/meminfo
awk '/MemAvailable|MemFree|Cached|Dirty|Committed_AS/' /proc/meminfo

# container truth (cgroup v2)
cat /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.max
cat /sys/fs/cgroup/memory.stat
```

**One rule**: `MemAvailable`, not `MemFree`, answers "is this box running out of memory?"

## Interview Prep

**Mid**: "What's MemAvailable vs MemFree?"

**Senior**: "How would you detect a memory leak from /proc/meminfo over time?"

**Staff**: "Walk me through interpreting /proc/meminfo on a database server that's swapping."

## Next Chapter

→ [C04 — CPU & Scheduling](../C04/README.md)
