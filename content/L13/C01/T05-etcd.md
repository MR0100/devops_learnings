# L13/C01/T05 — etcd Deep Dive

## Learning Objectives

- Operate etcd safely
- Backup + restore

## etcd

Distributed KV store. K8s state lives here.

- Written in Go (CoreOS / RedHat)
- Raft consensus
- gRPC API
- Watch support (used by K8s)
- TLS required

## Cluster Topology

3 or 5 nodes for HA:
- 3 nodes: tolerate 1 failure (quorum 2)
- 5 nodes: tolerate 2 failures (quorum 3)

Even numbers don't add fault tolerance; just adds overhead.

## Raft

Consensus protocol:
- Elects leader
- Leader handles writes
- Followers replicate
- Quorum acks before commit

If leader fails: election; new leader.

Read can be from leader (linearizable) or any node (serializable; may be stale).

## Stacked vs External

### Stacked
etcd runs on control plane nodes. Default for kubeadm. Simple.

### External
Dedicated etcd cluster. Best for big production:
- Independent scaling
- Failure isolation
- Stronger HA

## Storage Backend

bbolt (Go port of BoltDB). B+tree on disk.

Configurable:
- Quota (default 2 GB; up to 8 GB recommended max)
- Data dir (use fast disk)

## Performance

Latency-sensitive:
- fsync on every write
- Slow disk → slow K8s
- NVMe SSD strongly recommended for production
- Network latency between members matters

Quotas:
- Single keyspace limit ~8 GB
- For huge clusters: shard / clean up

## What's Stored

Everything K8s manages:
- Pods (millions of items in big clusters)
- ConfigMaps, Secrets
- Custom Resources
- Leader election locks
- Service registry

Compaction periodically reclaims space.

## Encryption At Rest

Configure EncryptionConfiguration:
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64>
  - identity: {}   # fallback
```

API Server encrypts before writing to etcd.

For: protect Secrets at rest.

## Backup

CRITICAL. etcd loss = cluster loss.

```bash
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/etcd-$(date +%s).db
```

Schedule (cron, K8s CronJob):
- Hourly snapshots
- Retain 7 days
- Ship to S3 (off-site)

## Restore

Disaster: all etcd nodes lost.

```bash
# Stop API server (so it doesn't see partial state)
# Stop existing etcd

# Restore on each member
ETCDCTL_API=3 etcdctl snapshot restore /backup/snap.db \
  --data-dir /var/lib/etcd-new \
  --initial-cluster master-1=https://10.0.0.1:2380,master-2=...,master-3=... \
  --initial-advertise-peer-urls https://10.0.0.1:2380 \
  --name master-1

# Update etcd config to use new data-dir
# Start etcd
# Start API server
```

For managed K8s: provider handles backup/restore.

## Performance Tuning

```yaml
# etcd startup flags
--quota-backend-bytes=8589934592   # 8 GB quota
--auto-compaction-mode=periodic
--auto-compaction-retention=8h
--listen-peer-urls=https://0.0.0.0:2380
--listen-client-urls=https://0.0.0.0:2379
```

Disk:
- NVMe SSD
- Dedicated disk (not OS disk)
- Fast network between members

## Compaction

Removes old revisions:
- Automatic (configured) or manual
- Periodic vs revision-count

```bash
etcdctl compact <rev>
```

Without: keyspace grows; performance degrades.

## Defrag

After compaction, defrag reclaims free space:
```bash
etcdctl defrag
```

One node at a time (locks DB).

## Health

```bash
etcdctl endpoint health
etcdctl endpoint status -w table
etcdctl member list
```

For monitoring.

## Members

Add member:
```bash
etcdctl member add master-3 --peer-urls=https://10.0.0.3:2380
# Then start new etcd with --initial-cluster-state=existing
```

Remove:
```bash
etcdctl member remove <id>
```

Careful: don't lose quorum.

## Failure Modes

### One Member Down (3-node)
- Cluster healthy (quorum 2/3 → 2)
- Replace member ASAP

### Quorum Lost
- All writes fail
- Reads on remaining may succeed
- Cluster effectively read-only

Recover: restart members; if data corrupt, restore from snapshot.

### Disk Full
- Writes fail
- Compact + defrag + free disk

### Slow Disk
- etcd writes slow
- All K8s operations slow
- Symptoms: kubectl apply takes seconds; controllers lag

Fix: faster disk; isolate etcd.

## Monitoring

Key metrics:
- `etcd_server_has_leader`
- `etcd_server_leader_changes_seen_total` (high = bad)
- `etcd_disk_backend_commit_duration_seconds`
- `etcd_disk_wal_fsync_duration_seconds`
- `etcd_mvcc_db_total_size_in_bytes` (vs quota)
- `etcd_server_proposals_committed_total`

Alert on:
- No leader
- Frequent leader changes
- Slow commits / fsyncs
- Approaching quota

## etcdctl Commands

```bash
# Get key
etcdctl get /registry/pods/default/mypod

