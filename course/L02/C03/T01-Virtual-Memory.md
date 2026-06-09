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

## Interview Prep

**Mid**: "What's the difference between virtual and physical memory?"

**Senior**: "Our database has a 64GB working set. Why might we enable huge pages?"
- Reduces TLB pressure; fewer TLB misses on hot pages; significant throughput gain.

**Staff**: "Walk me through what happens between `malloc(1GB)` and writing to it."
- Malloc returns success immediately (overcommit); only on page touch does kernel allocate a physical frame, build page table entry, and return. First touch is slow due to allocation + zeroing.

## Next Topic

→ [T02 — Swap, Swappiness, OOM Killer](T02-Swap-Swappiness-OOM.md)
