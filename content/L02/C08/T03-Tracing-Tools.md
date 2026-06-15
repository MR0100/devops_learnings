# L02/C08/T03 — Tracing Tools

## Learning Objectives

- Choose the right tracer for the job: profiler (`perf`), syscall tracer (`strace`/`ltrace`), or programmable tracing (`ftrace`, `bpftrace`)
- Run `perf` to profile on-CPU time and generate flame graphs
- Use `strace`/`ltrace` safely, understanding their overhead and when *not* to use them in production
- Drive `ftrace` and `bcc`/`bpftrace` for low-overhead, in-kernel observability

## The Tracing Tool Map

Tracers differ in **what** they observe and **how much** they cost:

| Tool | Observes | Mechanism | Overhead | Use in prod? |
|---|---|---|---|---|
| `perf` (sampling) | On-CPU stacks, PMU counters | Statistical sampling + hardware counters | Low | Yes, short bursts |
| `perf` (tracing) | Tracepoints, kprobes, uprobes | Event tracing to a ring buffer | Med | Carefully |
| `strace` | Syscalls of one process | `ptrace()` — stops process per syscall | **Very high (10–100×)** | Rarely / never |
| `ltrace` | Library calls | `ptrace()` / PLT breakpoints | **Very high** | No |
| `ftrace` | Kernel function calls, tracepoints | In-kernel ring buffer (`/sys/kernel/tracing`) | Low | Yes |
| `bpftrace` / `bcc` | Anything (kprobe/uprobe/tracepoint/USDT) | eBPF programs in-kernel | Very low | Yes |

Rule of thumb: **sample first** (`perf top`) to find *where* time goes, then **trace specific events** (`bpftrace`, `ftrace`) to understand *why*. Reach for `strace` only when you genuinely need the exact syscall arguments of a single, non-latency-sensitive process.

## perf — The Linux Profiler

`perf` samples the CPU at a fixed frequency and records the stack each time. Aggregate enough samples and the functions that appear most often are where the CPU spent its time.

```bash
perf top                            # live, system-wide on-CPU profile
perf record -F 99 -a -g sleep 30    # sample 99 Hz, all CPUs, call graphs, 30s
perf report                         # interactive report of the recording
perf report --stdio                 # text report
perf script | ./flamegraph.pl > out.svg   # render a flame graph
```

Why 99 Hz, not 100? An odd frequency avoids **lockstep** with periodic activity (timers that fire at 100 Hz), which would bias the sample. `-g` captures call graphs; on modern CPUs add `--call-graph dwarf` or compile with frame pointers so stacks unwind correctly.

`perf` also reads the hardware **Performance Monitoring Unit (PMU)** for counters you cannot get any other way:

```bash
$ perf stat -e cycles,instructions,cache-misses,branch-misses ./app
   1,204,553,019  cycles
     612,004,221  instructions   #  0.51 insn per cycle   <-- low IPC = stalled
      18,221,004  cache-misses
```

An **IPC (instructions per cycle) below ~1.0** signals the CPU is stalling — usually on memory (cache misses) — pointing you at a data-locality problem rather than raw compute.

## Flame Graphs

A flame graph turns thousands of `perf` stacks into one picture: the **x-axis is the fraction of samples** (wider = more CPU time), the **y-axis is stack depth**. You read it left-to-right looking for wide plateaus — those are your hot paths. Flame graphs are the fastest way to communicate "function X is eating 40% of CPU" to a team.

## strace — Syscall Tracing (Handle With Care)

`strace` shows every system call a process makes, with arguments and return values. It is invaluable for "why can't this process open that file?" and disastrous as a production profiler.

```bash
strace ./app                      # trace from launch
strace -p 1234                    # attach to a running PID
strace -f -p 1234                 # follow forked children/threads
strace -c -p 1234                 # SUMMARY: count + time per syscall
strace -e trace=openat,read,write ./app   # filter to specific syscalls
strace -e trace=network -p 1234   # filter by class (network/file/...)
strace -T -tt -p 1234             # show time-in-syscall + timestamps
```

The `-c` summary is the safest mode — it counts rather than printing every call:

```
$ strace -c -p 1234
% time     seconds  usecs/call     calls    errors syscall
 61.20    0.451200         902       500           futex
 28.10    0.207100          41      5012        12 read
  9.40    0.069300          17      4001           write
```

**Why strace is dangerous in prod:** it uses `ptrace()`, which stops the target on *every* syscall, traps into the tracer, and resumes it — adding two context switches per syscall. A busy process can slow down 10–100×, which can trip timeouts, health checks, and cascading failures. For syscall counts at scale, prefer `bpftrace` (next section) which runs in-kernel with negligible overhead.

## ltrace — Library Call Tracing

`ltrace` is `strace`'s cousin for **dynamic library calls** (and optionally syscalls). It's handy for debugging dynamic linking and seeing which `libc`/library functions a program calls:

```bash
ltrace ./app                  # trace library calls
ltrace -e 'malloc+free' ./app # filter to specific functions
ltrace -S ./app               # also show syscalls
```

Same `ptrace()` overhead caveat as `strace` — a debugging tool, not a production profiler.

## ftrace — The Built-in Kernel Tracer

