# L02/C04/T02 — Nice, Priority, Real-Time Classes

## Learning Objectives

- Map the Linux scheduling-class hierarchy and where normal vs real-time tasks fit
- Use `nice`/`renice` and `chrt` to change priority and scheduling policy
- Understand the dangers of real-time priorities (starvation, RT throttling) and when to use them

## Scheduling Classes (Priority Order)

The kernel checks classes top-to-bottom; a higher class always preempts a lower one.

```
┌──────────────────────────────────────────────┐
│ stop_sched_class   (kernel internal, migration)│  highest
│ dl_sched_class     SCHED_DEADLINE              │
│ rt_sched_class     SCHED_FIFO, SCHED_RR        │
│ fair_sched_class   SCHED_OTHER, SCHED_BATCH    │
│ idle_sched_class   SCHED_IDLE                  │  lowest
└──────────────────────────────────────────────┘
```

| Policy | Class | Priority range | Behavior |
|---|---|---|---|
| `SCHED_DEADLINE` | deadline | (runtime, deadline, period) | Earliest-deadline-first; admission-controlled |
| `SCHED_FIFO` | real-time | rtprio 1–99 | Runs until it blocks or yields; no time slice |
| `SCHED_RR` | real-time | rtprio 1–99 | Like FIFO but round-robins same-priority tasks |
| `SCHED_OTHER` | normal (CFS) | nice -20…+19 | Fair share, the default |
| `SCHED_BATCH` | normal (CFS) | nice -20…+19 | CPU-bound, no wakeup preemption |
| `SCHED_IDLE` | idle | — | Runs only when nothing else wants the CPU |

## Nice Values (SCHED_OTHER)

Nice ranges from **-20 (highest priority)** to **+19 (lowest)**, default **0**. Each step changes the task's CFS weight by ~1.25×, which works out to roughly a **10% CPU share difference** per step between two competing tasks.

```bash
nice -n 10 ./backup.sh          # start a low-priority job
renice -n 5 -p 1234             # change a running PID
renice -n -5 -u postgres        # all of a user's processes
ps -eo pid,ni,pri,comm | head   # NI = nice, PRI = kernel priority
```

- Only **root** (or `CAP_SYS_NICE`) can set a *negative* nice (raise priority).
- The "priority numbers" in `top`/`ps` (`PRI`) are an internal mapping: for normal tasks `PRI = 20 + nice` shown as 0–39, or `RT`/negative for real-time tasks. Don't confuse `PRI` with `nice`.

```
nice  -20 ─────────────────────────► +19
share  high                         low
weight 88761  ...  1024 (nice 0) ...  15
```

## Real-Time Policies (SCHED_FIFO / SCHED_RR)

Real-time tasks have **static** priorities 1–99 and always preempt every normal task. They do **not** use `vruntime`.

```bash
# Run a command as FIFO priority 50
chrt -f 50 ./low-latency-engine

# Inspect / change a running task
chrt -p 1234                    # show class + rtprio
chrt -f -p 80 1234              # set FIFO prio 80
chrt -r -p 10 1234              # set RR prio 10
chrt -o -p 0 1234               # back to SCHED_OTHER (normal)
```

- `SCHED_FIFO`: a task runs until it blocks, yields (`sched_yield`), or is preempted by a *higher* RT priority. A busy-looping FIFO task can **starve everything else on that CPU**, including kernel threads.
- `SCHED_RR`: same, but tasks at the *same* priority round-robin with a quantum (`sched_rr_timeslice_ms`, default 100 ms).

### RT Throttling — The Safety Net

To prevent a runaway RT task from locking up the box, the kernel reserves a slice of CPU for non-RT work:

```bash
sysctl kernel.sched_rt_period_us     # 1000000  (1 s window)
sysctl kernel.sched_rt_runtime_us    # 950000   (RT may use 950 ms)
```

So by default RT tasks can consume at most **95%** of each CPU-second; the remaining 5% keeps CFS and kernel threads alive. Setting `sched_rt_runtime_us = -1` disables the throttle (dangerous — a buggy RT task then truly hangs the system).

## SCHED_DEADLINE

EDF-based, for tasks with explicit timing needs. Each task declares `(runtime, deadline, period)` and the kernel runs **admission control** — it refuses the policy change if the new task would overcommit the CPU.

```bash
chrt -d --sched-runtime 10000000 \
        --sched-deadline 30000000 \
        --sched-period 30000000 0 ./control-loop
```

