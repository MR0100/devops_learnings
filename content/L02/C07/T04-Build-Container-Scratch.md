# L02/C07/T04 — Build a Container from Scratch

## Learning Objectives

- Assemble namespaces + chroot/pivot_root + cgroups into a working container by hand
- Understand the exact ordering a runtime follows: rootfs → namespaces → root pivot → mounts → cgroup → exec
- Explain what runc/crun add on top of this minimal recipe (capabilities, seccomp, OCI images, overlayfs)
- Debug a hand-built container with `lsns`, `nsenter`, and the cgroup files

## The Big Picture

A container is not a kernel object — it is a process that a runtime placed inside a fresh set of namespaces, behind its own root filesystem, and under a cgroup with limits. Build those three layers manually and "container" stops being magic.

```
   docker run  ==  unshare(namespaces)
                 + pivot_root(image rootfs)
                 + mount /proc /sys
                 + write cgroup limits
                 + drop caps / apply seccomp
                 + execve(entrypoint)

   ┌─ new mnt+pid+net+uts+ipc ns ─┐
   │  / = /path/to/rootfs         │   <- chroot / pivot_root
   │  PID 1 = /bin/bash           │   <- --fork --mount-proc
   │  hostname = sandbox          │   <- new UTS ns
   │  cgroup: mem=100M cpu=1      │   <- /sys/fs/cgroup/sandbox
   └──────────────────────────────┘
```

## Step 1 — Prepare a root filesystem

The container needs its own `/`. Any minimal userland works — debootstrap, a BusyBox tarball, or an unpacked Docker image.

```bash
# Option A: Debian rootfs
sudo apt-get install -y debootstrap
sudo debootstrap --variant=minbase bookworm /tmp/rootfs \
  http://deb.debian.org/debian

# Option B: borrow an image's rootfs (no Docker daemon needed)
mkdir -p /tmp/rootfs
docker export $(docker create alpine) | tar -C /tmp/rootfs -xf -
```

After this, `/tmp/rootfs` contains `bin/`, `lib/`, `etc/`, etc. — a complete filesystem tree to become the container's `/`.

## Step 2 — Enter new namespaces and chroot

The quickest demo uses `unshare` to create the namespaces and `chroot` to swap the root:

```bash
sudo unshare \
  --pid --fork --mount-proc \   # new PID ns; remount /proc for it
  --mount \                     # private mount tree
  --uts \                       # own hostname
  --ipc \                       # own SysV IPC
  --net \                       # empty network stack (lo only)
  chroot /tmp/rootfs /bin/sh

# Inside the container now:
hostname sandbox
echo $$          # 1  -> we are PID 1
ps aux           # only our processes (thanks to --mount-proc)
ls /             # the rootfs, not the host's /
```

What each flag bought us:
- `--pid --fork` puts the new shell's children in a fresh PID namespace and makes the forked child PID 1.
- `--mount-proc` mounts a fresh `/proc` so `ps`/`top` reflect the new PID namespace.
- `--mount` isolates the mount tree so our binds don't leak to the host.
- `--uts/--ipc/--net` give independent hostname, IPC, and network stack.

## Step 3 — Mount the pseudo-filesystems

Inside the chroot, programs expect `/proc`, `/sys`, and `/dev` shims. `--mount-proc` handled `/proc`; add the rest manually if `unshare` didn't:

```bash
mount -t proc proc /proc
mount -t sysfs sys /sys
mount -t tmpfs tmpfs /dev
mount -t devpts devpts /dev/pts 2>/dev/null || true
```

### chroot vs pivot_root

`chroot` changes the apparent root but the old root is still reachable via tricks and remains mounted — real runtimes use `pivot_root` instead, which *moves* the old root out and then unmounts it, so the container truly cannot see the host filesystem:

```bash
# Sketch of what runc does (inside the mount namespace):
mount --bind /tmp/rootfs /tmp/rootfs        # make rootfs a mount point
cd /tmp/rootfs
mkdir -p oldroot
pivot_root . oldroot                        # new root = rootfs, old at /oldroot
umount -l /oldroot                          # detach the host root
```

## Step 4 — Apply cgroup limits

Create a cgroup, set caps, and move the container's PID 1 into it. Do this from the **host** (the cgroupfs lives on the host hierarchy), using the container's host PID.

```bash
# On the host, before/while the container runs:
CG=/sys/fs/cgroup/sandbox
sudo mkdir -p "$CG"
echo "+cpu +memory +pids" | sudo tee /sys/fs/cgroup/cgroup.subtree_control
echo 104857600     | sudo tee "$CG/memory.max"   # 100 MiB
echo 0             | sudo tee "$CG/memory.swap.max"
echo "100000 100000" | sudo tee "$CG/cpu.max"    # 1 CPU
echo 256           | sudo tee "$CG/pids.max"     # fork-bomb guard

# find the container's PID 1 on the host and move it in:
HOSTPID=$(pgrep -f 'unshare .* /bin/sh' | head -1)
echo "$HOSTPID" | sudo tee "$CG/cgroup.procs"
```

Now the container is bounded: allocate >100 MiB inside it and the cgroup OOM killer fires; check `cat $CG/memory.events`.

## Step 5 — Give it a network (optional)

A new net namespace has only a down `lo`. Wire it up with a veth pair from the host:

