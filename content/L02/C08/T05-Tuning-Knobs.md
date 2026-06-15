# L02/C08/T05 — Kernel Tuning Knobs

## Learning Objectives

- Tune the kernel safely with `sysctl` and persist changes in `/etc/sysctl.d/`
- Know the high-impact knobs: `vm.swappiness`, `vm.dirty_*`, `net.core.somaxconn`, `net.ipv4.tcp_*`, `fs.file-max`
- Raise per-process limits with `ulimit` / `limits.conf` / systemd, and pick the right I/O scheduler and CPU governor
- Tune from a measured bottleneck (USE/RED), never by copy-pasting "magic" configs

## Tuning Workflow (Measure First)

The cardinal rule: **never tune a knob you can't tie to a measured bottleneck.** Copy-pasted "performance configs" routinely make things worse. The loop is: measure with USE/RED → form a hypothesis → change one knob → measure again → keep or revert. Tuning blindly hides the real problem and creates configuration drift no one understands.

`sysctl` reads/writes kernel parameters exposed under `/proc/sys/`:

```bash
sysctl vm.swappiness               # read one value
sysctl -a                          # dump everything
sysctl -w vm.swappiness=10         # set at runtime (NOT persistent)
echo 10 > /proc/sys/vm/swappiness  # equivalent runtime write
```

Persist changes in a drop-in file (survives reboot, and keeps your changes separate from distro defaults):

```bash
# /etc/sysctl.d/99-tune.conf
vm.swappiness = 10
net.core.somaxconn = 65535

sysctl --system            # reload all sysctl.d files now
```

## Memory & VM Knobs

| Knob | Default | Tuned | Effect |
|---|---|---|---|
| `vm.swappiness` | 60 | 1–10 | How aggressively the kernel swaps anon pages vs. reclaiming page cache. Lower = avoid swap. **0 doesn't fully disable swap** (it still swaps to avoid OOM). |
| `vm.dirty_ratio` | 20 | 10 | % of RAM that can hold dirty pages before *writers block* and flush synchronously. Lower bounds write-storm latency spikes. |
| `vm.dirty_background_ratio` | 10 | 5 | % dirty at which the kernel starts flushing *in the background* (async). Keep below `dirty_ratio`. |
| `vm.overcommit_memory` | 0 (heuristic) | 0/1/2 | Allocation policy. `2` = strict (no overcommit, respects `CommitLimit`). |
| `vm.max_map_count` | 65530 | 262144+ | Max memory map areas per process. Elasticsearch and some JVM/DB workloads need it raised. |

The `dirty_*` pair governs write-back. If `Dirty` in `/proc/meminfo` (see C03/T05) grows large, a sudden flush stalls writers; lowering `vm.dirty_ratio` trades a little throughput for far smoother, more predictable write latency on database hosts.

## Network Knobs (High Connection-Rate Servers)

```bash
# /etc/sysctl.d/99-net.conf
net.core.somaxconn          = 65535   # max queued accepted conns (listen backlog cap)
net.ipv4.tcp_max_syn_backlog = 65535  # max half-open (SYN_RECV) conns
net.core.netdev_max_backlog = 16384   # packets queued at the NIC before the stack
net.ipv4.tcp_tw_reuse       = 1       # reuse TIME_WAIT sockets for new outbound conns
net.ipv4.tcp_fin_timeout    = 15      # shorten FIN_WAIT2 hold time
net.ipv4.ip_local_port_range = 1024 65535   # widen ephemeral port range
net.netfilter.nf_conntrack_max = 1048576     # conntrack table size (if using netfilter)
net.ipv4.tcp_slow_start_after_idle = 0       # don't reset cwnd on idle (keep-alive perf)
```

The two most misunderstood:

