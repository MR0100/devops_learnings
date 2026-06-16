# L02/C08/T01 — The USE Method

## Learning Objectives

- Apply Brendan Gregg's USE method (Utilization, Saturation, Errors) to any hardware resource
- Build a resource → tool checklist so you reach for the right command in seconds
- Read real `vmstat`, `iostat`, `mpstat`, and `sar` output and turn numbers into a diagnosis
- Know when USE points at a resource bottleneck vs. a software/service problem

## What the USE Method Is

The USE method is a checklist for system bottlenecks. For **every resource**, you check three metrics:

| Metric | Definition | What "bad" looks like |
|---|---|---|
| **Utilization** | The percentage of time the resource was busy servicing work | Sustained near 100% (for a single-server resource) |
| **Saturation** | The degree of queued/extra work the resource cannot service yet | A growing queue, run-queue, or backlog |
| **Errors** | The count of error events | Any non-zero, ideally |

The power of USE is **completeness and speed**: instead of randomly sampling metrics, you enumerate the resources (CPU, memory, disk, network, and their interconnects) and tick three boxes each. It catches the resource that is actually the bottleneck instead of the one that happens to be on your dashboard.

Utilization can be measured two ways. **Time-based**: percent of an interval the resource was busy (a single disk at 90% util is busy 90% of the time). **Capacity-based**: percent of a resource's total capacity in use (a disk that is 90% full). A resource at 100% time-based utilization is usually a bottleneck; a resource that is only 70% utilized *on average* can still be saturated in bursts, which is why you always check saturation too.

## The USE Checklist (per resource)

| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| **CPU** | `vmstat` (`us`+`sy`), `mpstat -P ALL`, `top` | run-queue length: `vmstat` `r` column, `sar -q` | rare; thermal throttle, `mcelog` |
| **Memory (capacity)** | `free -m`, `/proc/meminfo` `MemAvailable` | swap in/out (`vmstat` `si`/`so`), page-scan, OOM kills | `dmesg` (OOM, EDAC ECC errors) |
| **Disk I/O** | `iostat -xz 1` (`%util`) | `iostat -x` (`aqu-sz`, await), `vmstat` `b` (blocked) | `dmesg`, SMART (`smartctl -a`) |
| **Disk capacity** | `df -h`, `df -i` (inodes) | n/a (a full disk just ENOSPCs) | n/a |
| **Network** | `sar -n DEV 1` (% of link speed), `nstat` | drops, `nstat TcpRetransSegs`, `ss -ti` | `ip -s link` (errors/drops), `nstat` |

When you sit down to a "slow box", walk this table top to bottom. The first resource that shows high utilization **with** saturation, or any errors, is your prime suspect.

## CPU — Reading the Numbers

`vmstat 1` is the fastest CPU triage tool. The interesting columns:

```
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 8  0      0 412300  93120 6231004    0    0     2    18 1450 2900 71 18  9  2  0
```

- `r` — processes runnable (running + waiting for a CPU). **This is CPU saturation.** If `r` consistently exceeds the number of vCPUs, threads are queueing for the CPU.
- `us`/`sy` — user/system CPU time. `us`+`sy` near 100% with `id` near 0 is high utilization.
- `wa` — waiting on I/O. High `wa` means the CPU is *idle waiting for disk*, which redirects you to the disk row.
- `st` — steal time. On a VM, `st` > 0 means the hypervisor gave your vCPU to someone else — a noisy-neighbor signal.

Per-CPU view to spot a single hot core (a single-threaded bottleneck hides in the average):

```
$ mpstat -P ALL 1
CPU    %usr   %sys %iowait  %irq  %soft  %idle
all   18.50   4.20    1.10  0.00   0.30  75.90
  0   99.00   1.00    0.00  0.00   0.00   0.00   <-- one core pinned
  1    2.00   1.00    0.50  0.00   0.10  96.40
```

## Memory — Capacity and Saturation

For memory, *utilization* is the capacity question (covered in `/proc/meminfo`), but **saturation is what hurts**. Memory saturation shows up as paging/swapping and as the OOM killer firing:

```
$ vmstat 1
 r  b   swpd   free  ...  si   so ...
 2  1 524288  18000      8240 12100   <-- si/so non-zero = swapping = saturation
```

`si` (swap-in) and `so` (swap-out) being non-zero means the system is paging anonymous memory to disk — a strong saturation signal. Confirm OOM events and ECC memory errors in the ring buffer:

```
$ dmesg -T | grep -iE 'killed process|out of memory|edac'
[Mon Jun 15 09:12:44 2026] Out of memory: Killed process 23110 (java) total-vm:8123400kB
```

## Disk I/O — `iostat -xz 1`

This is the single most useful storage command. The `z` skips idle devices, `x` gives extended stats:

```
$ iostat -xz 1
Device   r/s   w/s   rkB/s   wkB/s  r_await w_await aqu-sz  %util
nvme0n1  120   880   480.0  35200.0    0.30    8.40   7.12   98.5
```

