# L02/C03/T03 — Shared Memory, mmap, /dev/shm

## Learning Objectives

- Use `mmap` for high-performance file I/O
- Understand shared memory between processes
- Recognize `/dev/shm` usage patterns

## mmap()

```c
void *addr = mmap(NULL, length, PROT_READ, MAP_PRIVATE, fd, offset);
```

Maps a file (or anonymous memory) into the process's address space. Reading a mapped file is then ordinary memory access — kernel handles page faults to load data lazily.

### When mmap Wins
- Large read-only files (binaries, datasets)
- Multiple processes reading the same file (shared page cache)
- Random access patterns
- Avoid `read()` syscall overhead

### When read() Wins
- Sequential streaming where prefetch matters
- Small files (mmap overhead > savings)
- Files on slow storage (page faults add latency)

## Shared Memory

### POSIX Shared Memory
```c
int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0600);
ftruncate(fd, size);
void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
```
File appears in `/dev/shm/` (tmpfs).

### SysV Shared Memory (legacy)
- `shmget`, `shmat`, `shmdt`, `shmctl`
- Visible in `ipcs -m`

### Anonymous Shared Memory (between fork-related processes)
```c
void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE,
                 MAP_SHARED | MAP_ANONYMOUS, -1, 0);
```

## /dev/shm

A tmpfs mount; backed by RAM (or swap under pressure). Typical default size: 50% of RAM.

```bash
df -h /dev/shm
mount | grep shm
# Resize: mount -o remount,size=8G /dev/shm
```

Used by:
- Postgres (`shared_buffers` if mapped here)
- Many SDKs for inter-process communication
- Containers: each container has its own /dev/shm by default (small — often 64MB)

### The Container /dev/shm Surprise
Container `/dev/shm` defaults to 64MB. ML workloads (PyTorch DataLoader) often need much more.

```bash
docker run --shm-size=2g myimage
```

```yaml
# K8s
volumes:
- name: shm
  emptyDir:
    medium: Memory
    sizeLimit: 2Gi
```

## Page Cache Tour

`mmap`'d files share the kernel page cache. Two processes mmapping the same file share physical pages. This is how the `vm.cache_pressure` tunable affects different workload mixes.

## Interview Prep

**Mid**: "What does mmap do?"

**Senior**: "When would you use mmap over read()?"

**Staff**: "Our ML training pod gets `Bus error` when loading data. Likely cause?"
- `/dev/shm` exhausted. Increase shm-size or use a different shared storage strategy.

## Next Topic

→ [T04 — Slab Allocator & Buddy System](T04-Slab-Buddy.md)
