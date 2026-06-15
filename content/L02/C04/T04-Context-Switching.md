# L02/C04/T04 — Context Switching Costs

## Learning Objectives

- Break down the direct and indirect costs of a context switch
- Distinguish voluntary vs involuntary switches and what each signals
- Measure switching with `vmstat`, `pidstat`, `/proc`, and `perf sched`

## What a Context Switch Actually Costs

A context switch saves one task's CPU state and restores another's. The **direct** cost (register save/restore, scheduler logic, page-table/`CR3` swap on a process switch) is small — roughly **1–5 µs**. The **indirect** cost is usually larger and invisible to simple counters:

```
Direct cost (~1–5 µs):   save regs → run scheduler → restore regs → swap CR3
Indirect cost (often >):  cold L1/L2/L3 cache, TLB flush, branch predictor reset
                          ↓
              hundreds of cache-miss cycles as the new task "warms up"
```

A process-to-process switch also reloads `CR3`, which can flush the TLB (mitigated by PCID tagging on modern CPUs). Thread-to-thread switches within the same process keep the address space, so they're cheaper.

## Types of Context Switch

| Type | Trigger | Counter |
|---|---|---|
| **Voluntary** | Task blocks: I/O wait, lock, `sleep`, `read()` on empty socket | `voluntary_ctxt_switches` |
| **Involuntary** | Preempted: time slice ended, higher-priority task woke, CFS rebalanced | `nonvoluntary_ctxt_switches` |

```bash
grep ctxt /proc/1234/status
#   voluntary_ctxt_switches:    48213    ← blocking a lot (I/O, locks)
#   nonvoluntary_ctxt_switches: 192       ← being preempted (CPU contention)
```

- High **voluntary** → the task blocks often: I/O-bound, lock contention, chatty syscalls.
- High **involuntary** → CPU is oversubscribed: too many runnable threads fighting for cores.

## Measuring System-Wide

```bash
vmstat 1
# procs ---------- cpu ----------  -system--
#  r  b   ...      us sy id wa     in     cs
#  4  0            30 12 55  3   12000  85000   ← cs = context switches/sec
```

- `cs` — context switches per second (system-wide).
- `in` — interrupts per second.
- `r` — runnable tasks; if `r` consistently exceeds the number of CPUs, the run queue is backed up and involuntary switches climb.

```bash
pidstat -w 1                 # per-process voluntary (cswch/s) + involuntary (nvcswch/s)
pidstat -wt 1                # per-thread
mpstat -P ALL 1              # per-CPU %sys, plus %idle to spot a hot core
cat /proc/stat | grep ctxt   # total switches since boot
```

## Drilling In with perf

`perf sched` records every scheduling event and reconstructs run/wait timelines.

```bash
perf sched record -- sleep 5      # capture scheduler events
perf sched latency                # per-task scheduling latency (avg/max wait)
perf sched timehist               # event-by-event: when each task ran
perf stat -e context-switches,cpu-migrations,task-clock ./app
```

`cpu-migrations` is the count of times tasks moved between CPUs — each one is a cache-cold restart. High migrations alongside high `cs` argues for CPU pinning (T03).

## When Switching Becomes a Problem

```
throughput
   │        ╭───────╮
   │       ╱         ╲___      ← past optimal concurrency, more threads
   │      ╱              ╲___     = more switching = throughput collapse
   │     ╱                   ╲___
   └────┴────┴────┴────┴────┴────► number of runnable threads
        cores                  oversubscribed
```

Symptoms of **context-switch thrashing**:
- `cs` in the hundreds of thousands/sec with `%sys` high and `%us` (useful work) low.
- Adding threads *lowers* throughput.
- p99 latency balloons while average CPU looks "not full."

Common causes: thread pools sized far above core count, lock convoys (everyone wakes, one wins, rest re-block), busy-wait/spin loops, and interrupt storms.

## Interrupts: Hard IRQ, Soft IRQ, ksoftirqd

