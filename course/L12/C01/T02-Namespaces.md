# L12/C01/T02 — Namespaces (Recap from L02)

## Learning Objectives

- Understand each namespace type
- Apply to containers

## Linux Namespaces

Process-level isolation. Each:
- Subset of system resource
- Process sees only its namespace

Container uses multiple namespaces; isolated environment.

## Types

| Namespace | Isolates |
|---|---|
| pid | Process IDs |
| net | Network stack |
| mnt | Filesystem mounts |
| uts | Hostname + domain |
| ipc | IPC (semaphores, queues) |
| user | UIDs / GIDs |
| cgroup | cgroup view (1.18+) |
| time | Clock (newer; uncommon) |

## PID Namespace

Each container: own PID tree.
- Container's PID 1: app process
- Host sees with different PID

```bash
docker run -d nginx
docker exec <container> ps
# PID 1: nginx

ps aux | grep nginx
# (host PID, e.g., 12345)
```

PID 1 special:
- Reaps zombies
- Handles signals
- App should handle SIGTERM (else SIGKILL after grace)

## Network Namespace

Each container: own network stack.
- Own interfaces
- Own routing
- Own iptables

```bash
docker run -it alpine
ip addr
# eth0 (container's)
ifconfig
```

Networking modes (covered C05):
- bridge: default; veth pair
- host: shares host network
- none: no network
- overlay: cross-host (Swarm/K8s)

## Mount Namespace

Each container: own filesystem view.
- Own root (/)
- Bind mounts isolated
- Doesn't see host's mounts

```bash
docker run -it alpine
ls /
# Container's root
mount
# Container's mounts
```

Volumes / bind mounts (covered C06):
- Volume: managed by Docker
- Bind: host path mounted
- tmpfs: RAM

## UTS Namespace

Hostname + domain isolation.

```bash
docker run -it --hostname myhost alpine
hostname
# myhost
```

Each container: own hostname.

## IPC Namespace

System V IPC + POSIX shared memory.

For: prevent inter-container IPC (without explicit setup).

## User Namespace

Map UIDs:
- Container's UID 1000 = host's UID 100000
- Container's "root" (UID 0) ≠ host root

Defense in depth: escape doesn't give root.

```bash
docker run --user 1000 alpine id
# uid=1000 gid=0
```

For: rootless containers.

## Cgroup Namespace

Container sees own cgroup hierarchy.

For: cgroup-aware tools (some monitoring) in container.

## Time Namespace

Container time can be offset from host:
```bash
unshare --time --boottime=10000000 bash
# Container time +10M seconds
```

Rare; testing apps with time differences.

## Create Namespace (Raw)

```bash
# Spawn shell in new PID namespace
sudo unshare --pid --fork --mount-proc bash

# In shell:
ps   # PID 1 = bash
```

Docker does this for you; under hood.

## Inspect Container Namespaces

```bash
# Get container PID
PID=$(docker inspect <container> --format '{{.State.Pid}}')

# Enter container namespaces
sudo nsenter -t $PID -m -p -n bash
# Now in container's mount, PID, net namespace
```

For debugging.

## /proc/<pid>/ns/

```bash
ls -l /proc/$PID/ns/
# pid -> pid:[4026532...]
# net -> net:[4026532...]
# mnt -> mnt:[...]
# ...
```

Same identifier = same namespace.

## Namespace Sharing

Multiple processes in same namespace:
- Same PID space → see each other
- Same network → share interfaces

For sidecars / mesh: containers in same pod share namespaces.

K8s pod: shared net + IPC; separate mnt.

## Why Useful

- App isolation (process trees, networks)
- Reuse OS (vs VM with whole OS)
- Lightweight (just kernel features)
- Configurable per resource type

## Create + Join

Container:
1. Runtime creates new namespaces
2. Forks process
3. Process moves into namespaces
4. Process execs app

Now isolated.

## Persistence

Namespaces exist while any process is in them.
- All processes exit → namespace gone

For container restart: new namespaces.

## Docker Examples

```bash
# Custom PID namespace
docker run --pid=host alpine ps   # see host processes

# Share network with another container
docker run --net=container:other alpine

# Host networking
docker run --net=host alpine

# Custom hostname
docker run --hostname=mybox alpine hostname
```

## K8s Pod = Shared Namespaces

Pod containers share:
- Network (one IP)
- IPC
- UTS (hostname)

Don't share:
- Mount (each: own FS)
- PID (configurable; default no)

For: sidecar mesh, log shipper.

## Performance

Namespace creation: <1ms.
Process in namespace: same as outside (no syscall overhead).

For: containers are fast.

## Security

Namespaces provide isolation but:
- Same kernel
- Kernel exploits bypass
- Other risks (mounts, sysctls)

For strong isolation: VM-based runtime (gVisor, Kata).

## Debugging Namespace Issues

```bash
# Container's mounts
docker exec <container> mount

# Container's processes
docker top <container>

# Container's network
docker exec <container> ip addr
docker exec <container> ss -tunlp

# Enter namespace
PID=$(docker inspect <container> --format '{{.State.Pid}}')
sudo nsenter -t $PID -m -p -n bash
```

## Container vs Host Process

```bash
# Container PID 1
docker inspect <container> --format '{{.State.Pid}}'
# Returns host PID, e.g., 12345

# Host
ps -p 12345
# Process with original command

# Process tree
pstree -p 12345
```

Same process; PID space differs.

## Common Mistakes

- Assuming container == VM (kernel shared)
- Privileged containers (loses isolation)
- /proc, /sys mounts disclosing host info
- User namespace not used (root escapes)

## Best Practices

- Use all default namespaces
- User namespace where possible
- Non-root inside container (USER directive)
- Mount only what's needed
- Restrict capabilities + seccomp

## Quick Refs

```bash
# Inspect
ls /proc/$PID/ns/
docker inspect CONTAINER

# Enter
sudo nsenter -t PID -m -p -n bash

# Create (raw)
unshare --pid --fork --mount-proc bash
```

## Interview Prep

**Mid**: "What namespaces isolate."

**Senior**: "User namespace for security."

**Staff**: "Container isolation guarantees."

## Next Topic

→ [T03 — Cgroups (Recap from L02)](T03-Cgroups.md)
