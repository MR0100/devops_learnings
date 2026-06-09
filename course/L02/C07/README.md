# L02/C07 — Cgroups & Namespaces (Container Foundations)

## Chapter Overview

This is **the most important chapter in L02** for understanding containers. Docker, Kubernetes, and every container runtime are simply orchestration around cgroups + namespaces + chroot. After this chapter, you'll build a container by hand.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-Seven-Namespaces.md) | The 7 Namespaces (pid, net, ipc, mnt, uts, user, cgroup) | 1.5 hr |
| [T02](T02-Cgroups-v1-v2.md) | Cgroups v1 vs v2 | 1.5 hr |
| [T03](T03-Resource-Limits.md) | Resource Limits (cpu, memory, blkio, pids) | 1 hr |
| [T04](T04-Build-Container-Scratch.md) | Building a Container from Scratch with unshare | 2 hr |

## The 7 Namespaces

A namespace isolates a class of system resource. Each process belongs to one of each.

| Namespace | What it isolates | View |
|---|---|---|
| pid | Process IDs | `/proc` shows only same-namespace processes |
| net | Network interfaces, routes, iptables, ports | Independent network stack |
| mnt | Filesystem mounts | Private mount tree |
| uts | Hostname, domainname | Independent identity |
| ipc | System V IPC, POSIX msgq | Cannot send IPC across |
| user | UID/GID mappings | Rootless containers; CAP_USER_NS |
| cgroup | Cgroup view | Hides host's cgroup hierarchy |
| time | (added 2020) CLOCK_BOOTTIME / MONOTONIC | Independent clock offsets |

```bash
# See what namespaces a process is in
ls -l /proc/<pid>/ns/

# Enter a namespace
nsenter -t <pid> -n      # network ns
nsenter -t <pid> -m      # mount ns
nsenter -a -t <pid>      # all

# Create new ones
unshare --pid --net --mount --uts --ipc --user --fork bash
```

## Cgroups Deep

Cgroups (control groups) limit and account resources per process group. Two versions; v2 is now default in modern distros.

### Cgroup v1 (legacy)
- Multiple hierarchies (one per controller)
- `/sys/fs/cgroup/cpu`, `/sys/fs/cgroup/memory`, etc.
- More complex; harder to reason about

### Cgroup v2 (unified)
- Single hierarchy
- `/sys/fs/cgroup` (the whole tree)
- One controller config per cgroup
- Pressure Stall Information (PSI) for early-warning

### Controllers
- `cpu` — CPU shares/quota (`cpu.weight`, `cpu.max`)
- `memory` — memory limit (`memory.max`, `memory.high`)
- `io` — block I/O weight (`io.weight`, `io.max`)
- `pids` — process count limit (`pids.max`)
- `cpuset` — CPU pinning (`cpuset.cpus`, `cpuset.mems`)
- `hugetlb` — hugepage limits
- `rdma` — RDMA limits

### Creating a Cgroup (v2)
```bash
mkdir /sys/fs/cgroup/mygroup
echo "100M" > /sys/fs/cgroup/mygroup/memory.max
echo "200000 100000" > /sys/fs/cgroup/mygroup/cpu.max   # 2 CPUs (200000us per 100000us period)
echo $$ > /sys/fs/cgroup/mygroup/cgroup.procs           # add current shell
```

### systemd Manages Cgroups
On systemd systems, every service is a cgroup. Easier to use:
- `systemctl set-property myapp.service MemoryMax=2G`
- `systemctl set-property myapp.service CPUQuota=200%`

### Cgroups + Containers
Containers ARE cgroups + namespaces. Docker creates a cgroup for each container at `/sys/fs/cgroup/docker/<id>/` (v1) or `/sys/fs/cgroup/system.slice/docker-<id>.scope/` (v2 via systemd).

## Building a Container from Scratch

The minimum:
1. Prepare a root filesystem (e.g., debootstrap)
2. `unshare` into new namespaces
3. `chroot` to root
4. Mount `/proc`, `/sys`
5. Apply cgroup limits
6. Run the program

```bash
# Tiny demo (skips cgroups for brevity)
sudo unshare --fork --pid --mount-proc --mount --uts --ipc --net \
  chroot /path/to/rootfs /bin/bash
```

Real container runtimes (runc, crun) handle this plus capabilities, seccomp, AppArmor, OCI image unpacking, layered filesystems.

## Interview Themes

- "What is a container? Explain in terms of kernel primitives."
- "Difference between cgroup v1 and v2."
- "Walk me through what happens when `docker run` is called."
- "Why does setting `--cpus=2` not always give exactly 2 CPUs of throughput?"
- "Build a container by hand — what kernel features do you need?"

## Hands-On Lab

1. Use `unshare` to create a process in a new network namespace
2. Set up a veth pair between host and namespace
3. Mount your own proc inside an unshare'd PID namespace
4. Create a cgroup with 50MB memory limit; run a script that allocates 100MB; observe OOM

This is the foundation of Docker. Doing it by hand demystifies everything.
