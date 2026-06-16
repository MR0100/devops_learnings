# L02/C08 — Performance & Observability

## Chapter Overview

This chapter teaches you to diagnose any Linux performance issue with first-principles tools: USE/RED methods, perf, strace, bpftrace, eBPF.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-USE-Method.md) | USE Method (Utilization, Saturation, Errors) | 1 hr |
| [T02](T02-RED-Method.md) | RED Method (Rate, Errors, Duration) | 0.5 hr |
| [T03](T03-Tracing-Tools.md) | perf, strace, ltrace, bpftrace | 2 hr |
| [T04](T04-eBPF.md) | eBPF: The New Frontier | 1.5 hr |
| [T05](T05-Tuning-Knobs.md) | Performance Tuning Knobs (sysctl, ulimits, IO schedulers) | 1 hr |

## USE Method (Brendan Gregg)

For every resource (CPU, memory, disk, network), check three metrics:

| Metric | Definition |
|---|---|
| Utilization | % time busy |
| Saturation | Queue length / overflow |
| Errors | Error events |

### Tools by Resource

| Resource | U | S | E |
|---|---|---|---|
| CPU | `vmstat`, `top` | run-queue length (`vmstat` r col) | nothing useful |
| Memory | `vmstat`, `free` | swap I/O, OOM kills | dmesg |
| Disk | `iostat` (%util) | `iostat -x` (aqu-sz) | `dmesg`, SMART |
| Network | `sar -n`, `nstat` | drops, retransmits | `ip -s link` |

## RED Method (Tom Wilkie)

For every service:
- **Rate** — requests per second
- **Errors** — errors per second
- **Duration** — distribution of latencies

USE is for resources; RED is for services. Use together.

## Tracing Tools

### perf
- The Linux profiler. Sample CPU at intervals.
```bash
perf top                          # live
perf record -F 99 -a -g sleep 30  # 30-sec system-wide flame
perf report
perf script | flamegraph.pl > out.svg
perf stat -e cache-misses,cycles  cmd
```

### strace
- Trace syscalls of a process.
```bash
strace -p 1234                 # attach
strace -c -p 1234              # count syscalls
strace -e openat,read,write ./app  # filter
strace -f ./app                # follow forks
```
Heavy overhead — use sparingly in production.

### ltrace
- Like strace, but for library calls. Useful for debugging dynamic linking.

### bpftrace
- High-level eBPF tracing language.
```bash
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { @[comm] = count(); }'
bpftrace -e 'kprobe:vfs_read { @[comm] = count(); }'
bcc-tools also useful: opensnoop, execsnoop, biolatency, runqlat
```

### eBPF
The most important Linux observability advance of the decade. Programmable in-kernel tracing.

- Tools built on eBPF: BCC, bpftrace, Cilium, Falco, Tetragon, Pixie
- Use cases: networking (Cilium), security (Falco), observability (Pixie), profiling (Parca)
- Zero overhead for tracepoints not hit

## Performance Tuning Knobs

### sysctl
Common production tweaks:
```
# /etc/sysctl.d/99-tune.conf
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_tw_reuse = 1
net.netfilter.nf_conntrack_max = 1048576
vm.swappiness = 10
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
```

### ulimits
- File descriptors (`nofile`)
- Processes (`nproc`)
- Locked memory (`memlock`)
- Stack size

`/etc/security/limits.conf` (PAM) or systemd `LimitNOFILE=`

### I/O Schedulers
- `none` / `noop` — for NVMe (modern default)
- `mq-deadline` — multi-queue deadline
- `kyber` — modern, low-latency
- `bfq` — fairness; can hurt throughput

```bash
cat /sys/block/sda/queue/scheduler
echo none > /sys/block/sda/queue/scheduler
```

For SSDs/NVMe, `none` is usually best.

### CPU Governor
- `performance` — max freq always (servers, low-latency)
- `powersave`, `ondemand`, `schedutil`

```bash
cpupower frequency-info
cpupower frequency-set -g performance
```

## Interview Themes

- "Walk me through diagnosing a slow service using USE and RED."
- "What's eBPF and what would you use it for?"
- "Tune a Linux host for high TCP connection rate."
- "We have 500K open files — what could go wrong?"
