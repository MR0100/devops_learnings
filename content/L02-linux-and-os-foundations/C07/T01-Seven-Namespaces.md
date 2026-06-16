# L02/C07/T01 — The Linux Namespaces

## Learning Objectives

- Explain what each namespace isolates and how a process joins or leaves one
- Use `unshare`, `nsenter`, and `lsns` to inspect and manipulate namespaces
- Understand how `/proc/<pid>/ns/` symlinks identify namespace membership
- Connect namespaces to the `clone()` / `unshare()` / `setns()` syscalls that runtimes use

## The Big Picture

A namespace virtualizes a single class of global kernel resource so that processes inside it see their own isolated instance. There is no single "container namespace" — a container is a process that happens to live in a *fresh set* of all the namespaces below at once. Each process belongs to exactly one namespace of each type.

```
              Host (init namespaces)
   ┌──────────────────────────────────────────┐
   │  PID ns: 1=systemd, 1000s of host PIDs    │
   │  NET ns: eth0, host routes, host iptables │
   │                                           │
   │   ┌───────────────────────────────────┐   │
   │   │ Container = new {pid,net,mnt,uts,  │   │
   │   │             ipc,user,cgroup} ns    │   │
   │   │  PID ns: 1=app  (host sees 24917)  │   │
   │   │  NET ns: eth0@if (veth), own routes│   │
   │   │  MNT ns: private / from image      │   │
   │   │  UTS ns: hostname=web-7f9          │   │
   │   └───────────────────────────────────┘   │
   └──────────────────────────────────────────┘
```

The kernel exposes namespace membership as magic symlinks under `/proc/<pid>/ns/`. Two processes share a namespace if and only if those symlinks point at the same inode.

```bash
ls -l /proc/self/ns/
# lrwxrwxrwx ... net -> 'net:[4026531840]'
# lrwxrwxrwx ... pid -> 'pid:[4026531836]'
# lrwxrwxrwx ... mnt -> 'mnt:[4026531841]'
```

The number in brackets is the namespace inode. The `4026531xxx` range is the host (initial) namespaces.

## The Namespaces

| Namespace | `clone()` flag | Isolates | Since |
|---|---|---|---|
| Mount | `CLONE_NEWNS` | Filesystem mount points (the mount tree) | 2.4.19 |
| UTS | `CLONE_NEWUTS` | Hostname and NIS domain name | 2.6.19 |
| IPC | `CLONE_NEWIPC` | System V IPC, POSIX message queues | 2.6.19 |
| PID | `CLONE_NEWPID` | Process ID number space | 2.6.24 |
| Network | `CLONE_NEWNET` | NICs, routes, firewall, ports, `/proc/net` | 2.6.29 |
| User | `CLONE_NEWUSER` | UID/GID mappings, capabilities | 3.8 |
| Cgroup | `CLONE_NEWCGROUP` | The cgroup root a process sees | 4.6 |
| Time | `CLONE_NEWTIME` | `CLOCK_MONOTONIC` / `CLOCK_BOOTTIME` offsets | 5.6 |

(The mount namespace flag is the oldest and oddly named `CLONE_NEWNS` because it was the first; "NS" meant "namespace" generically before others existed.)

### Mount (`CLONE_NEWNS`)

Gives the process a private copy of the mount table. New mounts inside it are invisible to the host. Mount *propagation* (`private`, `shared`, `slave`) governs whether mount events cross the boundary — runtimes typically make the container's root `rprivate` so a `mount` inside cannot leak to the host. This is what lets a container have a totally different `/` from the image's rootfs.

### UTS (`CLONE_NEWUTS`)

Isolates the two strings returned by `uname()`: nodename (hostname) and domainname. This is why `hostname` inside a container differs from the host and changing it does not affect the host.

### IPC (`CLONE_NEWIPC`)

Isolates System V semaphores, shared memory segments, message queues, and POSIX message queues. Processes in different IPC namespaces cannot see each other's `ipcs` objects or attach to the same SysV shm.

### PID (`CLONE_NEWPID`)

The first process in a new PID namespace becomes PID 1 inside it and reaps orphans like `init`. The host still sees that process under its real (host) PID. PID namespaces nest: a PID has one number per namespace level. If PID 1 dies, the whole namespace is torn down and its children are killed.

### Network (`CLONE_NEWNET`)

A fresh, empty network stack: only a `lo` interface (down), no routes, no iptables rules, its own port space. Connectivity is added by moving one end of a `veth` pair into the namespace. Two containers can both bind `:80` because each has an independent port space.

### User (`CLONE_NEWUSER`)

Maps UIDs/GIDs between the namespace and its parent via `/proc/<pid>/uid_map` and `gid_map`. Root (UID 0) inside can map to an unprivileged UID outside — this is the basis of *rootless* containers. A process gains a full capability set *within* the user namespace it created, but those capabilities are scoped to resources owned by that namespace. It is the only namespace an unprivileged user can create without `CAP_SYS_ADMIN`.

