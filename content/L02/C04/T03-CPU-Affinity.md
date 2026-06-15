# L02/C04/T03 — CPU Affinity (taskset, cpusets)

## Learning Objectives

- Pin processes and IRQs to specific CPUs with `taskset`, cgroup `cpuset`, and `numactl`
- Understand why affinity helps (cache/NUMA locality) and where it hurts (load imbalance)
- Connect Linux affinity primitives to the Kubernetes CPU Manager static policy

## Why Pin a Task?

By default CFS moves tasks between CPUs to balance load. That migration is cheap for the scheduler but expensive for the *task*: a moved task loses its warm L1/L2 cache and, on NUMA boxes, may end up running far from its memory.

```
CPU0 (warm cache for task X)        CPU3 (cold cache)
   ████ task X data in L1/L2   ──►   ░░░░ must refill from L3/RAM
```

Affinity (pinning) keeps a task on a fixed set of CPUs so its cache and memory stay local — the standard move for databases, low-latency engines, and DPDK/packet workloads.

## taskset — Per-Process Affinity

`taskset` reads/sets the CPU **affinity mask** (which CPUs a task is *allowed* to run on).

```bash
taskset -p 1234                 # show current mask (hex)
taskset -cp 1234                # show as CPU list (e.g. 0-3)
taskset -cp 2,3 1234            # restrict running PID to CPUs 2 and 3
taskset -c 0-3 ./engine         # launch a new process pinned to CPUs 0-3
```

The mask is a bitmap: CPU0 = bit 0. `0x1` = CPU0 only, `0x3` = CPUs 0+1, `0xff` = CPUs 0–7.

```
mask 0x0000000C  =  ...0000 1100  =  CPUs 2 and 3
                          ↑↑
                       cpu3 cpu2
```

Affinity is inherited by children, so pinning a launcher pins the whole subtree.

## /proc View and the Programmatic API

```bash
grep Cpus_allowed_list /proc/1234/status     # human-readable CPU list
grep -i cpus_allowed   /proc/1234/status     # raw mask
```

Programmatically it's `sched_setaffinity(2)` / `sched_getaffinity(2)`; threads can each have their own mask via `pthread_setaffinity_np`.

## cpusets — cgroup-Based Affinity

`taskset` is per-task and advisory; **cpusets** confine an entire cgroup (and everything spawned inside it) to a set of CPUs and memory nodes — the mechanism containers and Kubernetes actually use.

### cgroup v2

```bash
# Confine a cgroup to CPUs 4-7 and NUMA node 1
echo "4-7" > /sys/fs/cgroup/myapp/cpuset.cpus
echo "1"   > /sys/fs/cgroup/myapp/cpuset.mems
echo 5678  > /sys/fs/cgroup/myapp/cgroup.procs

cat /sys/fs/cgroup/myapp/cpuset.cpus.effective   # what it actually got
```

### cgroup v1 (legacy)

```bash
mkdir /sys/fs/cgroup/cpuset/myapp
echo "4-7" > /sys/fs/cgroup/cpuset/myapp/cpuset.cpus
echo "1"   > /sys/fs/cgroup/cpuset/myapp/cpuset.mems
echo 5678  > /sys/fs/cgroup/cpuset/myapp/tasks
```

cpusets compose with CFS weights and bandwidth limits — you can give a cgroup *exclusive* CPUs (`cpuset.cpus.partition = root`) so no other cgroup schedules there.

## NUMA Awareness with numactl

On multi-socket boxes, memory has a "home" node. Running on a CPU far from your memory adds latency on every miss.

```bash
numactl --hardware                       # show nodes, CPUs, distances
numactl --cpunodebind=1 --membind=1 ./db # CPUs and memory both on node 1
numastat -p 1234                         # per-node memory hits/misses for a PID
```

```
Node 0                      Node 1
[CPU 0-7] ── local RAM      [CPU 8-15] ── local RAM
     \                          /
      ── interconnect (slower) ─
```

`--membind` is strict (allocation fails rather than spilling cross-node); `--preferred` is a soft hint.

## Isolating CPUs from the Scheduler

For the lowest jitter, remove CPUs from the general scheduler entirely so *only* explicitly pinned tasks run there:

```bash
# Kernel cmdline (GRUB):
isolcpus=4-7 nohz_full=4-7 rcu_nocbs=4-7
```