- **`net.core.somaxconn`** caps the *completed*-connection backlog (the accept queue). If your app's `listen(fd, backlog)` asks for more than `somaxconn`, it's silently clamped — so you must raise both the sysctl **and** the app's backlog. A full accept queue drops connections and shows up as client connection timeouts.
- **`tcp_tw_reuse`** lets the kernel reuse a socket in `TIME_WAIT` for a new *outbound* connection, helping clients/proxies that open huge numbers of short-lived connections exhaust fewer ephemeral ports. (Note: the old `tcp_tw_recycle` was **removed** in 4.12 — it broke NAT; do not look for it.)

Watch the symptoms these fix:

```bash
ss -s                         # socket summary, TIME_WAIT count
ss -ltn                       # listening sockets + Recv-Q/Send-Q (accept-queue depth)
nstat -az | grep -i listendrop  # ListenOverflows/ListenDrops = somaxconn too small
```

## File Descriptor Knobs

Two layers must both be raised — system-wide and per-process:

```bash
# /etc/sysctl.d/99-fs.conf
fs.file-max = 2097152                 # system-wide max open file handles
fs.nr_open  = 1048576                 # per-process hard ceiling for nofile
fs.inotify.max_user_watches = 524288  # for file-watchers (IDEs, log shippers, k8s)
```

`fs.file-max` is the **kernel-wide** ceiling; the **per-process** limit is `ulimit -n` (`RLIMIT_NOFILE`), and it must be raised separately or processes hit "Too many open files" long before the system limit:

```bash
ulimit -n                  # current soft limit for this shell
ulimit -n 1048576          # raise soft limit (up to the hard limit)
cat /proc/<pid>/limits     # see a running process's actual limits
```

Persist per-process limits via PAM `limits.conf`:

```
# /etc/security/limits.conf
*  soft  nofile  1048576
*  hard  nofile  1048576
appuser  soft  nproc   65535
appuser  hard  memlock unlimited
```

For **systemd-managed services**, `limits.conf` is *not* applied — set them in the unit instead:

```ini
# [Service] section of the unit (or a drop-in)
LimitNOFILE=1048576
LimitNPROC=65535
LimitMEMLOCK=infinity
```

Common `ulimit` targets: `nofile` (file descriptors), `nproc` (processes/threads), `memlock` (locked pages — databases, eBPF), `stack` (stack size), `core` (core dump size).

## I/O Schedulers

The block-layer scheduler decides the order I/O requests are dispatched. Modern kernels use the multi-queue (blk-mq) schedulers:

| Scheduler | Best for | Notes |
|---|---|---|
| `none` (`noop`) | NVMe / fast SSD | No reordering; the device's own parallelism does the work. Usual NVMe default. |
| `mq-deadline` | General SSD/HDD | Deadline-based; bounds worst-case latency. Good safe default. |
| `kyber` | Low-latency SSD | Lightweight, latency-targeted. |
| `bfq` | Desktop / fairness | Per-process fairness; can cost throughput on servers. |

```bash
cat /sys/block/nvme0n1/queue/scheduler     # [none] mq-deadline kyber bfq
echo none > /sys/block/nvme0n1/queue/scheduler   # set (non-persistent)
```

For SSD/NVMe, `none` is usually best — the drive's internal controller schedules better than the kernel can. Persist via a udev rule so it survives reboot:

```
# /etc/udev/rules.d/60-ioscheduler.rules
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="none"
```

## CPU Frequency Governor

The governor controls how the CPU scales clock speed. For latency-sensitive servers, `performance` keeps cores at max frequency and avoids the latency cost of ramping up:

```bash
cpupower frequency-info                    # current governor + range
cpupower frequency-set -g performance      # pin to max frequency
```

