# L02/C03/T03 — Shared Memory, mmap, /dev/shm

## Learning Objectives

- Use `mmap` for high-performance file I/O and reason about when it beats `read()`
- Share memory between processes with POSIX, SysV, and anonymous mappings
- Understand `/dev/shm` (tmpfs) and the container 64 MB default that breaks ML workloads
- Diagnose `Bus error` / `SIGBUS` and page-cache interactions in production

## mmap()

```c
void *addr = mmap(NULL, length, PROT_READ, MAP_PRIVATE, fd, offset);
```

`mmap` maps a file (or anonymous memory) directly into the process's virtual address space. Reading the mapping is then ordinary memory access; the kernel services page faults to pull file data into the page cache lazily, on demand. No `read()` syscall per chunk, no copy from kernel buffer into a user buffer.

Key flags:

| Flag | Meaning |
|---|---|
| `PROT_READ`/`PROT_WRITE`/`PROT_EXEC` | page protections |
| `MAP_PRIVATE` | copy-on-write; writes are private, not flushed to the file |
| `MAP_SHARED` | writes go through to the backing file/object, visible to other mappers |
| `MAP_ANONYMOUS` | no file backing; zero-filled memory (this is how `malloc` gets big regions) |
| `MAP_POPULATE` | prefault all pages now instead of on first touch |

```c
// Flush dirty MAP_SHARED pages to disk durably
msync(addr, length, MS_SYNC);
munmap(addr, length);                     // unmap when done
madvise(addr, length, MADV_SEQUENTIAL);   // hint the kernel's readahead
```

### When mmap Wins
- Large read-only files (binaries, indexes, datasets) — the dynamic linker mmaps every shared library
- Multiple processes reading the same file — they share the same physical page-cache pages
- Random access patterns where you'd otherwise `seek`+`read` repeatedly
- Avoiding per-call `read()` syscall and copy overhead

### When read() Wins
- Pure sequential streaming where kernel readahead already prefetches efficiently
- Small files — `mmap`'s setup, page-table, and TLB cost exceeds the savings
- Files on slow/remote storage — each page fault becomes a synchronous I/O stall
- When you need predictable error handling: `read()` returns errors; a bad `mmap` page surfaces as an asynchronous `SIGBUS`

## Shared Memory Between Processes

### POSIX Shared Memory (preferred)
```c
int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0600);
ftruncate(fd, size);                      // size the object
void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
// ... use ptr ...
shm_unlink("/myshm");                     // remove the name when done
```
The object appears as a file in `/dev/shm/myshm` (tmpfs). Clean API, file-descriptor-based, integrates with `select`/`poll` on related fds.

### SysV Shared Memory (legacy)
- `shmget` / `shmat` / `shmdt` / `shmctl`; keyed by `ftok()` integer, not a path
- Visible and manageable with `ipcs -m` and `ipcrm`
- Persists until explicitly removed or reboot — a common source of leaked segments after crashes (`ipcs -m` then `ipcrm -m <id>`)

### Anonymous Shared Memory (fork-related processes)
```c
void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE,
                 MAP_SHARED | MAP_ANONYMOUS, -1, 0);
pid_t pid = fork();   // both parent and child see the same physical pages
```
No name, no file — the mapping is inherited across `fork()`. Ideal for a parent coordinating with its own children.

Whatever the mechanism, shared memory has **no built-in synchronization**. You must place a mutex/semaphore *inside* the shared region (`pthread_mutex` with `PTHREAD_PROCESS_SHARED`, or a POSIX named semaphore) to avoid torn reads/writes.

## /dev/shm

A tmpfs mount backed by RAM (and swap under pressure). Default size is typically 50% of physical RAM on a host.

```bash
df -h /dev/shm                    # size and usage
mount | grep shm                  # confirm it's tmpfs
mount -o remount,size=8G /dev/shm # resize on a host
```

Used by:
- PostgreSQL for dynamic shared memory segments (parallel query workers)
- Chromium/Electron, Python `multiprocessing`, many SDKs for fast IPC
- Anything calling `shm_open` — POSIX shm objects live here