- `%util` — utilization. 98.5% means the device is almost always busy. (Caveat: on SSD/NVMe with internal parallelism, `%util` can read 100% while the device still has headroom — corroborate with await.)
- `aqu-sz` — average queue size. **This is saturation.** A queue of 7 outstanding requests means I/O is backing up.
- `await` — average time (ms) per request including queue time. Rising `w_await` of 8 ms here is the smoking gun for a write-bound workload.

## Errors — Don't Skip the E

Errors are the most-ignored leg of USE because they are usually zero — until they aren't, and a single flaky NIC or a disk throwing ECC corrections explains an entire incident.

```
$ ip -s link show eth0
2: eth0: ...
    RX:  bytes  packets  errors  dropped  overrun
    ...                       0       412        0   <-- 412 dropped RX packets
$ nstat -az | grep -iE 'retrans|drop'
TcpRetransSegs                  9821   <-- TCP retransmits = network saturation/loss
```

## sar — Historical USE

`sar` (from the `sysstat` package) records all of these over time, so you can answer "what did the box look like at 3 AM when the alert fired?" without a live repro:

```
$ sar -u 1 3        # CPU utilization
$ sar -q 1 3        # run-queue (CPU saturation) + load average
$ sar -r 1 3        # memory utilization
$ sar -d -p 1 3     # per-disk utilization/await
$ sar -n DEV 1 3    # network throughput
$ sar -f /var/log/sa/sa15   # replay a past day's archive
```

## Common Mistakes

- **Reading averages only.** A disk at 40% average `%util` can be 100% saturated for 400 ms every second. Sample at 1 s and watch the variance.
- **Trusting `%util` blindly on NVMe.** Devices with deep parallelism report 100% busy while accepting more I/O. Confirm with `aqu-sz` and `await`.
- **Ignoring `st` (steal) and `wa` (iowait).** High `wa` is not a CPU problem — it redirects you to disk. High `st` is not your problem at all — it's the hypervisor.
- **Skipping Errors.** Teams chase utilization for hours when a single `ip -s link` would have shown a NIC dropping packets.
- **Using `free`'s "free" column** as available memory — a healthy box has near-zero free because the kernel uses RAM for page cache (see C03/T05).

## Best Practices

- Memorize the resource checklist table and walk it top-to-bottom on every "slow host" ticket. Completeness beats intuition.
- Always pair utilization with saturation. One without the other is half a diagnosis.
- Keep `sysstat` (`sar`) enabled on every server so you have historical USE data after an incident.
- Sample at 1-second intervals during triage to expose burst saturation that 1-minute metrics hide.
- When USE shows **no** resource bottleneck, stop tuning hardware — the problem is in software/locking/dependencies, and you should switch to the RED method on the service.

## Quick Refs

```bash
vmstat 1                 # r=CPU saturation, si/so=swap, wa=iowait, st=steal
mpstat -P ALL 1          # per-core CPU utilization (find the hot core)
iostat -xz 1             # %util, aqu-sz, await per disk
free -m ; cat /proc/meminfo   # memory capacity utilization
sar -u 1 3 ; sar -q 1 3       # CPU util + run-queue (saturation), live
sar -r 1 3 ; sar -d -p 1 3    # memory + per-disk util/await
sar -n DEV 1 3                # network throughput
ip -s link show eth0          # NIC errors/drops (the E in USE)
nstat -az | grep -i retrans   # TCP retransmits = network saturation
dmesg -T | grep -i 'out of memory'   # OOM errors
smartctl -a /dev/nvme0n1      # disk hardware errors
```

## Interview Prep

**Junior**: "What does the USE method stand for?" — Utilization, Saturation, and Errors, checked for every system resource (CPU, memory, disk, network).

**Mid**: "On a slow box, how do you tell a CPU problem from a disk problem with one command?" — Run `vmstat 1`: high `us`+`sy` with low `id` is CPU-bound, while high `wa` (iowait) means the CPU is idle waiting on disk, so I pivot to `iostat -xz 1`.

**Senior**: "A disk shows 100% %util but the app isn't slow — what's going on?" — On NVMe/SSD with internal parallelism `%util` saturates while the device still accepts I/O, so I corroborate with `aqu-sz` and `await`; if the queue and latency are low, the device has headroom and 100% util is misleading.

**Staff**: "Design a USE-method dashboard and alerting strategy for a fleet." — Per host I'd export utilization + saturation + errors for each resource (run-queue/vCPU ratio, swap rate, disk aqu-sz/await, NIC drops/retransmits), alert on the *saturation* and *error* signals rather than raw utilization to avoid false pages, and keep `sar` archives for post-incident forensics; USE covers resources, and I'd layer RED on the services on top.

## Next Topic

→ [T02 — The RED Method](T02-RED-Method.md)