| Governor | Behavior |
|---|---|
| `performance` | Always max frequency (servers, low-latency, databases) |
| `powersave` | Min frequency / energy-saving (laptops; on intel_pstate it's actually fine) |
| `ondemand` / `schedutil` | Scale with load (`schedutil` is the modern scheduler-driven default) |

## Common Mistakes

- **`vm.swappiness=0` to "disable swap".** It doesn't — the kernel still swaps to avoid OOM. To truly disable, `swapoff -a`, and be sure you have the RAM headroom.
- **Raising `somaxconn` but not the app backlog.** The `listen()` backlog is clamped to `somaxconn`; both must change or the accept queue still overflows.
- **Setting `ulimit -n` high but using systemd.** `limits.conf` is ignored for systemd services — you must set `LimitNOFILE=` in the unit.
- **Copying a "tuned" sysctl gist wholesale.** Knobs like `tcp_tw_recycle` (removed, broke NAT) or wrong `dirty_ratio` cause subtle outages. Tune from a measured bottleneck.
- **Runtime-only changes.** `sysctl -w` and `echo > /sys` are lost on reboot — persist in `/etc/sysctl.d/`, udev rules, or systemd.

## Best Practices

- Tune from evidence: tie every knob change to a USE/RED symptom, change one at a time, and re-measure.
- Persist everything: `/etc/sysctl.d/*.conf` for sysctls, udev rules for I/O schedulers, systemd unit limits for FD/nproc.
- Set `vm.swappiness` low (1–10) and bound `vm.dirty_ratio` on database/latency-sensitive hosts.
- Raise file-descriptor limits at **both** layers (`fs.file-max` and per-process `nofile`) and verify with `/proc/<pid>/limits`.
- Use `none`/`mq-deadline` for SSD/NVMe and the `performance` governor for latency-critical servers; document why each non-default knob is set.

## Quick Refs

```bash
# sysctl
sysctl vm.swappiness ; sysctl -a
sysctl -w vm.swappiness=10              # runtime only
sysctl --system                          # reload /etc/sysctl.d/*

# memory / vm
vm.swappiness=10  vm.dirty_ratio=10  vm.dirty_background_ratio=5  vm.max_map_count=262144

# network (high conn-rate)
net.core.somaxconn=65535  net.ipv4.tcp_max_syn_backlog=65535
net.ipv4.tcp_tw_reuse=1   net.ipv4.ip_local_port_range="1024 65535"
ss -s ; ss -ltn ; nstat -az | grep -i listendrop

# file descriptors
fs.file-max=2097152
ulimit -n 1048576 ; cat /proc/<pid>/limits
# /etc/security/limits.conf : "* hard nofile 1048576"
# systemd unit            : "LimitNOFILE=1048576"

# I/O scheduler & CPU governor
cat /sys/block/nvme0n1/queue/scheduler ; echo none > /sys/block/nvme0n1/queue/scheduler
cpupower frequency-set -g performance
```

## Interview Prep

**Junior**: "How do you change a kernel parameter and make it stick?" — Set it at runtime with `sysctl -w key=value`, then persist it by adding `key = value` to a file in `/etc/sysctl.d/` and running `sysctl --system` so it survives reboot.

**Mid**: "What does `vm.swappiness` do and what value would you pick on a server?" — It controls how aggressively the kernel swaps anonymous memory versus reclaiming page cache; on a server I set it low (1–10) to avoid swapping under cache pressure, knowing `0` still swaps to avoid OOM rather than fully disabling it.

**Senior**: "Tune a host for a very high TCP connection rate." — Raise `net.core.somaxconn` and `tcp_max_syn_backlog` (and the app's `listen()` backlog to match), widen `ip_local_port_range`, enable `tcp_tw_reuse`, bump `netdev_max_backlog`, and raise `fs.file-max` plus per-process `nofile`; then verify with `ss -ltn` accept-queue depth and `nstat` ListenOverflows that the backlog is no longer dropping.

**Staff**: "How do you approach performance tuning across a fleet without causing regressions?" — Every knob is tied to a measured USE/RED bottleneck and changed one at a time with before/after metrics; changes are codified (sysctl.d, udev, systemd limits) and version-controlled rather than hand-applied, defaults are documented with rationale, and I avoid cargo-culted configs (e.g. removed `tcp_tw_recycle`) because the goal is predictable, reproducible hosts — not maximal numbers on one box.

## Next Chapter

→ Move to [L02/C09 — Linux Security](../C09/README.md)
