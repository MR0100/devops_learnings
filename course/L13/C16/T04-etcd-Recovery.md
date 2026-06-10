# L13/C16/T04 — etcd Recovery

## Learning Objectives

- Recover etcd
- Restore from snapshot

## Critical

etcd holds ALL K8s state. Lost = cluster lost.

For managed K8s (EKS / GKE / AKS): provider handles. You can't access etcd directly.

For self-hosted: critical to backup + know recovery.

## Snapshot

```bash
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/snap-$(date +%s).db
```

Required: TLS certs.

Snapshot is point-in-time.

## Verify

```bash
etcdctl snapshot status /backup/snap.db -w table
```

Shows revision, size, hash.

## Schedule Backup

K8s CronJob:
```yaml
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
          hostNetwork: true
          containers:
          - name: etcd-backup
            image: bitnami/etcd
            env:
            - name: ETCDCTL_API
              value: "3"
            volumeMounts:
            - name: etcd-certs
              mountPath: /etc/kubernetes/pki/etcd
            - name: backup
              mountPath: /backup
            command:
            - sh
            - -c
            - |
              etcdctl --endpoints=https://etcd:2379 \
                --cacert=/etc/kubernetes/pki/etcd/ca.crt \
                --cert=/etc/kubernetes/pki/etcd/server.crt \
                --key=/etc/kubernetes/pki/etcd/server.key \
                snapshot save /backup/snap-$(date +%s).db
              aws s3 cp /backup/snap-*.db s3://my-backups/etcd/
          ...
```

Hourly + offsite to S3.

## Retention

Keep:
- Hourly for 24 hr
- Daily for 7 days
- Weekly for 30 days

Delete older.

## Restore Scenarios

### Single Member Lost (HA Cluster)
3 members; 1 fails. Cluster still works (quorum = 2).

```bash
# Remove dead member
etcdctl member remove <id>

# Add new member
etcdctl member add new-member --peer-urls=https://10.0.0.5:2380

# Start new etcd with --initial-cluster-state=existing
```

Data syncs from healthy members.

### Quorum Lost
3 members; 2 fail. Cluster read-only / unusable.

Recover:
```bash
# On surviving member: restore from snapshot
etcdctl snapshot restore /backup/snap.db --data-dir=/var/lib/etcd-new ...

# Reconfigure as new single-node cluster
# Restart etcd with new data dir
```

Then bring up other members.

### All Members Lost
Catastrophic. Restore from snapshot:

```bash
# On each new etcd node
etcdctl snapshot restore /backup/snap.db \
  --data-dir=/var/lib/etcd-new \
  --initial-cluster master-1=https://10.0.0.1:2380,master-2=https://10.0.0.2:2380,master-3=https://10.0.0.3:2380 \
  --initial-advertise-peer-urls=https://10.0.0.1:2380 \
  --name=master-1

# Update etcd config:
# data-dir: /var/lib/etcd-new
# Start etcd

# Repeat on each node with own name/peer-urls
```

API server reconnects automatically.

## Procedure (Full Cluster Restore)

1. Stop API server on all control plane nodes (avoid writes during restore)

```bash
# On each
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
# Static pod removed; kubelet stops it
```

2. Stop etcd

```bash
mv /etc/kubernetes/manifests/etcd.yaml /tmp/
```

3. Restore on each member

```bash
ETCDCTL_API=3 etcdctl snapshot restore /backup/snap.db \
  --data-dir=/var/lib/etcd-new \
  --initial-cluster=NODE_LIST \
  --initial-advertise-peer-urls=https://NODE_IP:2380 \
  --name=NODE_NAME
```

4. Update etcd manifest

```yaml
# /etc/kubernetes/manifests/etcd.yaml
volumes:
- name: etcd-data
  hostPath:
    path: /var/lib/etcd-new   # new dir
```

5. Restart etcd

