# L02/C03 — Memory Management

## Chapter Overview

Linux memory management is the area where most production failures hide. Understanding virtual memory, swap, OOM killer, and the meminfo interface is essential for capacity planning, debugging, and tuning.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-Virtual-Memory.md) | Virtual Memory, Paging, Page Tables | 1 hr |
| [T02](T02-Swap-Swappiness-OOM.md) | Swap, Swappiness, OOM Killer | 1 hr |
| [T03](T03-Shared-Memory-mmap.md) | Shared Memory, mmap, /dev/shm | 1 hr |
| [T04](T04-Slab-Buddy.md) | Slab Allocator & Buddy System | 0.5 hr |
| [T05](T05-Meminfo.md) | Reading /proc/meminfo Like a Pro | 1.5 hr |

## Key Concepts

### Virtual vs Physical Memory
- Each process sees a 48-bit virtual address space (x86_64)
- Page table maps virtual pages (4KB by default) to physical frames
- TLB caches recent translations

### Swap
- Disk space used as overflow for memory
- Configured per-system; modern advice: small swap (1–4GB) or none for low-latency workloads
- `vm.swappiness` (0–100) controls eagerness; 60 is default

### OOM Killer
- Triggered when memory cannot be freed
- Picks a victim based on `oom_score` (configurable via `oom_score_adj`)
- Often kills the largest process — not always what you want
- Symptom: `dmesg | grep -i oom`

### /proc/meminfo
Key fields: MemTotal, MemFree, MemAvailable, Buffers, Cached, Active, Inactive, SwapTotal, SwapFree, Slab, KernelStack, PageTables, HugePages, Committed_AS, CommitLimit

### MemAvailable vs MemFree
`free` is often near-zero on a healthy system (caches use all unused RAM). `MemAvailable` is the realistic "how much can apps allocate without swapping" number.

## Interview Themes

- Diagnose OOM kills
- Explain why `free` is low on healthy systems
- Tune swappiness for DB vs cache workloads
- Use mmap for large file processing

## Production Gotchas

- JVM uses RSS, not heap — watch native memory
- Containers with no memory limit can OOM the host
- Page cache vs slab confusion in cgroup v1
- Huge pages misconfiguration killing performance