Use it for periodic control loops where "must finish within X" matters more than "highest priority". Deadline outranks FIFO/RR.

## SCHED_IDLE and SCHED_BATCH

- `SCHED_BATCH`: marks a CPU-bound task so CFS skips wakeup preemption — good for compile farms / batch crunchers that shouldn't disturb interactive latency.
- `SCHED_IDLE`: extreme low priority; runs only when the box is otherwise idle. Lower effective weight than nice +19.

```bash
chrt -b 0 ./compile-everything     # SCHED_BATCH
chrt -i 0 ./scavenger              # SCHED_IDLE
```

## Real-Time vs Nice — When to Use What

| Goal | Tool |
|---|---|
| "This job is less important, yield to others" | `nice +N` / `SCHED_IDLE` |
| "This job should get more share but stay fair" | `nice -N` (small negative) |
| "Bounded wakeup latency, audio/control/trading" | `SCHED_FIFO`/`SCHED_RR` + pinning |
| "Hard periodic deadline with admission control" | `SCHED_DEADLINE` |

Reach for RT only when you genuinely need bounded latency and you have isolated CPUs for it. On a shared node, a misconfigured `SCHED_FIFO` priority is one of the fastest ways to wedge the whole machine.

## Common Mistakes

- Treating `nice -20` as "real-time" — it's still CFS and still yields to any RT task.
- Running `SCHED_FIFO` on a CPU that also hosts `ksoftirqd`/kernel threads, then wondering why the network stalls.
- Disabling RT throttling (`sched_rt_runtime_us = -1`) "for performance" and hanging the host on the first RT bug.
- Forgetting that negative nice / RT policies need root or `CAP_SYS_NICE`; the call silently fails to elevate.
- Confusing the `PRI` column in `ps`/`top` with the nice value.

## Best Practices

- Default to nice tuning; escalate to RT only with a measured latency requirement.
- Pin RT tasks to dedicated, `isolcpus`-reserved cores so they never fight kernel threads.
- Keep RT throttling enabled; tune `sched_rt_runtime_us` rather than removing it.
- Grant `CAP_SYS_NICE` narrowly (systemd `AmbientCapabilities`) instead of running services as root.
- Prefer `SCHED_DEADLINE` over high FIFO priorities when the requirement is "finish by T", because admission control prevents overload.

## Quick Refs

```bash
# Nice / renice (CFS)
nice -n 10 ./job
renice -n -5 -p 1234
renice -n 5 -u builduser
ps -eo pid,ni,pri,cls,comm        # NI, PRI, scheduling CLaSs

# Real-time / class changes
chrt -p 1234                      # show policy + priority
chrt -f 80 ./engine               # SCHED_FIFO prio 80
chrt -r 10 ./worker               # SCHED_RR  prio 10
chrt -o -p 0 1234                 # back to SCHED_OTHER
chrt -b 0 ./batch                 # SCHED_BATCH
chrt -i 0 ./idle                  # SCHED_IDLE

# RT throttle safety net
sysctl kernel.sched_rt_period_us
sysctl kernel.sched_rt_runtime_us
```

## Interview Prep

**Junior**: "What does `nice` do?"
- Adjusts a normal task's CFS priority from -20 (more CPU) to +19 (less CPU); each step is roughly a 10% share change.

**Mid**: "Difference between SCHED_FIFO and SCHED_RR?"
- Both are fixed-priority real-time; FIFO runs until it blocks/yields, RR adds a time quantum so tasks of the *same* priority round-robin.

**Senior**: "A SCHED_FIFO task pegged a core and the box froze. Why, and what protects against it?"
- A busy FIFO task preempts all normal and kernel threads on that CPU; RT throttling (`sched_rt_runtime_us`/`period_us`) reserves ~5% per CPU-second for non-RT work, which is why it usually doesn't *fully* freeze unless throttling is disabled.

**Staff**: "Design priority assignment for a mixed trading + telemetry + batch workload on one node."
- Isolate cores with `isolcpus`/`nohz_full` for the latency engine, pin it via affinity and run it `SCHED_FIFO` (or `SCHED_DEADLINE` for periodic loops), keep telemetry on CFS with modest negative nice, demote batch to `SCHED_BATCH`/`SCHED_IDLE`, and keep RT throttling on as a guardrail.

## Next Topic

→ [T03 — CPU Affinity](T03-CPU-Affinity.md)