### Cgroup (`CLONE_NEWCGROUP`)

Virtualizes the cgroup root so `/proc/<pid>/cgroup` shows paths relative to the namespace root rather than the host's full hierarchy. This hides the host's cgroup layout from the container.

### Time (`CLONE_NEWTIME`)

Lets a namespace present a different `CLOCK_MONOTONIC` / `CLOCK_BOOTTIME` offset, useful for checkpoint/restore (CRIU) so restored processes see continuous uptime.

## Syscalls Behind It

Three syscalls do all the work:

- `clone(flags, ...)` — create a child process already placed in new namespaces selected by the `CLONE_NEW*` flags. Runtimes use this to spawn the container's first process.
- `unshare(flags)` — move the *calling* process into new namespaces without forking (except PID, which only takes effect for children).
- `setns(fd, nstype)` — join an existing namespace given an open fd to its `/proc/<pid>/ns/<type>` file. This is exactly what `nsenter` and `docker exec` do.

## Hands-On

```bash
# Create a process in new UTS + PID + mount namespaces
sudo unshare --uts --pid --mount --fork --mount-proc bash
hostname container-demo     # only changes inside this ns
echo $$                     # this shell is PID 1 here
ps aux                      # sees only namespace-local processes

# From another terminal, find its host PID and enter it
lsns -t pid                 # list pid namespaces and their leader PID
sudo nsenter -t <pid> -a    # enter ALL of that process's namespaces
sudo nsenter -t <pid> -n ip addr   # run just inside its net namespace

# Inspect namespace inodes
readlink /proc/self/ns/net
sudo readlink /proc/<pid>/ns/net   # same inode => shared namespace
```

`lsns` is the most useful audit tool: it groups all processes by namespace and shows the leader PID, type, and number of members.

## How Docker / runc Use This

`docker run` ultimately calls `runc`, which reads the OCI `config.json` and:

1. Calls `clone()` with the requested `CLONE_NEW*` flags to create the init process.
2. Sets up the user namespace UID/GID maps (if rootless).
3. Moves a `veth` end into the new net namespace.
4. Pivots root into the unpacked image (mount namespace + `pivot_root`).
5. Applies cgroup limits, seccomp, capabilities, then `execve()`s the entrypoint.

`docker exec` is `setns()` into each of the target container's namespaces, then `execve()`.

## Common Mistakes

- Expecting `unshare --pid` alone to give the shell PID 1 — without `--fork`, the *current* shell stays in the old PID namespace; only forked children land in the new one.
- Forgetting `--mount-proc`, so `ps` and `/proc` still show host processes inside a new PID namespace.
- Assuming a new net namespace has connectivity — it starts with only a down `lo`; you must add a veth and routes.
- Treating "the container namespace" as one thing — it is always a *set* of independent namespaces.

## Best Practices

- Use `lsns` and `nsenter` for debugging instead of installing tools inside minimal containers.
- Prefer user namespaces (rootless) so a container "root" maps to an unprivileged host UID.
- Make the container root mount `rprivate` to prevent mount propagation back to the host.
- Treat PID 1 inside a container as `init`: ensure it reaps zombies (use a proper init like `tini` for multi-process containers).

## Quick Refs

```bash
ls -l /proc/<pid>/ns/                 # namespace membership (symlinks)
readlink /proc/self/ns/net            # net namespace inode
lsns                                  # list all namespaces + members
lsns -t pid                           # only PID namespaces
unshare --pid --net --mount --uts \
  --ipc --user --fork --mount-proc bash   # new full set
nsenter -t <pid> -a                   # enter all namespaces of <pid>
nsenter -t <pid> -n ip addr           # run in target's net namespace
ip netns add demo; ip netns exec demo bash   # named net namespaces
```

## Interview Prep

**Junior**: "What is a Linux namespace?"
- A kernel feature that isolates one class of global resource (PIDs, network, mounts, etc.) so processes inside see their own private instance.

**Mid**: "How do you enter a running container's network namespace from the host?"
- Find its init PID, then `nsenter -t <pid> -n <cmd>`, which `setns()`s into the net namespace fd at `/proc/<pid>/ns/net`.

**Senior**: "Why can two containers both listen on port 80?"
- Each lives in its own network namespace with an independent port/socket space, so the bind to `:80` happens in separate stacks that never collide.

**Staff**: "How do rootless containers grant root inside while staying unprivileged outside?"
- A user namespace maps in-namespace UID 0 to an unprivileged host UID via `uid_map`/`gid_map`; the process holds capabilities only over resources owned by that user namespace, so it cannot affect the host.

## Next Topic

→ [T02 — cgroups v1 vs v2](T02-Cgroups-v1-v2.md)
