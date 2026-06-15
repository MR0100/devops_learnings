# L02/C03/T01 — Virtual Memory, Paging, Page Tables

## Learning Objectives

- Explain virtual-to-physical address translation
- Understand pages, page tables, and TLB
- Apply huge pages for high-performance workloads

## The Big Picture

Every process gets a private 48-bit virtual address space (on x86_64). The kernel maintains page tables that map virtual addresses to physical RAM. The MMU does the lookup; the TLB caches it.

```
Virtual Address (48 bits)
   ↓
  MMU + Page Table
   ↓
Physical Frame
```

## Page Table Structure

Modern x86_64 uses 4-level page tables:
- PML4 (Page Map Level 4)
- PDPT (Page Directory Pointer Table)
- PD (Page Directory)
- PT (Page Table)

Each entry can point to another table or to a final page. 5-level page tables (57-bit address space) are coming.

A page table walk is up to 4 memory accesses — expensive. That's why the TLB exists.

## Page Sizes

- Default: 4KB
- Huge pages: 2MB (PMD level)
- Gigantic pages: 1GB (PUD level)

Huge pages reduce TLB pressure for large memory workloads (databases, JVM heaps). Configure via `/proc/sys/vm/nr_hugepages` or transparent huge pages.

## TLB and TLB Shootdowns

- TLB: per-CPU cache of recent virtual→physical translations
- Hit: ~1 cycle
- Miss: ~10–100 cycles (page table walk)
- Modifying a page table requires *TLB shootdown* on other CPUs — expensive at scale

## Process Memory Layout

```
0xFFFF...    Kernel space (top half)
─────────────  user/kernel boundary
            Stack (grows down)
            ↓
            ...mmap region (libraries, mmap'd files)...
            ↑
            Heap (grows up via brk)
            BSS (uninitialized)
            Data (initialized)
            Text (code)
0x00400000   Default program start
```

Inspect a running process:
```bash
cat /proc/<pid>/maps
pmap -X <pid>
```

## Overcommit

Linux overcommits memory by default — `malloc()` returns success even if there isn't enough RAM + swap. Real allocation happens on first page touch (demand paging).

- `vm.overcommit_memory`: 0 (heuristic, default), 1 (always allow), 2 (strict)
- `vm.overcommit_ratio`: with mode 2, percent of RAM allowed

Overcommit lets sparse mmaps work, but hides true memory pressure.

## Common Tooling

```bash
free -h                    # high-level
cat /proc/meminfo          # detailed
pmap -X 1234               # per-process map
ps -eo pid,rss,vsz,cmd     # RSS, VSS per process
smem -tk                   # PSS-aware
```

### RSS vs VSS vs PSS
- **VSS** (Virtual Set Size): virtual address space allocated
- **RSS** (Resident Set Size): physical memory in use (incl. shared)
- **PSS** (Proportional Set Size): RSS with shared pages divided by sharers

For accurate per-process memory accounting in a container/JVM environment, prefer PSS.

## Common Mistakes

- **Reading VSZ as "memory used"** — virtual size includes unbacked mappings, shared libs, and overcommitted allocations; it routinely dwarfs real RSS.
- **Summing RSS across processes** — shared pages (libc, mmapped files) are counted in every sharer, double-counting; use PSS for fleet/container accounting.
- **Assuming `malloc` reserves physical memory** — with overcommit, allocation succeeds immediately and frames are only assigned on first touch (page fault).
- **Enabling huge pages blindly** — transparent huge pages can hurt latency-sensitive or fork-heavy workloads (e.g., Redis); they help large, stable working sets like databases.
- **Ignoring TLB pressure** — a "memory-bound" slowdown is sometimes TLB-bound; more RAM won't help, but huge pages might.

## Best Practices

- **Account with PSS in shared environments** — `smem -tk` or `/proc/<pid>/smaps_rollup` gives per-process truth when libraries are shared.
- **Match overcommit policy to workload** — keep the default heuristic for general hosts; consider `vm.overcommit_memory=2` with a ratio for databases that must never be OOM-surprised.
- **Use huge pages deliberately** — reserve explicit hugepages for big, hot, stable working sets (DB buffer pools); leave THP `madvise` or off for latency-critical services.
- **Pre-fault when first-touch latency matters** — touch or `mlock` critical regions at startup so the page-fault cost isn't paid on the hot path.
- **Watch faults, not just RSS** — rising major faults in `/proc/<pid>/stat` or `vmstat` signals thrashing well before RSS tells the story.

## Quick Refs

**The three "sizes"**

| Metric | Meaning | Use for |
|---|---|---|
| **VSZ** | Virtual address space mapped | Almost never (overstates usage) |
| **RSS** | Resident physical pages (incl. shared) | Per-process ceiling |
| **PSS** | RSS with shared pages split by sharers | Fair per-process / container accounting |

```bash
free -h                              # system-wide
cat /proc/meminfo                    # detailed fields
pmap -X <pid>                        # per-mapping breakdown
cat /proc/<pid>/smaps_rollup         # quick PSS/RSS totals
smem -tk                             # PSS-aware listing
grep -i huge /proc/meminfo           # huge page status
cat /sys/kernel/mm/transparent_hugepage/enabled
```

**Key sysctls**: `vm.overcommit_memory` (0 heuristic / 1 always / 2 strict) · `vm.overcommit_ratio` · `vm.nr_hugepages`.

## Interview Prep

**Mid**: "What's the difference between virtual and physical memory?"

**Senior**: "Our database has a 64GB working set. Why might we enable huge pages?"
- Reduces TLB pressure; fewer TLB misses on hot pages; significant throughput gain.

**Staff**: "Walk me through what happens between `malloc(1GB)` and writing to it."
- Malloc returns success immediately (overcommit); only on page touch does kernel allocate a physical frame, build page table entry, and return. First touch is slow due to allocation + zeroing.

## Next Topic

→ [T02 — Swap, Swappiness, OOM Killer](T02-Swap-Swappiness-OOM.md)