# Watch
etcdctl watch /registry/pods/ --prefix

# Delete (DANGEROUS)
etcdctl del /key

# Range
etcdctl get / --prefix --keys-only | head

# Compact + defrag
etcdctl compact <rev>
etcdctl defrag
```

## Don't Direct Edit

NEVER:
- etcdctl del /registry/...
- Modify etcd directly

Always go through API Server. Direct edits bypass validation; can corrupt cluster.

## Managed K8s

For EKS / GKE / AKS:
- etcd hidden; provider manages
- Backup automatic (provider responsibility)
- Restore on disaster: limited; sometimes new cluster
- Auto-scale + patch

You don't operate etcd directly.

## Sizing

For 5000-node cluster:
- 5-member etcd
- 16-32 GB RAM per member
- 100+ GB NVMe SSD per member
- 10 Gbps network

For 100-node cluster:
- 3-member etcd
- 8 GB RAM
- 50 GB SSD

## Common Issues

### "database space exceeded"
Quota hit. Compact + defrag.

### Slow commits
Disk latency. Switch to NVMe.

### High leader changes
Network issues between members. Investigate.

### Stale data
Etcd-API gateway lag. Usually self-resolves.

## Common Mistakes

- Editing etcd directly (`etcdctl put`/`del` on `/registry/...`) instead of going through the API Server — bypasses validation and corrupts the cluster.
- Running an even number of members (e.g. 2 or 4) — adds overhead without improving fault tolerance and makes losing quorum more likely.
- Putting etcd on slow or shared disks — every write does an fsync, so disk latency makes all of Kubernetes slow.
- No off-site snapshots (or never testing restore) — etcd loss is cluster loss, and an untested backup is not a backup.
- Letting the keyspace grow without scheduled compaction + defrag, then hitting "database space exceeded" and stalling all writes.
- Ignoring leader-change and fsync metrics until quorum is already lost.

## Best Practices

- 3 or 5 members
- NVMe SSD
- Dedicated nodes (external etcd)
- Daily snapshots → off-site
- Monitor metrics
- Compact + defrag scheduled
- Encryption at rest
- TLS between members
- Restoration tested

## Disaster Recovery

Test annually:
1. Take snapshot
2. Spin up new cluster from snapshot
3. Verify state
4. Document procedure

If never tested: assume it won't work.

## Snapshots Procedure

For managed: provider does.

For self-hosted:
```yaml
# K8s CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: etcd-backup
spec:
  schedule: "0 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: bitnami/etcd
            command: ["sh", "-c"]
            args:
            - |
              etcdctl snapshot save /backup/etcd-$(date +%s).db
              aws s3 cp /backup/etcd-*.db s3://my-backups/etcd/
              find /backup -mtime +7 -delete
```

Adapt for your env.

## Quick Refs

```bash
# Health
etcdctl endpoint health
etcdctl endpoint status -w table

# Snapshot
etcdctl snapshot save snap.db

# Restore (each member)
etcdctl snapshot restore snap.db --data-dir ...

# Member ops
etcdctl member list
etcdctl member add NAME --peer-urls=...
etcdctl member remove ID

# Compact
etcdctl compact REV
etcdctl defrag
```

## Interview Prep

**Mid**: "What is etcd."

**Senior**: "etcd backup + restore."

**Staff**: "Tuning etcd for huge cluster."

## Next Topic

→ Move to [L13/C02 — Core Workload Resources](../C02/README.md)
