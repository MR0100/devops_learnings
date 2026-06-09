# L12/C01 — Container First Principles

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-What-Is-Container.md) | What a Container Actually Is | 1 hr |
| [T02](T02-Namespaces.md) | Namespaces (Recap from L02) | 0.5 hr |
| [T03](T03-Cgroups.md) | Cgroups (Recap from L02) | 0.5 hr |
| [T04](T04-Union-FS.md) | Union Filesystems (overlayfs) | 1 hr |
| [T05](T05-Capabilities-Seccomp.md) | Capabilities & Seccomp | 1 hr |

## A Container Is Not a Thing

A container is not a single object. It's a **process (or processes)** running in isolation provided by:

1. **Namespaces** — what the process can SEE (pid, net, mnt, uts, ipc, user, cgroup)
2. **Cgroups** — what the process can USE (CPU, memory, IO, processes)
3. **Union FS** — layered, copy-on-write filesystem
4. **Capabilities** — fine-grained privilege control
5. **Seccomp** — syscall filtering
6. **MAC** (SELinux/AppArmor) — additional mandatory access control

There's no "container" in the kernel. It's a userspace abstraction over these kernel primitives.

## Namespaces (Quick Recap)

| Namespace | Isolates |
|---|---|
| pid | Process IDs (container sees PID 1 as itself) |
| net | Network interfaces, routes, iptables |
| mnt | Filesystem mounts |
| uts | Hostname, domainname |
| ipc | System V IPC, POSIX message queues |
| user | UID/GID mappings (rootless containers) |
| cgroup | Cgroup hierarchy view |
| time | Clock offsets (newer) |

## Cgroups (Quick Recap)

Hierarchical resource limits + accounting:
- `cpu` — CPU shares, quota
- `memory` — memory limit, swap
- `io` — block I/O weight, throttle
- `pids` — max processes
- `cpuset` — CPU pinning
- `hugetlb`, `rdma`, `net_cls`, `net_prio`

Cgroups v1 vs v2: v2 is unified hierarchy, single tree, default in modern distros.

## Union Filesystems (OverlayFS)

OverlayFS stacks read-only "lower" layers with a read-write "upper" layer:

```
upper (RW)            ← container's writes
+ merged              ← what container sees (unified)
─ lower N             ← Dockerfile layer N
─ lower N-1           ← Dockerfile layer N-1
...
─ lower 0             ← base image
```

### Why It Matters
- Image layers shared between containers (one copy on disk for the lower)
- Container writes go to upper layer only
- Removing a file in upper just marks it deleted (lower unchanged)
- Image immutable; container is the diff

### Performance
- OverlayFS is fast for reads (lower layer paths)
- Writes copy-up to upper (slower than native FS for first write)
- For heavy writes inside container, use a volume (bind mount)

## Capabilities

Linux split root's "all powers" into ~40 capabilities. Examples:
- `CAP_NET_BIND_SERVICE` — bind to ports < 1024
- `CAP_NET_ADMIN` — configure network
- `CAP_SYS_ADMIN` — broad superuser-ish (avoid)
- `CAP_SYS_PTRACE` — trace processes
- `CAP_DAC_OVERRIDE` — bypass file permission checks
- `CAP_CHOWN` — change file owner

Docker by default keeps a small allowlist; drops most. Run with `--cap-drop ALL --cap-add NET_BIND_SERVICE` for maximum hardening.

## Seccomp (Secure Computing Mode)

Filters syscalls. Container can be restricted to a subset.

- Docker default: blocks ~40 dangerous syscalls
- Custom profiles: JSON allowlist/denylist
- K8s: `securityContext.seccompProfile.type: RuntimeDefault`

Without seccomp, a CVE in your code can call dangerous syscalls. With it, even an exploit is constrained.

## Container vs VM

```
VM:                              Container:
┌────────────────┐               ┌────────────────┐
│ App            │               │ App            │
├────────────────┤               ├────────────────┤
│ Libraries      │               │ Libraries      │
├────────────────┤               ├────────────────┤
│ Guest OS       │               │
├────────────────┤               │ (shares host kernel)
│ Hypervisor     │               │
├────────────────┤               │
│ Host OS        │               │ Host OS        │
└────────────────┘               └────────────────┘
```

- VM: separate kernel per VM; hardware-level isolation; slower boot, more overhead
- Container: shared kernel; OS-level isolation; faster boot, less overhead, less isolated

## Build a Container by Hand (Conceptual)

```bash
# 1. Create a rootfs (debootstrap, alpine extract, etc.)
debootstrap bookworm /opt/rootfs

# 2. Apply cgroup limits
mkdir /sys/fs/cgroup/mycontainer
echo "100M" > /sys/fs/cgroup/mycontainer/memory.max

# 3. Enter new namespaces + chroot
sudo unshare --fork --pid --net --mount --uts --ipc --user --map-root-user \
  chroot /opt/rootfs /bin/bash

# 4. Inside: mount /proc, /sys, set up loopback...
```

This is roughly what `runc` does behind the scenes. Real container runtimes also handle: OCI image unpack, capabilities, seccomp, cgroup attachment, network setup via CNI, signal forwarding.

## OCI Standards

The Open Container Initiative defines:
- **Image Spec** — how an image is structured (manifest, config, layers as tar)
- **Runtime Spec** — how a container is configured (config.json) and started
- **Distribution Spec** — how a registry serves images

Docker images and runtime are OCI-compliant. So are containerd, CRI-O, runc, podman, etc.

## Interview Themes

- "What is a container at the kernel level?"
- "Compare container and VM"
- "Why is overlay filesystem fast?"
- "Why drop capabilities?"
- "What does seccomp protect against?"
- "Build a container by hand — what kernel features?"