Hardware interrupts add involuntary switches too. The kernel splits interrupt work:

- **Hard IRQ** — minimal top-half, runs immediately at high priority.
- **Soft IRQ** — deferred bottom-half (network RX/TX, timers, block I/O completion).
- **ksoftirqd/N** — per-CPU kernel thread that drains soft IRQs when they pile up.

```bash
cat /proc/interrupts            # hard IRQ counts per CPU
cat /proc/softirqs              # soft IRQ counts (NET_RX, TIMER, ...)
top -H                          # watch ksoftirqd/N climb
mpstat -P ALL 1                 # %soft column = time in soft IRQs
```

On high-packet-rate hosts, `ksoftirqd` can dominate a CPU. Fixes: enable **RPS/RFS** to spread RX across cores, use **NAPI** (poll mode at high load), and pin NIC IRQs (T03).

## Reducing Switch Overhead

- **Size thread pools near core count** for CPU-bound work; oversizing only adds switches.
- **Batch syscalls / I/O** (`io_uring`, larger reads) to cut voluntary switches.
- **Pin hot tasks** to reduce migrations and keep caches warm.
- **Use lock-free / sharded structures** to break lock convoys.
- **Spread interrupts** (RPS/RFS, IRQ affinity) instead of letting one core soak them.

## Common Mistakes

- Looking only at total `cs` without splitting voluntary vs involuntary — they point to opposite problems.
- Adding worker threads to "use more CPU" when the bottleneck is already switch/lock overhead.
- Counting only the direct switch cost and ignoring the cache/TLB warm-up that dominates real impact.
- Blaming application code for high `%sys` when it's actually `ksoftirqd` from an interrupt storm.
- Assuming thread switches and process switches cost the same — process switches also swap the address space.

## Best Practices

- Track voluntary vs involuntary switch trends per service; alert on sudden involuntary spikes (CPU oversubscription).
- Right-size concurrency to cores; benchmark for the throughput knee rather than guessing.
- Pin latency-critical tasks and steer IRQs off their cores.
- Prefer event-driven / async I/O over thread-per-connection to cut voluntary switching at scale.
- Use `perf sched latency` to attribute tail latency to scheduler wait, not just CPU time.

## Quick Refs

```bash
# Per-process / per-thread switches
grep ctxt /proc/<pid>/status
pidstat -w 1                 # cswch/s (vol) + nvcswch/s (invol)
pidstat -wt 1                # per thread

# System-wide
vmstat 1                     # cs, in, r columns
mpstat -P ALL 1              # %sys, %soft, per-CPU
cat /proc/stat | grep ctxt   # total since boot

# Deep dive
perf sched record -- sleep 5
perf sched latency
perf sched timehist
perf stat -e context-switches,cpu-migrations ./app

# Interrupts
cat /proc/interrupts
cat /proc/softirqs
```

## Interview Prep

**Junior**: "What is a context switch?"
- Saving one task's CPU state and loading another's so the CPU can run a different task.

**Mid**: "Voluntary vs involuntary context switch?"
- Voluntary happens when a task blocks (I/O, lock, sleep); involuntary happens when the scheduler preempts it (time slice up, higher-priority wakeup, rebalance).

**Senior**: "Throughput dropped after we doubled the thread pool. Why?"
- Context-switch thrashing — more runnable threads than cores means time is spent switching and warming cold caches instead of doing work; the system passed the concurrency knee. Check `vmstat` `cs`/`r` and `pidstat -w`.

**Staff**: "On a 2M-packet/sec host, one core sits at 100% in ksoftirqd. How do you fix it without dropping packets?"
- Spread RX processing with RPS/RFS and multi-queue NIC + MSI-X IRQ affinity across cores, rely on NAPI polling at high load to coalesce interrupts, pin the IRQs off latency-critical cores, and verify with `/proc/softirqs` and `mpstat` `%soft` that load is now balanced.

## Next Chapter

→ Move to [L02/C05 — Filesystems & Storage](../C05/README.md)
