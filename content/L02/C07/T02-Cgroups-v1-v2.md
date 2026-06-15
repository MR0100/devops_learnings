# L02/C07/T02 — cgroups v1 vs v2

## Learning Objectives

- Explain what cgroups account for and limit, separate from namespaces
- Contrast the v1 multi-hierarchy model with the v2 unified hierarchy
- Navigate `/sys/fs/cgroup`, read `cgroup.controllers`, and delegate subtrees
- Understand how systemd and container runtimes drive the cgroup tree

## The Big Picture

Namespaces decide what a process can *see*; cgroups (control groups) decide how much it can *use*. A cgroup is a set of processes plus a collection of *controllers* (cpu, memory, io, pids…) that meter and cap resources for that set. Cgroups form a tree; limits are hierarchical — a child can never exceed what its ancestors allow.

```
v1: one tree PER controller (mounted separately)
  /sys/fs/cgroup/cpu/      <- cpu hierarchy
  /sys/fs/cgroup/memory/   <- memory hierarchy
  /sys/fs/cgroup/pids/     <- pids hierarchy
  (a process can sit at different paths in each)

v2: ONE unified tree, controllers enabled per node
  /sys/fs/cgroup/
    ├── cgroup.controllers      "cpu io memory pids"
    ├── cgroup.subtree_control  enable controllers for children
    └── mygroup/
          ├── cpu.max
          ├── memory.max
          └── cgroup.procs
```

Check which version you are on:

```bash
stat -fc %T /sys/fs/cgroup     # "cgroup2fs" => v2, "tmpfs" => v1 (or hybrid)
mount | grep cgroup
```

Modern distros (Fedora, Ubuntu 22.04+, RHEL 9, Debian 11+) default to pure v2.

## cgroup v1 — Multiple Hierarchies

In v1, each controller is mounted as its own hierarchy. A process therefore has an independent position in the cpu tree, the memory tree, the pids tree, and so on. `/proc/<pid>/cgroup` lists one line per hierarchy:

```
12:pids:/docker/abc...
11:memory:/docker/abc...
9:cpu,cpuacct:/docker/abc...
```

Strengths: a controller can be co-mounted (e.g. `cpu,cpuacct`) and hierarchies are flexible. Weaknesses: the same process can be at inconsistent paths across controllers, making it hard to reason about combined limits; there is no clean way to delegate a subtree; and the memory controller cannot coordinate with the io controller for writeback accounting.

```bash
# v1: set a 100MB memory limit
mkdir /sys/fs/cgroup/memory/demo
echo 104857600 > /sys/fs/cgroup/memory/demo/memory.limit_in_bytes
echo $$ > /sys/fs/cgroup/memory/demo/tasks
```

## cgroup v2 — Unified Hierarchy

v2 collapses everything into a single tree mounted once at `/sys/fs/cgroup`. Every process has exactly one cgroup path (`/proc/<pid>/cgroup` shows a single `0::/...` line). Controllers are turned on per node through two key files:

- `cgroup.controllers` — controllers *available* in this cgroup (granted by the parent).
- `cgroup.subtree_control` — controllers *enabled for children*; write `+cpu +memory` to delegate them down.

```bash
cat /sys/fs/cgroup/cgroup.controllers       # cpuset cpu io memory hugetlb pids
echo "+cpu +memory +pids" > /sys/fs/cgroup/cgroup.subtree_control

mkdir /sys/fs/cgroup/demo
echo 104857600 > /sys/fs/cgroup/demo/memory.max     # 100 MiB
echo "200000 100000" > /sys/fs/cgroup/demo/cpu.max  # 2 CPUs
echo $$ > /sys/fs/cgroup/demo/cgroup.procs
```

### The "no internal processes" rule

In v2, a cgroup that has child cgroups with controllers enabled may **not** also contain processes directly (except the root). Processes live only in leaf cgroups. This makes resource distribution unambiguous — every node is either a controller distributor or a process container, not both.

### Key v2 interface files

| File | Meaning |
|---|---|
| `cgroup.procs` | PIDs in this cgroup (write to move a process) |
| `cgroup.controllers` | controllers available here |
| `cgroup.subtree_control` | controllers enabled for children |
| `cgroup.type` | `domain`, `threaded`, etc. |
| `cgroup.events` | `populated`, `frozen` state |
| `memory.current` / `memory.max` | live usage / hard cap |
| `cpu.stat` | usage_usec, throttled time |

