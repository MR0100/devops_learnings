# L02/C04/T01 — CFS (Completely Fair Scheduler) Internals

## Learning Objectives

- Explain how CFS picks the next task using `vruntime` and a red-black tree
- Understand the core CFS tunables (`sched_latency_ns`, `sched_min_granularity_ns`, `sched_wakeup_granularity_ns`)
- Read per-task scheduler stats from `/proc` and reason about fairness vs latency trade-offs

## The Big Picture

CFS is the default scheduler for `SCHED_OTHER` (normal) tasks. Its one job: hand every runnable task a *fair* slice of CPU over time. Instead of fixed time slices, CFS tracks how much CPU each task has consumed (its **virtual runtime**, `vruntime`) and always runs the task that has run the *least* so far.

```
Runqueue (per-CPU) — tasks ordered by vruntime in a red-black tree

       [vruntime=120]
        /          \
 [vr=80]            [vr=210]
   /  \             /
[60] [95]       [180]   ← leftmost node = smallest vruntime = runs next
```

"Most starved" (smallest `vruntime`) sits at the leftmost node. CFS picks it in O(log n), runs it, advances its `vruntime`, and re-inserts it. Fairness emerges without any explicit time-slice table.

## vruntime — The Heart of CFS

`vruntime` is wall-clock runtime *weighted by nice value*:

```
delta_vruntime = delta_exec * (NICE_0_WEIGHT / task_weight)
```

- A nice-0 task has weight 1024 (`NICE_0_WEIGHT`), so its `vruntime` advances at ~real time.
- A high-priority (negative nice) task has a *larger* weight, so its `vruntime` grows *slower* — it stays toward the left of the tree and gets scheduled more often.
- A low-priority (positive nice) task's `vruntime` grows *faster*, pushing it right.

New/woken tasks are placed near `min_vruntime` (not at 0) so they can't monopolize the CPU by "looking starved" forever.

## Scheduling Latency and Granularity

CFS targets a **scheduling period** — a window in which every runnable task should run at least once.

| Tunable | Default | Meaning |
|---|---|---|
| `sched_latency_ns` | 6,000,000 (6 ms) | Target period when nr_running is small |
| `sched_min_granularity_ns` | 750,000 (0.75 ms) | Minimum slice a task gets before preemption |
| `sched_wakeup_granularity_ns` | 1,000,000 (1 ms) | How much "ahead" a waker must be to preempt the current task |

When the number of runnable tasks exceeds `sched_latency_ns / sched_min_granularity_ns` (≈ 8), the period *stretches*:

```
period = max(sched_latency_ns, nr_running * sched_min_granularity_ns)
slice  = period * (task_weight / total_runqueue_weight)
```

So with 20 runnable tasks, each gets a tiny but bounded slice rather than a 6 ms / 20 sliver that would thrash the caches.

```bash
# On older kernels these live in /proc/sys/kernel (sysctl):
sysctl kernel.sched_latency_ns
sysctl kernel.sched_min_granularity_ns
sysctl kernel.sched_wakeup_granularity_ns
```

> Note: On kernels 6.6+ CFS was replaced by **EEVDF** (Earliest Eligible Virtual Deadline First). EEVDF keeps `vruntime` but adds a per-task *lag* and *virtual deadline*; the latency/granularity sysctls were renamed/removed (e.g. `sched_min_granularity_ns` → `base_slice_ns` under `/sys/kernel/debug/sched/`). The mental model below still holds.

## Inspecting the Scheduler

```bash
# Per-task scheduler statistics (run/wait/slice counts)
cat /proc/<pid>/sched

# Per-task time on-CPU vs waiting in runqueue
cat /proc/<pid>/schedstat        # run_ticks  wait_ticks  timeslices

# System-wide runqueue + domain dump
cat /proc/sched_debug | less

# Debugfs knobs on modern kernels
ls /sys/kernel/debug/sched/
cat /sys/kernel/debug/sched/base_slice_ns   # EEVDF base slice
```

Key lines in `/proc/<pid>/sched`:
- `se.vruntime` — the task's current virtual runtime
- `se.sum_exec_runtime` — total real CPU time
- `nr_switches` / `nr_voluntary_switches` / `nr_involuntary_switches`

A high *involuntary* switch count means the task is being preempted (CPU contention); high *voluntary* means it blocks a lot (I/O, locks).

## Load Tracking (PELT)

CFS uses **PELT** (Per-Entity Load Tracking) to estimate how much load each task and runqueue carries. PELT decays past utilization geometrically (~half-life of 32 ms), feeding:

- **Load balancing** — moving tasks between per-CPU runqueues to even out load across cores/NUMA domains.
- **CPU frequency** (`schedutil` governor) — the scheduler tells cpufreq how busy it expects to be, driving DVFS.

```
util_avg of a task → runqueue util → schedutil governor → CPU frequency
```

This is why a bursty task can be slow to ramp the CPU clock: PELT has to "see" the load build up first.

## Group Scheduling and cgroups

CFS is **hierarchical**. With `CONFIG_FAIR_GROUP_SCHED`, cgroups become scheduling entities themselves:

```
root runqueue
 ├── cgroup A (cpu.weight=100)   ← gets ~50%
 │     ├── task1
 │     └── task2
 └── cgroup B (cpu.weight=100)   ← gets ~50%, split among its tasks
       └── task3
```

Two cgroups with equal `cpu.weight` split the CPU 50/50 regardless of how many tasks each holds. This is the foundation of Kubernetes CPU **requests** (cgroup v2 `cpu.weight`) and **limits** (`cpu.max` bandwidth throttling).

```bash
cat /sys/fs/cgroup/<slice>/cpu.weight     # v2 relative share
cat /sys/fs/cgroup/<slice>/cpu.max        # "quota period" e.g. 50000 100000
cat /sys/fs/cgroup/<slice>/cpu.stat       # nr_throttled, throttled_usec
```

`throttled_usec` climbing is the classic "my container is slow but CPU looks idle" CFS-quota culprit.

## Common Mistakes

- Assuming CFS gives fixed time slices — slices are computed dynamically from weight and runnable count.
- Tuning `sched_latency_ns` down to "reduce latency" — this *increases* context switches and cache thrash; usually a net loss.
- Ignoring CFS bandwidth throttling (`cpu.max`) when diagnosing latency in containers — the task can be runnable but throttled.
- Reading `vruntime` as wall time — it is weighted and resets relative to `min_vruntime`.
- Editing sysctls that no longer exist on 6.6+ kernels and assuming the change took effect.

## Best Practices

- Leave CFS tunables at defaults unless you have a measured, reproducible latency problem.
- For latency-sensitive services, prefer CPU **pinning** and **isolation** (next topics) over fiddling with `sched_*` knobs.
- Monitor `cpu.stat` `nr_throttled`/`throttled_usec` in containers; raise limits or remove them before tuning the scheduler.
- Use `cpu.weight` (requests), not CPU limits, to protect latency-critical pods from noisy neighbors.
- Treat `nr_involuntary_switches` growth as a CPU-contention signal, not a code bug.

## Quick Refs

```bash
# Tunables (pre-6.6 kernels)
sysctl kernel.sched_latency_ns
sysctl kernel.sched_min_granularity_ns
sysctl kernel.sched_wakeup_granularity_ns

# Modern (6.6+ / EEVDF)
cat /sys/kernel/debug/sched/base_slice_ns

# Per-task scheduler view
cat /proc/<pid>/sched
cat /proc/<pid>/schedstat
cat /proc/sched_debug

# cgroup CPU control + throttling
cat /sys/fs/cgroup/<path>/cpu.weight
cat /sys/fs/cgroup/<path>/cpu.max
cat /sys/fs/cgroup/<path>/cpu.stat
```

## Interview Prep

**Junior**: "What does the CFS scheduler try to do?"
- Give every runnable task a fair share of CPU over time by always running the one that has run the least.

**Mid**: "What is `vruntime` and how does nice affect it?"
- Virtual runtime is real runtime weighted by the task's priority weight; lower (negative) nice means a heavier weight, so `vruntime` advances slower and the task is scheduled more often.

**Senior**: "A container shows idle CPU but high latency. Where do you look?"
- CFS bandwidth throttling — check `cpu.max` and `cpu.stat` for `nr_throttled`/`throttled_usec`; the task is runnable but throttled within its quota period.

**Staff**: "How would you reason about CFS fairness across a multi-tenant Kubernetes node?"
- It's hierarchical group scheduling: pod `cpu.weight` (requests) sets relative shares at the cgroup level independent of task count; limits add a separate bandwidth cap. Design with weights/requests for proportional fairness and reserve limits for hard isolation, accounting for PELT ramp and per-NUMA load balancing.

## Next Topic

→ [T02 — Nice, Priority, Real-Time Classes](T02-Nice-Priority-RT.md)
