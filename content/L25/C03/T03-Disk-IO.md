# L25/C03/T03 — Disk I/O Saturation

## Learning Objectives

- Inject disk latency, errors, and corruption to find storage-bound failures
- Drive saturation deliberately with `fio` and `fallocate`
- Verify apps survive slow disks, `ENOSPC`, and read faults gracefully

## Why Disk Chaos

Disk is the silent dependency. It rarely fails cleanly — it gets *slow*, or
returns sparse errors, or fills up. Apps that assume disk is instant and
infinite break in ways unit tests never catch:

- A 100ms `fsync` stalls a synchronous write path → request latency explodes
- `ENOSPC` on a log write crashes a process that never handled the error
- A read error on one block should trigger replica failover, but doesn't
- A noisy-neighbor pod saturates shared EBS IOPS → every tenant degrades

## IOChaos (Chaos Mesh)

Chaos Mesh injects faults at the filesystem layer for a target pod via a
sidecar that intercepts syscalls on a mounted path.

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: IOChaos
metadata:
  name: disk-delay
spec:
  action: latency           # latency | fault | attrOverride | mistake
  mode: one                 # one pod from the selector
  selector:
    namespaces: [prod]
    labelSelectors:
      app: postgres
  volumePath: /data         # the mounted volume the sidecar watches
  path: '/data/**/*'        # glob of files to affect
  methods: [write, fsync]   # which syscalls (omit = all)
  percent: 100              # % of matching operations affected
  delay: '100ms'
  duration: '5m'
```

`volumePath` must be a real mount; `path` is a glob *under* it. Narrow
`methods` to model a specific stall (e.g. `fsync` only, to hit commit latency).

## Action Types

| Action         | Effect                          | Tests                              |
|----------------|---------------------------------|------------------------------------|
| `latency`      | Adds delay to I/O ops           | Timeout budgets, slow-disk handling|
| `fault`        | Returns an errno (e.g. ENOSPC)  | Error paths, retries, failover     |
| `attrOverride` | Lies about `stat` attributes    | Size/perm assumptions              |
| `mistake`      | Corrupts read/written bytes     | Checksums, integrity validation    |

## Injecting a Specific Errno

```yaml
spec:
  action: fault
  methods: [write]
  errno: 28          # ENOSPC — "No space left on device"
  percent: 100
```

Common errnos worth testing: `28` ENOSPC, `5` EIO (hardware read error),
`13` EACCES, `122` EDQUOT (quota). Each exercises a different error branch
the app probably never tested.

## Manual Saturation with fio

CRDs model *injected* faults; `fio` produces *real* load — useful outside
Kubernetes and to find the actual IOPS/bandwidth ceiling.

```bash
# Saturate with 4-thread random 4k writes for 60s, then read the summary
fio --name=sat --filename=/data/test --size=2G \
    --rw=randwrite --bs=4k --iodepth=64 --numjobs=4 \
    --direct=1 --time_based --runtime=60 \
    --group_reporting

# Key output to capture: IOPS, bw (MB/s), and clat p99 (tail latency)
```

`--direct=1` bypasses the page cache so you measure the device, not RAM. Run
your service against the same volume during the test and watch its p99.

## Forcing Disk-Full

```bash
# Pre-allocate a giant file to drive the volume toward 100%
fallocate -l 10G /data/big-balloon

# Cleanup
rm /data/big-balloon
```

Tests, in order of what usually breaks:
1. **Detection** — does monitoring fire a `disk_free < 10%` alert *before* full?
2. **Graceful behavior** — does the app return 503 or does it crash on write?
3. **Self-healing** — log rotation / temp cleanup / eviction reclaim space?
4. **Recovery** — after space frees, does the app resume without a restart?

```
df usage:  [██████████████████████████████████░░] 92%  ← alert should fire here
           [████████████████████████████████████] 100% ← writes start failing
```

## What to Verify

During and after any disk experiment:
- App p99 latency and error rate (yours and downstream)
- `iostat -x 1` — `%util`, `await`, `aqu-sz` on the device
- Whether retries fire on `EIO` and reads fail over to a replica
- Whether the app recovered to baseline without manual intervention
- That OTHER pods on the node weren't collateral damage (limits working?)

## Storage Class Matters

Results are meaningless without knowing the backing store. A `gp3` EBS volume
has a *provisioned* IOPS ceiling — chaos that exceeds it is indistinguishable
from a real throttle. Local NVMe behaves completely differently. Always note
the storage class, IOPS limit, and whether the volume is shared.

## Common Mistakes

- Running on a shared/host volume and saturating the *node*, not just the pod
- Testing latency but never `fault` — the error paths are where bugs hide
- Forgetting page cache: without `--direct=1`, `fio` benchmarks RAM
- No `df`/alert check first, so disk-full surprises you instead of the app
- Leaving the balloon file behind and actually filling production disk

## Best Practices

- Start in dev/staging on a dedicated volume; know the storage class first
- Model real failures: `fsync` latency for commits, `ENOSPC` for log/temp paths
- Pair injected IOChaos with real `fio` load to find the true ceiling
- Watch app behavior, not just the disk — verify retries, failover, recovery
- Always have cleanup ready and a `kubectl delete iochaos` abort path

## Quick Refs

```yaml
IOChaos:
  action: latency | fault | attrOverride | mistake
  volumePath: /data          # mount
  path: '/data/**/*'         # glob
  methods: [write, fsync]    # syscalls
  delay: '100ms' | errno: 28 # ENOSPC
  percent: 100
```
```bash
fio --rw=randwrite --bs=4k --iodepth=64 --direct=1 ...  # real load
fallocate -l 10G /data/big                              # fill disk
iostat -x 1   # %util, await    df -h   # free space
kubectl delete iochaos disk-delay                       # abort
```

## Interview Prep

**Junior**: "What is disk I/O chaos?" — Deliberately slowing disk operations, returning errors, or filling the volume to test how the app handles a misbehaving disk.

**Mid**: "How do you simulate disk-full?" — `fallocate -l 10G` to drive usage to 100%, or Chaos Mesh IOChaos `action: fault, errno: 28` (ENOSPC), then verify alerts fire and writes fail gracefully.

**Senior**: "Design a disk experiment for a database." — Inject `fsync` latency on the data volume, watch commit p99 and replication lag, then inject `EIO` reads to confirm the DB fails over to a replica instead of serving corrupt data.

**Staff**: "Why is storage class central to interpreting results?" — Backing store determines the real ceiling; on provisioned-IOPS EBS the chaos may just be hitting the throttle, so without knowing the class, IOPS limit, and whether the volume is shared, the experiment's signal is uninterpretable.

## Next Topic

→ [T04 — Pod / Node Kills](T04-Pod-Node-Kills.md)