- `isolcpus` — CFS won't auto-balance onto these CPUs.
- `nohz_full` — stops the periodic scheduler tick on them (no 1000 Hz interrupt).
- `rcu_nocbs` — offloads RCU callbacks elsewhere.

Then `taskset -c 4-7` your latency process. Pair with IRQ pinning so device interrupts don't land on the isolated cores:

```bash
cat /proc/interrupts                              # find the IRQ number
echo 1 > /proc/irq/<N>/smp_affinity               # send IRQ N to CPU0 only
```

## Kubernetes CPU Manager

The kubelet's **static** CPU Manager policy translates "Guaranteed pod with integer CPU requests" into exclusive cpuset pinning.

| Policy | Behavior |
|---|---|
| `none` (default) | All pods share the CPU pool; CFS shares via `cpu.weight` |
| `static` | Guaranteed pods with **integer** CPU limits get **exclusive** cores via cpuset |

Requirements for a pod to get pinned: QoS class **Guaranteed** (requests == limits) and **whole-number** CPU. A `500m` request stays in the shared pool. The Topology Manager can further align CPU + device (NIC/GPU) + memory on the same NUMA node.

## Common Mistakes

- Pinning everything to a few CPUs and leaving the rest idle — you traded cache locality for a load imbalance.
- Using `taskset` inside a container and expecting host-CPU semantics — you see the host's CPU numbers but the cgroup cpuset may already restrict you.
- Forgetting `cpuset.mems` — pinning CPUs but not memory still allows cross-NUMA allocations.
- Expecting K8s to pin a `cpu: 1500m` pod — fractional requests never get exclusive cores under the static policy.
- Isolating CPUs with `isolcpus` but leaving device IRQs landing on them, reintroducing jitter.

## Best Practices

- Pin for cache/NUMA locality only where you've measured a benefit (DBs, packet processing, latency engines).
- Always set both `cpuset.cpus` and `cpuset.mems` together on NUMA hardware.
- Combine `isolcpus` + `nohz_full` + IRQ affinity for true low-jitter cores, and reserve a couple of CPUs for the OS/kernel threads.
- In Kubernetes, use Guaranteed QoS with integer CPUs and the static CPU Manager policy for latency-critical pods.
- Verify with `Cpus_allowed_list` in `/proc/<pid>/status` and `cpuset.cpus.effective`, not just the command you issued.

## Quick Refs

```bash
# Per-process affinity
taskset -cp 1234                 # show CPU list
taskset -cp 2,3 1234             # restrict running PID
taskset -c 0-3 ./engine          # launch pinned
grep Cpus_allowed_list /proc/1234/status

# cgroup v2 cpuset
echo "4-7" > /sys/fs/cgroup/app/cpuset.cpus
echo "1"   > /sys/fs/cgroup/app/cpuset.mems
cat /sys/fs/cgroup/app/cpuset.cpus.effective

# NUMA
numactl --hardware
numactl --cpunodebind=1 --membind=1 ./db
numastat -p 1234

# Isolation + IRQ pinning
# cmdline: isolcpus=4-7 nohz_full=4-7 rcu_nocbs=4-7
echo 1 > /proc/irq/<N>/smp_affinity
```

## Interview Prep

**Junior**: "What does `taskset` do?"
- Sets a process's CPU affinity mask — which CPUs it's allowed to run on — to keep it on specific cores.

**Mid**: "Why would pinning a process to one CPU help performance?"
- It preserves the warm L1/L2 cache and, on NUMA, keeps the task near its local memory, avoiding migration and cross-node access costs.

**Senior**: "How do you build a low-jitter core for a latency engine?"
- `isolcpus`+`nohz_full`+`rcu_nocbs` to remove the CPU from the scheduler and tick, pin the process with `taskset`, set `cpuset.mems` to the local NUMA node, and steer device IRQs off that core via `/proc/irq/*/smp_affinity`.

**Staff**: "How does the Kubernetes CPU Manager static policy interact with CFS and NUMA?"
- Guaranteed pods with integer CPU limits get exclusive cores via cpuset, removed from the shared CFS pool so they don't compete on `cpu.weight`; the Topology Manager aligns those cores with memory and devices on one NUMA node, while shared/burstable pods keep using CFS proportional sharing on the remaining CPUs.

## Next Topic

→ [T04 — Context Switching Costs](T04-Context-Switching.md)