### Pressure Stall Information (PSI)

v2 adds `cpu.pressure`, `memory.pressure`, and `io.pressure` files reporting the fraction of time tasks stalled waiting on that resource — an early-warning signal that v1 lacked. Orchestrators use PSI to detect contention before throughput collapses.

## Delegation

A privileged manager can hand a subtree to an unprivileged user (or a container) by changing ownership of the directory and its `cgroup.procs` / `cgroup.subtree_control` files. The delegatee can then manage limits within its slice but cannot escape the ceiling set by the parent. systemd uses delegation to give each user session and each service its own cgroup.

## How systemd and Runtimes Drive It

On systemd hosts, the cgroup tree is partitioned into *slices* and *scopes*:

```
/sys/fs/cgroup/
  system.slice/        # system services
    docker.service/
    docker-<id>.scope/ # one scope per container (cgroupfs/systemd driver)
  user.slice/          # interactive user sessions
```

- v1 Docker default: `/sys/fs/cgroup/<controller>/docker/<container-id>/`.
- v2 + systemd driver: `/sys/fs/cgroup/system.slice/docker-<id>.scope/`.

`runc` writes the limits from the OCI `config.json` (`linux.resources`) into these files before exec. Kubernetes maps Pod/QoS classes onto a cgroup tree (`kubepods.slice/...`) so the kubelet can enforce requests and limits.

## Common Mistakes

- Trying to put a process directly in a v2 cgroup that already has controller-enabled children — the write fails ("no internal processes" rule).
- Forgetting to enable a controller in the parent's `cgroup.subtree_control`, so the child never gets a `cpu.max` / `memory.max` file.
- Mixing v1 byte-value files (`memory.limit_in_bytes`) with v2 files (`memory.max`) — the interface differs between versions.
- Assuming hybrid mode behaves like pure v2; in hybrid, some controllers stay on v1 and PSI/delegation may be unavailable.

## Best Practices

- Standardize on pure cgroup v2; it is the model Kubernetes and modern runtimes target.
- Let systemd own the cgroup tree and use `systemctl set-property` rather than poking `/sys/fs/cgroup` by hand on managed services.
- Watch `*.pressure` (PSI) for early contention signals instead of waiting for throttling or OOM.
- Use delegation to give workloads bounded autonomy instead of granting host-wide cgroup access.

## Quick Refs

```bash
stat -fc %T /sys/fs/cgroup              # cgroup2fs => v2
cat /proc/<pid>/cgroup                  # 0::/path on v2
cat /sys/fs/cgroup/cgroup.controllers   # available controllers
echo "+cpu +memory +pids" > /sys/fs/cgroup/cgroup.subtree_control
mkdir /sys/fs/cgroup/demo               # create a child cgroup
echo $$  > /sys/fs/cgroup/demo/cgroup.procs   # move shell into it
cat /sys/fs/cgroup/demo/memory.current  # live usage
cat /sys/fs/cgroup/demo/memory.pressure # PSI stall info
systemd-cgls                            # tree view of the hierarchy
systemd-cgtop                           # live per-cgroup resource use
```

## Interview Prep

**Junior**: "What is a cgroup?"
- A kernel mechanism that groups processes and limits/accounts their CPU, memory, I/O, and process count as a unit.

**Mid**: "What's the headline difference between cgroup v1 and v2?"
- v1 has a separate hierarchy per controller; v2 unifies all controllers into one tree with consistent per-process paths and per-node controller enabling.

**Senior**: "What is the v2 'no internal processes' rule and why does it exist?"
- A non-root cgroup with controller-enabled children can't hold processes directly; it removes ambiguity about whether a node distributes resources to children or competes with them.

**Staff**: "How would you detect resource contention before throttling hurts latency?"
- Monitor cgroup v2 PSI files (`cpu/memory/io.pressure`); rising stall percentages flag saturation early, letting you scale or rebalance before throttling and OOM cause user-visible impact.

## Next Topic

→ [T03 — Resource Limits](T03-Resource-Limits.md)
