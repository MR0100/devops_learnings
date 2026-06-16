# L02/C08/T04 — eBPF

## Learning Objectives

- Explain the eBPF architecture: programs, the verifier, JIT, maps, and attach points
- Understand the attach surface (kprobes, uprobes, tracepoints, USDT, XDP, tc, LSM)
- Write and read `bpftrace` one-liners for production observability
- Place the major eBPF-based tools (Cilium, Falco, Tetragon, Pixie, Parca, BCC) in their use cases

## What eBPF Is

eBPF (extended Berkeley Packet Filter) lets you run **sandboxed programs inside the Linux kernel** without changing kernel source or loading a kernel module. You attach a small program to an event — a syscall, a function entry, a network packet, a tracepoint — and the kernel runs your code each time that event fires. It is the most important Linux observability and networking advance of the last decade because it gives you **safe, programmable, low-overhead** access to kernel internals.

The key properties:

- **Safe** — every program passes a verifier before it can load; it cannot crash or hang the kernel.
- **Programmable** — you decide what to measure and aggregate, instead of being limited to fixed counters.
- **Low overhead** — programs run in-kernel, aggregate into maps, and only summaries cross to user space. Tracepoints you don't attach to cost nothing.

## eBPF Architecture

```
   user space                         kernel
 ┌────────────┐   bpf()    ┌──────────────────────────────┐
 │ bpftrace / │──syscall──▶│  Verifier  ─▶  JIT compiler   │
 │ BCC / Go   │            │     │              │          │
 │ loader     │            │     ▼              ▼          │
 └─────┬──────┘            │  bytecode      native code    │
       │  read             │     attached to event ▼       │
       │  maps             │   ┌──────────────────────────┐│
       ◀───────────────────┼───│ kprobe│tracepoint│XDP│...││
                           │   └──────────────────────────┘│
                           │            │ writes           │
                           │            ▼                   │
                           │      eBPF MAPS (hash, array,   │
                           │      histogram, ring buffer)   │
                           └──────────────────────────────┘
```