### The Container /dev/shm Surprise
A container's `/dev/shm` defaults to **64 MB**, regardless of host RAM. ML data pipelines (PyTorch `DataLoader` with `num_workers>0` uses shared memory to pass tensors between workers) blow past this instantly:

```bash
docker run --shm-size=2g myimage
```

```yaml
# Kubernetes: mount a Memory-backed emptyDir at /dev/shm
volumes:
- name: shm
  emptyDir:
    medium: Memory
    sizeLimit: 2Gi
volumeMounts:
- name: shm
  mountPath: /dev/shm
```

Note: a `Memory`-medium `emptyDir` counts against the pod's memory limit, so size it as part of the memory budget.

## Page Cache Tour

`mmap`'d and `read()`-served file data both live in the kernel **page cache**. Two processes mmapping the same file share the exact same physical pages — that's why a binary loaded 50 times consumes one copy of its read-only text. The page cache is reclaimable: it's the `Cached` line in `/proc/meminfo`, and `vm.vfs_cache_pressure` and memory pressure govern how aggressively the kernel evicts it. A `MAP_SHARED` write dirties a page that the kernel later writes back; until then it's `Dirty` in `meminfo` and at risk on power loss unless you `msync`.

## Common Mistakes

- Assuming shared memory provides synchronization — it doesn't; you must add a process-shared mutex/semaphore
- Leaking SysV segments or POSIX shm names after a crash (`ipcs -m` / files lingering in `/dev/shm`)
- Writing large scratch to `/dev/shm` and exhausting RAM, triggering OOM instead of using disk
- `mmap`-ing a file that another process truncates — touching the now-missing pages raises `SIGBUS`
- Forgetting `msync` before relying on `MAP_SHARED` writes being durable on disk

## Best Practices

- Prefer POSIX `shm_open` over SysV for new code: fd-based, path-named, cleaner lifecycle
- Always pair shared memory with explicit synchronization (`PTHREAD_PROCESS_SHARED` mutex or named semaphore)
- Set `--shm-size` / a Memory `emptyDir` for any container doing multiprocessing or ML data loading
- Use `madvise(MADV_SEQUENTIAL|MADV_RANDOM|MADV_DONTNEED)` to guide readahead and reclaim
- Unlink shm objects (`shm_unlink`/`ipcrm`) on shutdown so they don't accumulate across restarts

## Quick Refs

```bash
df -h /dev/shm                        # tmpfs size / usage
ls -la /dev/shm                       # live POSIX shm objects
ipcs -m                               # SysV shared memory segments
ipcrm -m <shmid>                      # remove a leaked SysV segment
grep -E 'Cached|Dirty|Shmem' /proc/meminfo   # page cache & shared mem accounting
pmap -x <pid> | grep -i shm           # this process's shared mappings
docker run --shm-size=2g img          # bump container /dev/shm from 64 MB
```

## Interview Prep

**Junior**: "What does `mmap` do?"
- Maps a file or anonymous memory into the process's address space so you access it as ordinary memory, with the kernel paging data in on demand.

**Mid**: "When would you use `mmap` over `read()`?"
- For large or randomly-accessed files, and especially when multiple processes read the same file so they share page-cache pages; `read()` is better for small files and pure sequential streaming where readahead already wins.

**Senior**: "Two processes need to share a 1 GB buffer with low latency. How?"
- POSIX shared memory: `shm_open` + `ftruncate` + `mmap(MAP_SHARED)` so both map the same physical pages, with a `PTHREAD_PROCESS_SHARED` mutex placed inside the region for synchronization.

**Staff**: "Our ML training pod throws `Bus error` while loading data. Likely cause and fix?"
- The container's 64 MB `/dev/shm` is exhausted by the DataLoader's worker shared memory, so a page fault on the full tmpfs raises `SIGBUS`; raise `--shm-size` (or mount a sized Memory `emptyDir` at `/dev/shm`) and account for it in the pod's memory limit.

## Next Topic

→ [T04 — Slab Allocator & Buddy System](T04-Slab-Buddy.md)
