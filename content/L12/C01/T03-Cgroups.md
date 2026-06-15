# L12/C01/T03 — Cgroups (Recap from L02)

## Learning Objectives

- Apply cgroups to containers
- Limit resources

## Cgroups

Linux control groups: resource limits + accounting.

Containers use cgroups for:
- CPU limits
- Memory limits
- I/O limits
- Network bandwidth (with tc)
- Device access

## Versions

- cgroup v1: legacy; separate hierarchies per controller
- cgroup v2: unified hierarchy; modern

Modern Docker / K8s: cgroup v2.

## cgroup v2

Unified `/sys/fs/cgroup/`:
```
/sys/fs/cgroup/
├── system.slice/
├── user.slice/
└── docker/
    └── <container-id>/
        ├── cgroup.controllers
        ├── cpu.max
        ├── memory.max
        └── ...
```

Per cgroup: control files.

## CPU Limits

```bash
docker run --cpus 0.5 alpine
```

Container can use 0.5 CPU (50% of one core).

Under hood:
```
/sys/fs/cgroup/docker/<id>/cpu.max
# 50000 100000
# (50ms per 100ms period = 50%)
```

## CPU Shares (Relative)

```bash
docker run --cpu-shares 512 alpine    # half priority of default 1024
```

For: relative weighting under contention.

## Memory Limits

```bash
docker run -m 256m alpine
```

Container can use up to 256 MB. Beyond: OOM-killed.

```
/sys/fs/cgroup/docker/<id>/memory.max
# 268435456
```

## Memory + Swap

```bash
docker run -m 256m --memory-swap 512m alpine
```

256 MB RAM + 256 MB swap.

## IO Limits

```bash
docker run --device-read-bps /dev/sda:10mb alpine
```

Read max 10 MB/s from /dev/sda.

## CPU Pinning

```bash
docker run --cpuset-cpus 0,1 alpine
```

Container restricted to CPUs 0 and 1.

For: NUMA awareness.

## PIDs Limit

```bash
docker run --pids-limit 100 alpine
```

Container can't fork more than 100 processes.

For: prevent fork bombs.

## Default Behavior

Without limits:
- Use all available
- Compete with other containers
- Risk: one container starves others

For prod: always limits.

## K8s Integration

K8s resource requests/limits map to cgroups:
```yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"
```

kubelet → containerd → runc → cgroup config.

## Reading Usage

```bash
# From cgroup
cat /sys/fs/cgroup/docker/<id>/memory.current
cat /sys/fs/cgroup/docker/<id>/cpu.stat

# Via docker
docker stats <container>
```

## CPU Throttling

CPU limit = CFS quota.

If limit hit: throttled (paused until next period).

```bash
cat /sys/fs/cgroup/docker/<id>/cpu.stat
# throttled_periods: 1234
# throttled_usec: 56000
```

For: identify throttled containers.

## OOM Kill

Memory exceeds limit:
1. Kernel OOM-killer picks victim
2. SIGKILL container's PID 1
3. Container exits (137)

```bash
docker inspect <container>
# OOMKilled: true
```

For: identify OOM.

## Soft Limits

cgroup v2:
- `memory.high`: throttle if exceeded
- `memory.max`: kill if exceeded

```bash
docker run --memory 512m --memory-swap 512m \
  --memory-reservation 256m alpine
```

Reservation: minimum guaranteed.

## Block I/O Weight

```bash
docker run --blkio-weight 500 alpine
```

Relative I/O priority (10-1000; default 500).

## Network (Not cgroup; tc)

```bash
# Not direct cgroup; use tc on container's veth
sudo tc qdisc add dev veth1 root tbf rate 1mbit burst 32kbit latency 400ms
```

For: bandwidth limit.

Or use CNI plugins with bandwidth annotation.

## Inspect

```bash
# All cgroup info for container
docker inspect <container> --format '{{.HostConfig.Resources}}'

# Stats
docker stats --no-stream

# Per-process
cat /sys/fs/cgroup/docker/<id>/cgroup.procs
```

## Resource Accounting

cgroups account:
- CPU time used
- Memory peak
- I/O total
- Network bytes

Used by:
- Prometheus (cAdvisor)
- kubectl top
- Datadog
- Billing systems

## Limits Best Practices

### CPU
- Request: actual avg need
- Limit: avoid setting (CFS throttling) OR generous

### Memory
- Request: actual peak
- Limit: peak + 20% buffer
- OOM is bad; tune

### Test
- Run app under load
- Measure
- Set limits

## Limits Strategies

### Burstable
```yaml
resources:
  requests: {cpu: 100m, memory: 128Mi}
  limits: {memory: 256Mi}   # no CPU limit
```

Common. Bursts CPU; capped memory.

### Guaranteed
```yaml
resources:
  requests: {cpu: 1, memory: 1Gi}
  limits: {cpu: 1, memory: 1Gi}
```

Same req=limit. Predictable; protected.

### BestEffort
```yaml
# no resources block
```

No reserve; first evicted.

For dev/test only.

## Docker Run Examples

```bash
# CPU + memory
docker run --cpus 1 -m 512m alpine

# Pin to CPUs
docker run --cpuset-cpus 0-3 alpine

# PIDs
docker run --pids-limit 50 alpine

# I/O
docker run --device-read-iops /dev/sda:100 alpine

# Combined
docker run \
  --cpus 0.5 \
  -m 256m \
  --memory-swap 512m \
  --cpuset-cpus 0-1 \
  --pids-limit 100 \
  alpine
```

## Kernel Tunables

```bash
# Swappiness
sysctl vm.swappiness=10

# OOM behavior
echo 1 > /proc/sys/vm/overcommit_memory
```

Affect cgroup behavior.

## Cgroup v1 vs v2

| | v1 | v2 |
|---|---|---|
| Hierarchies | Per-controller | Unified |
| Filesystem | /sys/fs/cgroup/cpu/, /memory/ | /sys/fs/cgroup/ |
| Controller | Set per-hierarchy | Set per-cgroup |
| Modern | Legacy | Default new |

Most modern systems: v2.

Check:
```bash
mount | grep cgroup
# tmpfs on /sys/fs/cgroup type tmpfs ... (v2)
```

## Common Mistakes

- No limits (noisy neighbor)
- Too tight memory (OOM cycles)
- CPU limit too low (throttling)
- Ignoring throttling metrics

## Best Practices

- Always set resource requests
- Memory limit = peak + buffer
- Monitor throttling
- Test under load
- Use Vertical Pod Autoscaler recommendations

## Production

- Prometheus for CPU/memory metrics
- Alerts on throttling, OOM
- Right-size periodically
- Cost-aware (over-provisioning waste)

## Quick Refs

```bash
# Docker limits
docker run --cpus N -m XGM CONTAINER

# Inspect
docker stats
cat /sys/fs/cgroup/docker/ID/cpu.max
cat /sys/fs/cgroup/docker/ID/memory.max
cat /sys/fs/cgroup/docker/ID/memory.current

# K8s
kubectl top pod
kubectl describe pod   # shows requests/limits
```

## Interview Prep

**Mid**: "Cgroups in containers."

**Senior**: "CPU throttling."

**Staff**: "Resource strategy for K8s cluster."

## Next Topic

→ [T04 — Union Filesystems (overlayfs)](T04-Union-FS.md)
