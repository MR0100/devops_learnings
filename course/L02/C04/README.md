# L02/C04 — CPU & Scheduling

## Chapter Overview

The Linux scheduler controls every microsecond of CPU. For latency-sensitive workloads (databases, APIs), scheduler behavior is the difference between p99 = 50ms and p99 = 500ms.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-CFS-Scheduler.md) | CFS (Completely Fair Scheduler) Internals | 1.5 hr |
| [T02](T02-Nice-Priority-RT.md) | Nice, Priority, Real-Time Classes | 1 hr |
| [T03](T03-CPU-Affinity.md) | CPU Affinity (taskset, cpusets) | 0.5 hr |
| [T04](T04-Context-Switching.md) | Context Switching Costs | 1 hr |

## Key Concepts

### CFS — Completely Fair Scheduler
- Default for SCHED_OTHER (normal processes)
- Goal: every runnable task gets a fair share of CPU
- Uses red-black tree of tasks sorted by `vruntime`
- "Fairness" can be weighted via nice values
- Scheduling latency target: ~6ms (tunable: `sched_latency_ns`)

### Scheduling Classes (Priority Order)
1. Stop (kernel internal)
2. Deadline (SCHED_DEADLINE) — earliest deadline first
3. Real-Time (SCHED_FIFO, SCHED_RR) — fixed priorities 1–99
4. Normal (SCHED_OTHER, CFS) — nice -20 to +19
5. Batch (SCHED_BATCH) — lower priority normal
6. Idle (SCHED_IDLE) — lowest

### Nice Values
- Range: -20 (highest priority) to +19 (lowest)
- Default: 0
- Each step is ~10% CPU weight difference
- `nice`, `renice`, `chrt`

### CPU Affinity
- Pin tasks to specific CPUs
- `taskset`, `numactl`, cgroup `cpuset`
- Useful for cache locality, NUMA-awareness
- K8s: CPU Manager static policy

### Context Switch Costs
- ~1–5 μs direct cost
- Cache misses after switch (real cost often higher)
- Excessive switching → throughput collapse
- Causes: thread contention, voluntary blocks, IPI

### Soft IRQs and Hard IRQs
- Hardware interrupts run at high priority
- ksoftirqd handles deferred processing
- High-network-rate hosts can have ksoftirqd dominate CPU

## Key Tools

```bash
top -H               # threads
mpstat -P ALL 1      # per-CPU
pidstat -t 1         # per-thread CPU
schedtool -p <pid>   # scheduler info
chrt -p <pid>        # show class/priority
taskset -p <pid>     # affinity mask
perf sched record/report
```

## Interview Themes

- "Our service has high p99 latency; how do you diagnose CPU-related causes?"
- "Compare real-time priority vs nice."
- "How does the K8s CPU manager interact with CFS?"
- "Walk me through what happens when you change CPU governor from powersave to performance."
