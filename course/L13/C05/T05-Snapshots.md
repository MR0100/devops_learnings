# L13/C05/T05 — Snapshots

## Learning Objectives

- Use VolumeSnapshots
- Backup + restore PVCs

## VolumeSnapshot

Point-in-time copy of volume:
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: snap-2024-06-09
spec:
  volumeSnapshotClassName: csi-snap-class
  source:
    persistentVolumeClaimName: my-pvc
```

Driver creates underlying storage snapshot (EBS snapshot, etc.).

## VolumeSnapshotClass

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snap-class
driver: ebs.csi.aws.com
deletionPolicy: Retain
parameters:
  encrypted: "true"
```

Like StorageClass; per driver.

## VolumeSnapshotContent

Bound to VolumeSnapshot. Represents underlying snapshot:
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotContent
spec:
  source:
    snapshotHandle: snap-xxxxx
  ... 
```

Usually auto-created. Manual for adopting existing.

## Restore from Snapshot

Create new PVC with dataSource:
```yaml
spec:
  storageClassName: gp3
  dataSource:
    name: snap-2024-06-09
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 50Gi
```

Driver creates new volume from snapshot.

## Use Cases

### Backup
Daily snapshots; retention. Restore on disaster.

### Cloning
Spin up test DB from prod snapshot.

### Migration
Snapshot, create PVC in new namespace / cluster.

### Pre-Upgrade
Snapshot before risky operation; restore on failure.

## Scheduled Snapshots

K8s native: no built-in scheduling. Use:
- CronJob with kubectl
- Velero with snapshot
- Backup tool with snapshot integration

```yaml
apiVersion: batch/v1
kind: CronJob
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: snapshot
            image: bitnami/kubectl
            command:
            - kubectl
            - apply
            - -f
            - /config/snap.yaml
            volumeMounts:
            - name: tpl
              mountPath: /config
          volumes:
          - name: tpl
            configMap:
              name: snap-template
```

## Velero

K8s-aware backup:
- Backs up resources + PV data
- Supports CSI snapshots
- Or restic for non-CSI volumes
- Restores to same / different cluster

```bash
velero backup create daily --include-namespaces prod
velero restore create --from-backup daily
```

For DR + cluster migration.

## Restic / Kopia

Velero uses Restic / Kopia for non-CSI backups:
- Reads files from running pod
- Backs up to S3
- Slower than CSI snapshot
- Useful for emptyDir, hostPath

## Cross-Region Backup

Snapshots are regional (most clouds). For cross-region:
- AWS EBS: copy snapshot to another region
- Manual via CLI:
```bash
aws ec2 copy-snapshot --source-region us-east-1 --source-snapshot-id snap-xxx --destination-region us-west-2
```

Or use DLM / AWS Backup.

## Restore Process

1. Create PVC with dataSource → snapshot
2. New PV from snapshot
3. Pod with new PVC
4. Restore complete

For: rolling back, testing, DR.

## Stateful Set Restore

For StatefulSet:
1. Snapshot each PVC
2. Delete StatefulSet (preserve PVCs)
3. Create new PVCs from snapshots
4. Recreate StatefulSet to use new PVCs

Complex; operators handle.

## DB-Level Backups vs Snapshots

Snapshots: storage-level; whole volume.
DB-level (pg_dump, mysqldump): logical; queryable.

Use both:
- Snapshots: fast restore
- Logical: portable, point-in-time DB-level

For prod: both.

## Snapshot Performance

Some CSIs use incremental:
- First: full
- Subsequent: only changed blocks
- Storage efficient

EBS snapshots: incremental.

## Snapshot Storage

EBS snapshots → S3 (managed; cheap).
Other clouds similar.

Cost: $0.05/GB-mo typically. Cheap.

## Retention

Define retention:
- Daily for 7 days
- Weekly for 30 days
- Monthly for 1 year

Auto-cleanup via DLM (AWS), or backup tool.

## Live vs Crash-Consistent

CSI snapshot: storage-level; "crash-consistent" — like power loss.

For DB integrity:
- App quiesce before snapshot
- Or use DB-level snapshot (pg_basebackup)

For safety: snapshot during off-peak; tested restore.

## VolumeGroupSnapshot (Alpha)

Snapshot multiple PVCs atomically:
- For multi-volume DBs (data + WAL)
- Consistent across volumes

In progress; check K8s version.

## Common Issues

### Snapshot Stuck
Driver issue. Check controller logs.

### Restore Slow
- Snapshot pulled from S3 (lazy)
- First I/O slow
- Pre-warm with `fio` after restore

### Snapshot Quota
Cloud may limit snapshots. AWS: ~10000 per region default.

## Best Practices

- Automated schedule (Velero or CronJob)
- Cross-region copy for DR
- Logical backups too (pg_dump)
- Test restore quarterly
- Tag snapshots with timestamps
- Retention policy
- Document RTO/RPO

## DR Testing

Quarterly:
1. Create snapshot
2. Restore to new namespace / cluster
3. Verify data integrity
4. Time it
5. Document

Without testing: assume DR doesn't work.

## Operators with Snapshots

CNPG (Postgres):
```yaml
spec:
  backup:
    barmanObjectStore:
      destinationPath: s3://backups
    retentionPolicy: 30d
```

Operator handles: snapshots, base backups, WAL archiving.

## Common Mistakes

- Snapshot without testing restore
- Same-region snapshot only (region failure → lost)
- DB not quiesced (corrupt snapshot)
- Retention forever (cost)
- No tag / metadata (can't find right snapshot)

## Cost Considerations

For 100 GB DB × 30 daily snapshots:
- Naïvely: 3000 GB × $0.05 = $150/mo
- Incremental: ~1.5× DB size = 150 GB × $0.05 = $7.50/mo
- Cross-region copy: extra storage there

For massive DBs: real money.

## Restore Time

Snapshot to new volume:
- AWS EBS: minutes (lazy fetch from S3); full perf takes longer
- Local FS snapshot: seconds (CoW)

Plan RTO accordingly.

## Pre-Warming

After EBS snapshot restore:
```bash
dd if=/dev/xvdf of=/dev/null bs=1M
# Touches all blocks; pulls from S3
```

For consistent performance.

## Quick Refs

```bash
# Create snapshot
kubectl apply -f snapshot.yaml

# List
kubectl get volumesnapshot

# Describe
kubectl describe volumesnapshot snap-2024-06-09

# Velero
velero backup create my-backup --include-namespaces prod
velero restore create --from-backup my-backup

# AWS EBS direct
aws ec2 describe-snapshots --filters Name=volume-id,Values=vol-xxx
```

## Interview Prep

**Mid**: "K8s VolumeSnapshot."

**Senior**: "Backup strategy for stateful platform."

**Staff**: "DR for K8s with snapshots."

## Next Topic

→ Move to [L13/C06 — Security](../C06/README.md)