`ftrace` lives in the kernel and is driven through `/sys/kernel/tracing` (or `tracefs`). It has near-zero overhead because it writes to an in-kernel ring buffer. The friendly front-end is Steven Rostedt's `trace-cmd`:

```bash
# function-graph tracer: see kernel call timing
trace-cmd record -p function_graph -g vfs_read sleep 1
trace-cmd report

# Raw tracefs (no trace-cmd):
cd /sys/kernel/tracing
echo function_graph > current_tracer
echo vfs_read > set_graph_function
cat trace_pipe        # live stream
echo nop > current_tracer   # stop
```

Useful built-in tracers: `function`, `function_graph` (call timing), and event tracing under `events/` (e.g., `events/sched/sched_switch`) for scheduler latency.

## bcc / bpftrace — Programmable Tracing

These are the modern default for production observability: eBPF programs attached to kprobes, uprobes, tracepoints, and USDT, aggregating in-kernel so almost nothing crosses to user space. (Deep dive in T04.)

```bash
# Count syscalls by process (the safe replacement for strace -c at scale)
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { @[comm] = count(); }'

# Who is calling vfs_read?
bpftrace -e 'kprobe:vfs_read { @[comm] = count(); }'

# Histogram of read() sizes returned
bpftrace -e 'tracepoint:syscalls:sys_exit_read { @ = hist(args->ret); }'
```

The `bcc` toolkit ships ready-made tools that are worth memorizing:

| Tool | What it shows |
|---|---|
| `opensnoop` | Every file open, live, with PID and path |
| `execsnoop` | Every new process exec (catches short-lived procs) |
| `biolatency` | Histogram of block I/O latency |
| `runqlat` | Histogram of CPU run-queue (scheduler) latency |
| `tcplife` / `tcpconnect` | TCP session lifetimes / new connections |
| `cachestat` | Page-cache hit/miss ratio |

## Common Mistakes

- **Using `strace`/`ltrace` on a hot production process.** The `ptrace()` overhead can slow it 10–100× and cause the very outage you're debugging. Use `bpftrace` or `perf` instead.
- **Sampling `perf` without call graphs or frame pointers.** Stacks come back as `[unknown]`; use `-g`/`--call-graph dwarf` and ensure binaries aren't compiled with omitted frame pointers.
- **Profiling at 100 Hz.** It can lockstep with timers; use 99 Hz to decorrelate.
- **Reading IPC in isolation.** Low IPC is a clue (likely memory stalls), not a verdict — confirm with `cache-misses`.
- **Forgetting `perf` needs privileges/symbols.** Without `perf_event_paranoid` lowered and debug symbols installed, you get partial data; on containers you often need to map the host kernel symbols.

## Best Practices

- Profile before you trace: `perf top` to find the hot path, then targeted `bpftrace`/`ftrace` for the why.
- Keep tracing windows short (`sleep 30`) and scoped (one PID, one tracepoint) to bound overhead.
- Prefer in-kernel aggregation (`bpftrace`, `bcc`, `ftrace`) over per-event user-space tracers in production.
- Install matching kernel debug symbols and use frame pointers / DWARF so stacks and flame graphs are readable.
- Build a flame graph for any CPU-bound regression — it's the clearest artifact to attach to a ticket or share with the team.

## Quick Refs

```bash
# perf — sample on-CPU and flame-graph it
perf top
perf record -F 99 -a -g sleep 30 ; perf report
perf script | ./flamegraph.pl > out.svg
perf stat -e cycles,instructions,cache-misses ./app

# strace — syscalls (low-traffic processes only)
strace -f -p <pid>
strace -c -p <pid>                 # summary counts (safest mode)
strace -e trace=openat,read ./app

# ltrace — library calls
ltrace -e 'malloc+free' ./app

# ftrace — built-in kernel tracer
trace-cmd record -p function_graph -g vfs_read sleep 1 ; trace-cmd report

# bpftrace / bcc — programmable, production-safe
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { @[comm] = count(); }'
opensnoop ; execsnoop ; biolatency ; runqlat
```

## Interview Prep

**Junior**: "What does `strace` do?" — It traces the system calls a process makes, showing each call's arguments and return value, which is great for debugging things like missing files or permission errors.

**Mid**: "Why shouldn't you `strace` a busy production service?" — `strace` uses `ptrace()` and stops the process on every syscall, adding context switches that can slow it 10–100×, so on a hot service it can trip timeouts and cause an outage; I'd use `bpftrace` for low-overhead syscall counts instead.

**Senior**: "How would you find what's burning CPU on a production host?" — `perf record -F 99 -a -g sleep 30`, then `perf script | flamegraph.pl` to get a flame graph; the widest plateaus are the hot paths, and I'd cross-check IPC with `perf stat` to see if it's compute-bound or stalling on memory.

**Staff**: "Compare sampling vs. tracing and when each is appropriate." — Sampling (`perf`) is statistical and cheap, ideal for "where does on-CPU time go" across a whole host; tracing (`ftrace`/`bpftrace`) captures specific events with arguments and is right for causal questions like I/O latency distributions or which process opens a file — I sample to localize, then trace to explain, and avoid `ptrace`-based tracers in production entirely.

## Next Topic

→ [T04 — eBPF](T04-eBPF.md)
