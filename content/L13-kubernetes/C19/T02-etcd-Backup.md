# L13/C19/T02 — etcd Backup & Restore (Operations)

## Learning Objectives

- Operate etcd backups in production
- Restore confidently

## Recap

etcd recovery covered in L13/C16/T04 (Troubleshooting). This is operational.

## Schedule

Minimum: daily.
Recommended: hourly.
Tier-0: every 15 min.

For: tighter RPO.

## Automated CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: etcd-backup
  namespace: kube-system
spec:
  schedule: "0 * * * *"   # hourly
  jobTemplate:
    spec:
      template:
        spec:
          hostNetwork: true
          tolerations:
          - effect: NoSchedule
            operator: Exists
          nodeSelector:
            node-role.kubernetes.io/control-plane: ""
          serviceAccountName: etcd-backup
          containers:
          - name: backup
            image: bitnami/etcd:3.5
            env:
            - name: ETCDCTL_API
              value: "3"
            command:
            - sh
            - -c
            - |
              SNAPSHOT=/backup/etcd-$(date +%s).db
              etcdctl --endpoints=https://etcd:2379 \
                --cacert=/etc/kubernetes/pki/etcd/ca.crt \
                --cert=/etc/kubernetes/pki/etcd/server.crt \
                --key=/etc/kubernetes/pki/etcd/server.key \
                snapshot save $SNAPSHOT
              aws s3 cp $SNAPSHOT s3://my-backups/etcd/
              find /backup -mtime +1 -delete
            volumeMounts:
            - name: etcd-certs
              mountPath: /etc/kubernetes/pki/etcd
              readOnly: true
            - name: backup
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: etcd-certs
            hostPath:
              path: /etc/kubernetes/pki/etcd
          - name: backup
            hostPath:
              path: /var/backup
```

Runs on control plane; snapshots; ships to S3; deletes local old.

## S3 Lifecycle

```yaml
LifecycleRules:
- Status: Enabled
  Filter:
    Prefix: etcd/
  Transitions:
  - Days: 30
    StorageClass: GLACIER
  Expiration:
    Days: 365
```

For: cost + retention.

## Cross-Region

```bash
aws s3 cp $SNAPSHOT s3://my-backups-us-west-2/etcd/ --region us-west-2
```

For: regional disaster.

## Verify Snapshot

```bash
ETCDCTL_API=3 etcdctl snapshot status snap.db -w table
# +----------+----------+------------+------------+
# | hash     | revision | total keys | total size |
# +----------+----------+------------+------------+
# | abc123   | 1234567  | 12345      | 100 MB     |
# +----------+----------+------------+------------+
```

Sanity check: keys + size match expected.

## Restore Procedure

Recap from L13/C16/T04:
1. Stop API servers (move static manifests)
2. Stop etcd
3. Restore on each member with snapshot
4. Update etcd config (new data-dir)
5. Start etcd
6. Start API server

For managed K8s: provider handles.

## Test Restore

Quarterly:
1. Spin test cluster
2. Snapshot
3. Make changes
4. Restore from snapshot
5. Verify state pre-changes
6. Document time

Without test: assume DR fails.

## Velero Integration

Velero backs up K8s resources via API:
```bash
velero backup create daily --include-namespaces='*' --snapshot-volumes
```

Stores in S3. Restores via API.

For: per-namespace recovery.

## etcd Snapshot vs Velero

| | etcd Snapshot | Velero |
|---|---|---|
| Layer | etcd | K8s API |
| Scope | Full cluster | Per-namespace selectable |
| PV data | No | Yes (CSI snapshot or restic) |
| Restore | Whole cluster | Selective |
| Managed K8s | Provider | You |

For full DR: etcd (self-managed) or rely on provider.
For app-level backup: Velero.

## Pre-Maintenance

Before risky operations (upgrade, etc.):
1. Snapshot
2. Verify
3. Proceed
4. Snapshot after

For: rollback option.

## Monitoring

Alert if backup fails:
```yaml
- alert: ETCDBackupMissing
  expr: time() - kube_cronjob_status_last_schedule_time{cronjob="etcd-backup"} > 3600
  for: 5m
```

Backup job didn't run in last hour.

## S3 Permissions

Job needs IAM:
```json
{
  "Action": ["s3:PutObject", "s3:DeleteObject"],
  "Resource": "arn:aws:s3:::my-backups/etcd/*"
}
```

Via IRSA.

## Defrag

After snapshot, defrag (rebalance B+tree):
```bash
etcdctl defrag --endpoints=https://etcd1:2379
# One at a time (locks DB briefly)
```

Reduces size; improves performance.

## Compaction

Old revisions cleaned:
```bash
REV=$(etcdctl endpoint status --write-out=json | jq .[0].Status.header.revision)
etcdctl compact $REV
```

Or auto:
```
--auto-compaction-mode=periodic
--auto-compaction-retention=8h
```

Keep last 8 hours of revisions.

## Encryption

Encrypt snapshots:
```bash
aws s3 cp snap.db s3://backups/ --sse aws:kms --sse-kms-key-id alias/mykey
```

For: protect snapshot itself.

Or backup bucket SSE default.

## Snapshot Size

Typically: 10s-100s of MB for normal cluster.

For huge: 1 GB+. Compress + ship efficiently.

## Multi-Cluster

Per cluster: own backup job.

For fleet: central monitoring.

## SOC Audit Evidence

Snapshots demonstrate:
- DR planning
- RPO compliance
- Recovery capability tested

Document procedure + retention.

## RPO / RTO

RPO: data loss tolerance.
- Hourly snapshots: RPO 1 hr
- 15-min: RPO 15 min

RTO: recovery time.
- Snapshot restore: 30-60 min (self-managed)
- Plus cluster validation

For tighter RPO/RTO: more frequent + automation.

## Cost

Storage:
- 100 MB snapshot × hourly × 7 days = 16.8 GB
- S3: $0.40/mo
- + Glacier for old: cheaper

For huge clusters: TB-scale snapshots; manage carefully.

## CronJob Health

```bash
kubectl get cronjob etcd-backup -n kube-system
# LAST SCHEDULE  AGE
# 30m            7d
```

Last schedule = recent? Or stuck?

## Common Mistakes

- No backup
- Backup on same disk
- No off-site
- Never tested
- Job runs but fails silently (no monitoring)
- Retention forever (cost)

## Best Practices

- Hourly + off-site
- Verify status
- Test restore quarterly
- Retention policy
- Encrypted snapshots
- Monitor backup job
- Document procedure
- Backup before risky ops

## Quick Refs

```bash
# Snapshot
etcdctl snapshot save snap.db

# Status
etcdctl snapshot status snap.db -w table

# Restore (each member)
etcdctl snapshot restore snap.db \
  --data-dir=/var/lib/etcd-new \
  --initial-cluster=N1=URL1,N2=URL2,N3=URL3 \
  --initial-advertise-peer-urls=URL \
  --name=N1

# CronJob (above)

# S3
aws s3 cp snap.db s3://backups/etcd/
aws s3 ls s3://backups/etcd/
```

## Interview Prep

**Mid**: "etcd backup approach."

**Senior**: "Test restore procedure."

**Staff**: "DR for self-managed cluster."

## Next Topic

→ [T03 — Certificate Rotation](T03-Cert-Rotation.md)
