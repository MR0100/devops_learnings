# L02/C07/T03 — Resource Limits

## Learning Objectives

- Configure CPU, memory, I/O, and PID limits via cgroup v2 interface files
- Read accounting files (`memory.current`, `cpu.stat`) to verify enforcement
- Explain CPU throttling vs CPU weight and the OOM-kill path under `memory.max`
- Map Docker/Kubernetes flags (`--cpus`, `--memory`, requests/limits) onto cgroup files

## The Big Picture

A resource limit is a value written to a cgroup controller file. Two flavors exist: **hard caps** (a ceiling the kernel enforces — `memory.max`, `cpu.max`, `pids.max`) and **weights/soft targets** (relative shares used under contention — `cpu.weight`, `memory.high`, `io.weight`). Caps are absolute; weights only matter when a resource is contended.

```
   cpu.max   "200000 100000"  -> 2 full CPUs (quota/period)
   cpu.weight 50..10000        -> share when CPUs are contended
   memory.max 536870912        -> 512 MiB hard cap (OOM if exceeded)
   memory.high 402653184       -> 384 MiB soft cap (reclaim+throttle)
   pids.max   512              -> at most 512 tasks (fork-bomb guard)
   io.max     "8:0 rbps=10485760"  -> 10 MB/s read on device 8:0
```

## CPU

### `cpu.max` — bandwidth (hard cap)

Format: `"<quota_us> <period_us>"`. The cgroup may run for `quota` microseconds out of every `period`. `"max 100000"` means unlimited.

```bash
echo "200000 100000" > /sys/fs/cgroup/demo/cpu.max   # 2 CPUs of throughput
echo "50000 100000"  > /sys/fs/cgroup/demo/cpu.max   # half a CPU
```

This is why `docker run --cpus=2` does not pin to 2 cores: it sets quota=200000/period=100000, so the workload gets *2 CPUs' worth of time* spread across whatever cores the scheduler picks. Bursty single-threaded work can still be throttled at period boundaries.

### `cpu.weight` — proportional share (soft)

Range 1–10000 (default 100). When CPUs are saturated, runtime is divided in proportion to weight. With no contention, weight is irrelevant — a single busy cgroup gets the whole machine regardless of weight.

### Reading enforcement

```bash
cat /sys/fs/cgroup/demo/cpu.stat
# usage_usec, nr_periods, nr_throttled, throttled_usec
```

A high `nr_throttled` / `throttled_usec` means the cap is biting — a classic cause of mysterious p99 latency spikes in containers with tight CPU limits.

## Memory

### `memory.max` — hard cap

When usage would exceed `memory.max`, the kernel first reclaims; if it still cannot fit, the cgroup OOM killer fires and kills a process *inside that cgroup* (the rest of the host is unaffected).

```bash
echo 536870912 > /sys/fs/cgroup/demo/memory.max   # 512 MiB
cat /sys/fs/cgroup/demo/memory.current            # live usage
cat /sys/fs/cgroup/demo/memory.events             # oom, oom_kill counts
```

### `memory.high` — throttling soft cap

Above `memory.high` the kernel aggressively reclaims and throttles the cgroup (slows allocations) instead of killing. Set `high` below `max` to apply back-pressure before a hard OOM, giving the app a chance to shed load.

### `memory.swap.max`

Caps swap usage for the cgroup; set to `0` to forbid swapping (common in latency-sensitive or Kubernetes-by-default setups).

```bash
echo 0 > /sys/fs/cgroup/demo/memory.swap.max
```

## I/O

`io.max` sets per-device byte/IOPS ceilings; `io.weight` sets a proportional share (1–10000). Devices are addressed by `major:minor`.

```bash
lsblk -o NAME,MAJ:MIN                       # find device numbers
echo "8:0 rbps=10485760 wbps=5242880" \
  > /sys/fs/cgroup/demo/io.max              # 10 MB/s read, 5 MB/s write
echo "8:0 100" > /sys/fs/cgroup/demo/io.weight
cat /sys/fs/cgroup/demo/io.stat             # per-device rbytes/wbytes/rios/wios
```

I/O limits in v2 cooperate with the memory controller for buffered-write accounting, something v1 could not do cleanly.

## PIDs

`pids.max` caps the number of tasks (processes + threads) in the cgroup — the simplest defense against fork bombs.

```bash
echo 512 > /sys/fs/cgroup/demo/pids.max
cat /sys/fs/cgroup/demo/pids.current
```

## cpuset — pinning

`cpuset.cpus` and `cpuset.mems` pin a cgroup to specific cores and NUMA nodes — useful for cache locality and avoiding noisy-neighbor jitter on dedicated cores.

