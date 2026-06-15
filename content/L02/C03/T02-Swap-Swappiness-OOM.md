# L02/C03/T02 — Swap, Swappiness, OOM Killer

## Learning Objectives

- Configure swap appropriately for workload
- Tune swappiness
- Predict and prevent OOM kills

## Swap Fundamentals

Swap is disk-backed memory overflow. When the kernel needs to free RAM (under pressure), it can:
1. Drop clean page cache (free)
2. Write dirty pages back to disk (slower)
3. Swap out anonymous pages (slowest)

A working swap means the system degrades rather than killing processes.

## Should You Use Swap?

| Workload | Recommendation |
|---|---|
| Low-latency app servers | Small swap (1–4 GB) or none with watchdog |
| Database (Postgres, MySQL) | Small swap, low swappiness (1–10) |
| Memory-pressure-prone (Java) | Small swap; tune heap < container limit |
| K8s nodes | Historically disabled (kubelet `failSwapOn: true`). Swap is opt-in via the `NodeSwap` feature gate (beta since 1.28) plus `failSwapOn: false` and `memorySwap` config |

Old advice ("2× RAM swap") is outdated for modern workloads.

## Swappiness

`vm.swappiness` (0–100): how aggressively kernel prefers swap over dropping page cache.

- `60` — default
- `10` — for databases (prefer keeping anon pages in RAM)
- `1` — minimum effective; only swap under heavy pressure
- `0` — don't swap out anonymous pages until the system is near-OOM (free + file pages drop below the high watermark); not "never swap", but it defers anon swapping to the last moment and raises OOM risk

```bash
sysctl vm.swappiness               # check
echo 10 > /proc/sys/vm/swappiness  # set transient
# /etc/sysctl.d/99-mem.conf for persistence
```

## Creating Swap

### Swap File
```bash
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
# in /etc/fstab: /swapfile none swap defaults 0 0
```

### Swap Partition
- Create partition, mkswap, swapon
- Multiple partitions can be used; with `pri=`, kernel stripes

### zswap / zram
- Compressed RAM-backed swap; faster than disk
- `zram` creates compressed swap devices in RAM (no disk needed)
- Useful in low-RAM containers/desktops

## The OOM Killer

When memory is exhausted (no swap, no reclaimable pages), the OOM killer picks a victim and SIGKILLs it.

### How a Victim Is Chosen
- Each process has `oom_score` (0 to ~1000)
- Higher score → more likely victim
- Based on RSS, swap, age, niceness, oom_score_adj

```bash
cat /proc/<pid>/oom_score
cat /proc/<pid>/oom_score_adj      # tunable (-1000 to +1000)
echo -1000 > /proc/<pid>/oom_score_adj  # immune
```

### Symptoms
```bash
dmesg | grep -i oom
journalctl -k | grep -i "out of memory"
journalctl | grep oom-killer
```

Sample dmesg line:
```
Out of memory: Killed process 12345 (java) total-vm:8123456kB, anon-rss:6543210kB
```

### Preventing OOM Kills
- Set memory limits at the cgroup/container level
- Use `MemoryHigh` (systemd) or K8s memory limits
- Configure JVM `-Xmx` lower than container memory limit (leave 20% for non-heap)
- Watch for memory leaks via RSS over time

## OOM in Containers

### Docker
```bash
docker run -m 2g --oom-kill-disable=false myimage
```

When container hits its limit, kernel OOM-kills *within the container's cgroup*. Container restart policies handle the rest.

### Kubernetes
- `resources.limits.memory: 2Gi`
- Pod restarts on OOMKill (status: `OOMKilled`)
- `kubectl describe pod` shows OOMKilled
- Tune workloads: requests vs limits ratio, JVM heap < container limit, watch for native memory growth

## Memory Pressure Beyond OOM

Before OOM, the system slows down due to:
- Direct reclaim (allocation waits for memory to be freed)
- Heavy swap I/O
- Page cache thrashing

Monitor:
```bash
cat /proc/pressure/memory      # PSI: memory pressure stall info
vmstat 1                       # si/so columns (swap in/out)
sar -B 1                       # paging stats
```

PSI (Pressure Stall Information) is the modern early-warning. K8s uses it for evictions.

## The `OOMKilled` JVM Surprise

A JVM with `-Xmx=2g` in a 2g container will OOM under load because:
- Heap = 2g
- Plus metaspace, code cache, direct memory, stacks, threads, JNI = often another 500MB–1GB

Always leave headroom: `-Xmx=1500m` in a 2g container, or use `-XX:MaxRAMPercentage=70`.

## Common Mistakes

- **Sizing the JVM (or any runtime) to the whole limit** — heap + metaspace + code cache + thread stacks + direct/JNI memory must fit; `-Xmx=2g` in a 2g container gets OOMKilled.
- **Treating high swappiness as "use less RAM"** — `vm.swappiness` only biases reclaim between anon pages and page cache; high values can swap out hot anon memory and tank latency.
- **Disabling swap to "avoid slowness"** — without swap the kernel can't evict cold anon pages, so it OOM-kills sooner; a small swap often *improves* stability.
- **Blaming the OOM killer for picking the wrong victim** — it scores by `oom_score` (size-weighted); tune `oom_score_adj` instead of fighting it.
- **Reading container OOM as host OOM** — a cgroup `memory.max` breach kills inside the cgroup with no host memory pressure; check `memory.events`, not just `dmesg` global OOM.

## Best Practices

- **Leave runtime headroom** — `-XX:MaxRAMPercentage=70` (JVM) or `GOMEMLIMIT` (Go) so non-heap memory fits under the cgroup limit.
- **Keep a modest swap on bare metal/VMs** — enough to let the kernel page out genuinely cold memory; pair with low swappiness (`10`) for latency-sensitive servers.
- **Set requests/limits with intent in Kubernetes** — limits define the OOM ceiling; requests drive scheduling. Mismatched values cause surprise kills or wasted nodes.
- **Protect critical processes** — lower `oom_score_adj` for the process that must survive (and raise it for sacrificial helpers).
- **Alert on memory pressure early** — watch PSI (`/proc/pressure/memory`) and cgroup `memory.events`, not just the OOM after it's too late.

## Quick Refs

```bash
# swap
swapon --show ; free -h
sysctl vm.swappiness                 # 0-200 (default 60); 10 for DB/latency
sysctl vm.vfs_cache_pressure
fallocate -l 2G /swapfile && chmod 600 /swapfile
mkswap /swapfile && swapon /swapfile

# OOM tuning
cat /proc/<pid>/oom_score            # current victim score
echo -500 > /proc/<pid>/oom_score_adj   # less likely to be killed (-1000..1000)
dmesg | grep -i 'killed process'     # who got OOM-killed

# container / cgroup v2
cat /sys/fs/cgroup/memory.max
cat /sys/fs/cgroup/memory.events     # oom, oom_kill counters
cat /proc/pressure/memory            # PSI: some/full stall %
```

**Rules of thumb**: swappiness `10` for databases · runtime heap ≈ 70% of the limit · don't disable swap to dodge OOM — it makes OOM *earlier*.

## Interview Prep

**Mid**: "What's swappiness?"

**Senior**: "Our pod is OOMKilled despite low heap usage. What's happening?"
- Non-heap JVM memory (metaspace, direct, code cache, threads). Total RSS > heap.

**Staff**: "Design memory limits for a microservices fleet with heterogeneous JVM/Go/Python workloads."

## Next Topic

→ [T03 — Shared Memory, mmap, /dev/shm](T03-Shared-Memory-mmap.md)