```bash
# Host side: create veth, move one end into the container's net ns
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth1 netns "$HOSTPID"     # by pid of the netns owner
sudo ip addr add 10.0.0.1/24 dev veth0
sudo ip link set veth0 up

# Inside container netns (via nsenter):
sudo nsenter -t "$HOSTPID" -n ip addr add 10.0.0.2/24 dev veth1
sudo nsenter -t "$HOSTPID" -n ip link set veth1 up
sudo nsenter -t "$HOSTPID" -n ip link set lo up
sudo nsenter -t "$HOSTPID" -n ip route add default via 10.0.0.1
# Add a host NAT rule for outbound: iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -j MASQUERADE
```

## Putting it together (script)

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOTFS=/tmp/rootfs
CG=/sys/fs/cgroup/sandbox

# 1. cgroup limits
mkdir -p "$CG"
echo "+memory +pids +cpu" > /sys/fs/cgroup/cgroup.subtree_control
echo 104857600 > "$CG/memory.max"; echo 0 > "$CG/memory.swap.max"
echo 256 > "$CG/pids.max"

# 2. namespaces + chroot, joining the cgroup via a helper
unshare --pid --fork --mount-proc --mount --uts --ipc --net -- \
  bash -c '
    echo $$ > /sys/fs/cgroup/sandbox/cgroup.procs
    hostname sandbox
    exec chroot '"$ROOTFS"' /bin/sh
  '
```

## What runc / crun add

The hand recipe is the skeleton; production runtimes layer on:

- **OCI image + overlayfs**: image layers are mounted as a read-only `lowerdir` stack with a writable `upperdir` — copy-on-write, no rootfs copy.
- **Capabilities**: drop all and add back only what the spec lists (`CAP_NET_BIND_SERVICE`, etc.) instead of running with full root.
- **seccomp-bpf**: a syscall allow/deny filter applied before `execve`.
- **LSM**: AppArmor/SELinux profiles confining file and capability access.
- **User namespace**: map container root to an unprivileged host UID (rootless).
- **cgroup setup via systemd or cgroupfs driver**, reading limits from `config.json`'s `linux.resources`.
- **pivot_root** (not chroot) and a careful mount-propagation setup (`rprivate`).

`docker run` → containerd → `runc create`/`runc start`, with `runc` doing exactly the clone/setns/pivot_root/cgroup/exec sequence above.

## Debugging your container

```bash
lsns                          # confirm new pid/net/mnt/uts/ipc namespaces
sudo nsenter -t $HOSTPID -a   # drop into all of its namespaces
cat /sys/fs/cgroup/sandbox/memory.current   # live memory use
cat /sys/fs/cgroup/sandbox/cpu.stat         # throttling
cat /proc/$HOSTPID/cgroup                   # 0::/sandbox
```

## Common Mistakes

- Using `chroot` and assuming full isolation — without `pivot_root`+unmount, the host root can still be reachable.
- Skipping `--mount-proc`, so `ps`/`top` inside show host processes.
- Writing the container PID into the cgroup from inside the chroot, where `/sys/fs/cgroup` may not be mounted — do it from the host or mount sysfs first.
- Expecting network without a veth — a new net namespace starts empty.
- Running PID 1 as a normal shell with no zombie reaping for multi-process workloads.

## Best Practices

- Prefer `pivot_root` over `chroot` and mount the container root `rprivate`.
- Apply cgroup limits *before* exec so a fork bomb or memory spike can't escape the window.
- Drop capabilities and add a seccomp profile — namespaces alone are not a security boundary.
- Use overlayfs (layered images) instead of copying a fresh rootfs per container.
- Use a real init (`tini`/`dumb-init`) as PID 1 for anything spawning children.

## Quick Refs

```bash
debootstrap --variant=minbase bookworm /tmp/rootfs   # or: docker export
unshare --pid --fork --mount-proc --mount --uts \
  --ipc --net chroot /tmp/rootfs /bin/sh             # minimal container
mount -t proc proc /proc                             # inside, if needed
pivot_root . oldroot && umount -l /oldroot           # real root swap
mkdir /sys/fs/cgroup/sandbox                         # cgroup
echo 104857600 > /sys/fs/cgroup/sandbox/memory.max
echo <pid> > /sys/fs/cgroup/sandbox/cgroup.procs
ip link add veth0 type veth peer name veth1          # networking
ip link set veth1 netns <pid>
lsns ; nsenter -t <pid> -a                           # debug
```

## Interview Prep

**Junior**: "What kernel features do you need to build a container?"
- Namespaces (isolation), a root filesystem swap (chroot/pivot_root), and cgroups (resource limits).

**Mid**: "Walk me through what `docker run` does at the kernel level."
- It unpacks the image (overlayfs), `clone()`s into new namespaces, pivot_roots into the rootfs, mounts /proc and /sys, writes cgroup limits, drops capabilities and applies seccomp, then `execve`s the entrypoint.

**Senior**: "Why is `pivot_root` preferred over `chroot` for containers?"
- `chroot` only changes the apparent root and leaves the host root mounted/reachable; `pivot_root` moves the old root aside so it can be unmounted, giving real filesystem isolation.

**Staff**: "Namespaces and cgroups isolate resources — why isn't that enough for security?"
- They don't reduce the kernel attack surface; a single shared kernel means a syscall or kernel bug can break out, so you also need capability dropping, seccomp syscall filtering, an LSM (AppArmor/SELinux), user namespaces, and ideally a sandboxed runtime (gVisor/Kata) for hostile workloads.

## Next Chapter

→ Move to [L02/C08 — Performance Analysis](../C08/README.md)