```bash
echo "0-3" > /sys/fs/cgroup/demo/cpuset.cpus
echo "0"   > /sys/fs/cgroup/demo/cpuset.mems
```

## Mapping to Docker / Kubernetes

| Intent | Docker flag | cgroup v2 file |
|---|---|---|
| CPU cap | `--cpus=2` | `cpu.max "200000 100000"` |
| CPU share | `--cpu-shares=512` | `cpu.weight` (rescaled) |
| Pin cores | `--cpuset-cpus=0-3` | `cpuset.cpus` |
| Memory cap | `--memory=512m` | `memory.max` |
| Soft memory | `--memory-reservation` | `memory.high`(approx) |
| Disable swap | `--memory-swap=512m` | `memory.swap.max` |
| Process cap | `--pids-limit=512` | `pids.max` |
| I/O cap | `--device-write-bps` | `io.max` |

In Kubernetes, a container's `requests` become weights (proportional share when contended) and `limits` become hard caps. A `limits.memory` maps to `memory.max`; exceeding it triggers the cgroup OOM killer and the container shows `OOMKilled`. A `limits.cpu` maps to `cpu.max`, so a CPU-limited Pod can be throttled even on an otherwise idle node.

## Demo: trigger a cgroup OOM

```bash
sudo mkdir /sys/fs/cgroup/oomtest
echo "+memory" | sudo tee /sys/fs/cgroup/cgroup.subtree_control
echo 52428800 | sudo tee /sys/fs/cgroup/oomtest/memory.max   # 50 MiB
echo 0 | sudo tee /sys/fs/cgroup/oomtest/memory.swap.max
( echo $BASHPID | sudo tee /sys/fs/cgroup/oomtest/cgroup.procs >/dev/null
  python3 -c 'b=bytearray(); 
[b.extend(b"x"*1048576) for _ in range(100)]' )   # allocate 100 MiB
# -> process is OOM-killed; verify:
cat /sys/fs/cgroup/oomtest/memory.events    # oom_kill incremented
dmesg | tail                                # kernel oom-kill log line
```

## Common Mistakes

- Expecting `--cpus=2` to mean two dedicated cores — it is a bandwidth quota, not a pin; use `cpuset.cpus` to pin.
- Setting only `memory.max` with swap enabled and being surprised the app survives past the cap by swapping — set `memory.swap.max=0` for a hard ceiling.
- Ignoring `cpu.stat` throttling when chasing latency; tight CPU limits throttle even on idle hosts.
- Forgetting to enable the controller in the parent `subtree_control`, so the limit file does not exist to write to.

## Best Practices

- Set `memory.high` below `memory.max` so the app gets back-pressure before a hard OOM kill.
- Always cap `pids.max` to contain fork bombs and runaway thread leaks.
- Monitor `cpu.stat` (throttled_usec) and PSI alongside CPU usage — throttling, not utilization, is what hurts latency.
- For latency-critical workloads, pin with `cpuset` and disable swap rather than relying solely on weights.

## Quick Refs

```bash
echo "200000 100000" > cpu.max     # 2 CPUs of bandwidth
echo 100 > cpu.weight              # proportional share (1-10000)
cat cpu.stat                       # throttling + usage
echo 536870912 > memory.max        # 512 MiB hard cap
echo 402653184 > memory.high       # soft cap -> reclaim/throttle
echo 0 > memory.swap.max           # forbid swap
cat memory.current memory.events   # usage + oom counters
echo "8:0 rbps=10485760" > io.max  # 10 MB/s read on dev 8:0
echo 512 > pids.max                # fork-bomb guard
echo "0-3" > cpuset.cpus           # pin to cores 0-3
```

## Interview Prep

**Junior**: "How do you limit a container to 512MB of RAM?"
- Set `memory.max` to 512 MiB in its cgroup (Docker `--memory=512m`); exceeding it triggers the cgroup OOM killer.

**Mid**: "Why might `--cpus=2` still cause latency spikes on an idle host?"
- It is a quota (200000/100000us); a burst that exhausts the quota mid-period gets throttled until the next period, even with free cores available.

**Senior**: "Difference between `memory.high` and `memory.max`?"
- `high` is a soft cap that triggers reclaim and allocation throttling; `max` is a hard cap that triggers OOM kill — use `high` for graceful back-pressure ahead of `max`.

**Staff**: "A Kubernetes Pod is `OOMKilled` intermittently though average memory looks fine. How do you investigate?"
- Look at peak `memory.current` vs `memory.max` and `memory.events.oom_kill`, check page-cache/anon split and whether swap is off, inspect for allocation spikes or memory.high throttling, and right-size the limit or add `memory.high` head-room rather than only raising `max`.

## Next Topic

→ [T04 — Build a Container from Scratch](T04-Build-Container-Scratch.md)