```bash
mv /tmp/etcd.yaml /etc/kubernetes/manifests/
```

6. Wait for etcd ready

```bash
etcdctl endpoint health
```

7. Restart API server

```bash
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

8. Verify

```bash
kubectl get nodes
kubectl get pods -A
```

State as of snapshot time.

## What's Restored

- All K8s resources
- Workloads, secrets, configs

What's NOT restored:
- App data in PVs (separate backup)
- Logs in storage
- Snapshots themselves (don't include /var/lib/etcd in snapshot)

## What's Lost

Changes between snapshot + now:
- New workloads created
- Recent updates
- Logs / events

For HA: gap minimal (hourly snapshot = ≤1 hr loss).

## Test Restore

Annually:
1. Test cluster
2. Create snapshot
3. Restore on test
4. Verify state intact
5. Document time taken

Without test: assume DR fails.

## Disaster Recovery RTO/RPO

For etcd:
- RPO: 1 hour (hourly snapshots)
- RTO: 30-60 minutes (manual restore)

For automated tools: faster.

Managed K8s: provider handles; opaque to you.

## Velero

Backs up K8s resources + PV data:
- etcd not directly (uses API server)
- Recovers state via API

```bash
velero backup create daily --include-namespaces my-ns
velero restore create --from-backup daily
```

For: per-workload backups. Different from etcd snapshot.

## Velero vs etcd Snapshot

| | etcd Snapshot | Velero |
|---|---|---|
| Layer | etcd | API |
| Scope | Whole cluster | Selected resources |
| PV data | No | Yes (CSI snapshot or restic) |
| Restore | Full cluster | Selective |
| Self-hosted | Yes | Yes |
| Managed | No (provider) | Yes |

Use both. etcd for full DR; Velero for app-level.

## Managed K8s

For EKS:
- Control plane managed
- No etcd access
- Backup K8s state via Velero
- No snapshot/restore of cluster itself

For full cluster recovery in EKS:
1. New cluster via Terraform/eksctl
2. Velero restores resources

For self-hosted: must do etcd backups yourself.

## Common Mistakes

- No backup
- Backups not tested
- Snapshots on same disk (lost together)
- No offsite
- Manual restore in panic without practice
- Snapshot + restore on different etcd versions

## Best Practices

- Hourly snapshots
- Off-site (S3 with cross-region)
- Encrypt backups
- Test restore quarterly
- Document procedure
- Monitor snapshot job
- Snapshot before risky changes

## Pre-Snapshot Compact + Defrag

For consistent backup, do before:
```bash
# Get current revision
REV=$(etcdctl endpoint status --write-out=json | jq .[0].Status.header.revision)

# Compact
etcdctl compact $REV

# Defrag (one node at a time)
etcdctl defrag --endpoints=https://10.0.0.1:2379
```

Reduces snapshot size.

## etcd Health

```bash
etcdctl endpoint health
etcdctl endpoint status -w table
etcdctl member list
```

Run regularly.

## Slow etcd

If etcd slow:
- All K8s slow
- Disk latency typical cause
- Use NVMe SSD

```bash
# Disk latency
ioping -c 5 /var/lib/etcd
# Should be <1ms
```

## Quick Refs

```bash
# Snapshot
etcdctl snapshot save /backup/snap.db

# Verify
etcdctl snapshot status /backup/snap.db -w table

# Restore
etcdctl snapshot restore /backup/snap.db \
  --data-dir=/var/lib/etcd-new \
  --initial-cluster=... \
  --initial-advertise-peer-urls=https://IP:2380 \
  --name=NAME

# Health
etcdctl endpoint health
etcdctl endpoint status -w table
etcdctl member list
```

## Interview Prep

**Mid**: "etcd snapshot."

**Senior**: "Full cluster restore from snapshot."

**Staff**: "DR plan for K8s control plane."

## Next Topic

→ [T05 — Node Not Ready](T05-Node-Not-Ready.md)