1. **Program** — you write logic (in C compiled to eBPF bytecode, or in `bpftrace`'s high-level language). It's loaded via the `bpf()` syscall.
2. **Verifier** — statically proves the program **terminates** (no unbounded loops), only touches **valid memory**, and respects type/permission rules. If it can't prove safety, the program is rejected — this is what makes in-kernel code safe.
3. **JIT compiler** — translates verified bytecode to native machine code so it runs at near-native speed.
4. **Maps** — typed key/value data structures (hash, array, per-CPU, histogram, ring buffer, LRU) shared between the kernel program and user space. Aggregation happens here, in-kernel.
5. **Attach points / hooks** — where the program runs (below).

## The Attach Surface

| Hook | Fires on | Typical use |
|---|---|---|
| **kprobe / kretprobe** | Entry/return of (almost) any kernel function | Ad-hoc kernel tracing (`vfs_read`, `tcp_sendmsg`) |
| **tracepoint** | Stable, named kernel events | Preferred over kprobes — stable ABI (`syscalls:sys_enter_*`, `sched:sched_switch`) |
| **uprobe / uretprobe** | Entry/return of user-space functions | Trace your app's or libc's functions |
| **USDT** | Statically-defined app probes | Trace runtimes (JVM, Node) that ship USDT markers |
| **XDP** | Earliest point a packet hits the NIC driver | DDoS drop, load balancing (Cilium, Katran) |
| **tc (traffic control)** | Ingress/egress in the network stack | Packet filtering, policy, shaping |
| **LSM** | Kernel security hooks | Runtime security enforcement (KRSI) |

Prefer **tracepoints** over kprobes when one exists: tracepoints are a stable kernel ABI, while kprobes attach to internal function names that can change between kernel versions.

## bpftrace One-Liners

`bpftrace` is the awk of kernel tracing — a one-line program is often all you need. Structure is `probe { action }` with optional filters and aggregating map variables (`@`).

```bash
# Count syscalls by process name
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[comm] = count(); }'

# Histogram of block I/O latency (reimplements biolatency)
bpftrace -e 'kprobe:blk_account_io_start { @start[arg0] = nsecs; }
             kprobe:blk_account_io_done /@start[arg0]/ {
               @us = hist((nsecs - @start[arg0]) / 1000); delete(@start[arg0]); }'

# Files opened, live, with process and path
bpftrace -e 'tracepoint:syscalls:sys_enter_openat {
               printf("%-16s %s\n", comm, str(args->filename)); }'

# Run-queue latency: time threads wait for a CPU (scheduler health)
bpftrace -e 'tracepoint:sched:sched_wakeup { @qt[args->pid] = nsecs; }
             tracepoint:sched:sched_switch /@qt[args->next_pid]/ {
               @usecs = hist((nsecs - @qt[args->next_pid]) / 1000);
               delete(@qt[args->next_pid]); }'

# Per-second new TCP connections by destination
bpftrace -e 'kprobe:tcp_connect { @[comm] = count(); } interval:s:1 { print(@); clear(@); }'
```

Reading the output: aggregating functions are the point. `count()` totals, `hist()` produces a power-of-two histogram, `lhist()` a linear one, `stats()`/`avg()`/`max()` summarize — all computed **in the kernel**, so a one-liner that would be impossibly expensive with `strace` runs with negligible overhead.

```
@usecs:
[2, 4)        18 |@@@                                    |
[4, 8)       240 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[8, 16)       62 |@@@@@@@@@@                             |
[16, 32)       4 |                                       |
```

## The eBPF Tool Ecosystem

eBPF underpins a whole generation of infrastructure tools. Knowing which is which is common interview fodder:

| Tool | Domain | What it does with eBPF |
|---|---|---|
| **BCC** | Observability | Toolkit + Python/C framework (`opensnoop`, `biolatency`, `runqlat`) |
| **bpftrace** | Observability | High-level tracing language for one-liners and short scripts |
| **Cilium** | Networking | eBPF-based CNI: service routing, network policy, load balancing |
| **Falco** | Security | Runtime threat detection from syscall events |
| **Tetragon** | Security | eBPF security observability + in-kernel enforcement |
| **Pixie** | Observability | Auto-instrumented app/protocol telemetry, no code changes |
| **Parca** | Profiling | Continuous, always-on whole-fleet CPU profiling |
| **Katran** | Networking | XDP-based L4 load balancer (Meta) |

Use-case mapping: **networking** → Cilium/Katran (XDP/tc), **security** → Falco/Tetragon (syscalls/LSM), **observability** → Pixie/BCC/bpftrace, **profiling** → Parca/perf+eBPF.

## Requirements and Limits

- Needs a reasonably modern kernel (4.x+ for basics; 5.x+ for the good stuff like BTF/CO-RE). **CO-RE (Compile Once, Run Everywhere)** with **BTF** lets a compiled eBPF program run across kernel versions without recompiling against each kernel's headers.
- Loading programs requires `CAP_BPF` / `CAP_SYS_ADMIN` (privileged).
- The verifier imposes limits: bounded loops only, a finite instruction/complexity budget, and restricted helper functions. Very complex programs can be rejected.
- It observes the **kernel's** view; for fine-grained app logic you still combine it with uprobes/USDT.

## Common Mistakes

- **Attaching to kprobes when a tracepoint exists.** Kprobe targets are internal function names that break across kernel versions; tracepoints are a stable ABI.
- **Expecting eBPF on ancient kernels.** Pre-4.x kernels lack the modern eBPF surface; CO-RE/BTF needs 5.x+. Check `uname -r` first.
- **Forgetting privileges.** Loading programs needs `CAP_BPF`/`CAP_SYS_ADMIN`; it silently does nothing useful unprivileged.
- **Aggregating in user space.** The whole point is in-kernel maps; printing every event to user space throws away eBPF's overhead advantage.
- **Assuming zero risk.** The verifier prevents crashes, but a busy probe on a hot function still adds per-event cost — scope your probes.

## Best Practices

- Prefer `tracepoint:` over `kprobe:` for stability across kernel upgrades.
- Aggregate with `@` maps (`count`, `hist`, `stats`) in-kernel; only summarize to user space.
- Use CO-RE/BTF tooling (libbpf, BCC's newer builds) so probes are portable across the fleet's kernel versions.
- Start from the BCC toolkit and `bpftrace` one-liners before writing custom C programs — they cover most needs.
- Scope probes tightly (one function, one PID, short window) on hot paths to keep overhead negligible.

## Quick Refs

```bash
uname -r                              # check kernel version (need 5.x+ for CO-RE/BTF)
bpftool prog show                     # list loaded eBPF programs
bpftool map show                      # list eBPF maps

# bpftrace one-liners
bpftrace -l 'tracepoint:syscalls:*'   # list available probes
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { @[comm]=count(); }'
bpftrace -e 'kprobe:vfs_read { @[comm]=count(); }'
bpftrace -e 'tracepoint:syscalls:sys_exit_read { @=hist(args->ret); }'

# BCC ready-made tools
opensnoop ; execsnoop ; biolatency ; runqlat ; tcplife ; cachestat
```

```
eBPF pipeline:  program → verifier → JIT → attach to hook → write maps → read from user space
hooks: kprobe | tracepoint | uprobe | USDT | XDP | tc | LSM
tools: BCC/bpftrace (obs) · Cilium/Katran (net) · Falco/Tetragon (sec) · Pixie/Parca (obs/profiling)
```

## Interview Prep

**Junior**: "What is eBPF in one sentence?" — It lets you run small, sandboxed programs inside the Linux kernel to observe or modify behavior (tracing, networking, security) without writing a kernel module.

**Mid**: "What makes eBPF safe to run in the kernel?" — Every program goes through a verifier that statically proves it terminates, only accesses valid memory, and uses allowed helpers, then it's JIT-compiled; if safety can't be proven the program is rejected, so it can't crash or hang the kernel.

**Senior**: "Why prefer a tracepoint over a kprobe, and how does eBPF stay low-overhead?" — Tracepoints are a stable kernel ABI while kprobes attach to internal function names that change between versions; overhead stays low because the program runs in-kernel and aggregates into maps (count/hist), so only summaries cross to user space instead of per-event data.

**Staff**: "Where does eBPF fit across networking, security, and observability in a platform?" — Networking via Cilium/Katran on XDP/tc for policy and L4 load balancing, security via Falco/Tetragon on syscalls and LSM hooks for runtime detection and enforcement, and observability/profiling via Pixie/BCC/bpftrace and Parca; I'd standardize on CO-RE/BTF so probes are portable across the fleet's kernels and treat eBPF as the common substrate rather than bolting on separate agents.

## Next Topic

→ [T05 — Kernel Tuning Knobs](T05-Tuning-Knobs.md)
