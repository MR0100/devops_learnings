# L13/C20/T02 — Disaster Recovery

## Learning Objectives

- Plan K8s DR
- Use Velero

## DR Scope

Possible disasters:
- Cluster lost (etcd corruption, region failure)
- Namespace deleted
- PV data lost
- Workload misconfigured / broken
- Provider outage

Each: different recovery.

## RTO / RPO

- RTO: Recovery Time Objective
- RPO: Recovery Point Objective

For K8s:
- Tier-0: RTO < 1 hr, RPO < 15 min
- Tier-1: RTO < 4 hr, RPO < 1 hr
- Tier-2: RTO < 24 hr, RPO < 24 hr

Define per workload.

## Cluster-Level DR

### etcd Snapshot
Covered C16/T04 + C19/T02.

For self-managed: hourly snapshots → S3 → restore.

For managed: provider responsibility.

### Cluster Rebuild
- Terraform / CAPI / eksctl
- Reproducible from code
- Apply manifests / GitOps
- Restore data

RTO: 1-4 hr typically.

## Workload-Level DR

### Velero
Backs up K8s resources + PV data:

```bash
velero install --provider aws --bucket my-backups --backup-location-config region=us-east-1
velero backup create daily --include-namespaces='*'
velero schedule create daily --schedule='@daily' --include-namespaces='*'
```

Snapshot K8s state.

### Restore
```bash
velero restore create --from-backup daily
```

To same cluster or new.

### Selective
```bash
velero backup create prod-only --include-namespaces=production
velero restore create --from-backup prod-only --restore-volumes=true
```

For: per-namespace recovery.

## PV Backup

### CSI Snapshots
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: db-snap
spec:
  source:
    persistentVolumeClaimName: db-pvc
```

Storage-level; fast.

### Restic (Velero)
For non-CSI volumes:
```yaml
spec:
  defaultVolumesToRestic: true
```

Velero copies files via restic; slower but works on any volume.

## App-Level Backup

DB-specific:
- pg_dump for Postgres
- mysqldump for MySQL
- Mongodump for MongoDB

Sometimes more reliable than storage snapshots.

For DBs: operator (CNPG, etc.) handles.

## DR Locations

Backups should:
- Off-cluster
- Off-region
- Encrypted
- Versioned (S3 lifecycle)

For: region failure.

## Multi-Region Strategy

### Active-Passive
- Prod in region A
- Standby in region B
- Replicate continuously
- Failover via DNS / mesh

### Active-Active
- Both regions serving
- Traffic split
- DB synchronized

For tier-0: active-active.

## DR Test

Quarterly:
1. Choose scope (full cluster vs namespace)
2. Restore in test environment
3. Verify functionality
4. Measure RTO + RPO
5. Document

Without test: assume DR fails.

## Failover Drills

Game day:
- Simulate cluster failure
- Drain prod cluster
- Restore in DR cluster
- Switch traffic
- Verify

For: validate procedures.

## Tier-0 RTO < 1 hr

Requires:
- Pre-provisioned DR cluster (warm standby)
- Automated restore
- Tested procedures
- DNS / mesh ready to switch

Most companies don't achieve <1 hr.

## Tier-1 RTO 4 hr

Achievable:
- Off-region backups
- Documented manual restore
- Tested

## What Velero Backs Up

- All K8s resources (Deployments, Services, etc.)
- CRDs
- PVs (via snapshot or restic)

What NOT:
- Cluster config (control plane)
- External cloud resources (RDS, S3)

For complete: combine with Terraform state + cloud snapshots.

## What CSI Snapshot Does

- Volume snapshot at storage layer
- Fast for cloud volumes (EBS, GCP PD)
- Restore: new PVC from snapshot

For DBs: snapshot is crash-consistent; not app-aware. Quiesce DB first for safety.

## Velero Restore Steps

For full cluster:
1. New cluster provisioned (Terraform)
2. Velero installed
3. velero restore create --from-backup BACKUP
4. Verify resources + data
5. DNS update

Total: 1-2 hr for typical workload.

## Storage DR

For PVs in single region:
- Lost on region failure
- Need cross-region replication

For RDS / Aurora: cross-region replica.
For EBS: snapshot copy to other region.

## Operator-Specific DR

Operators often have DR features:
- CNPG: continuous backup to S3 + restore
- Strimzi: MirrorMaker for cross-cluster
- ElasticOperator: snapshots

Use operator-native when available.

## Documentation

Per-app runbook:
- What's critical
- Where backups
- How to restore
- Validation steps
- Communication plan
- RTO / RPO

For: incident response not improvisation.

## Communication

During DR event:
- Status page
- Customer comms
- Internal updates
- Stakeholder briefing

For: managed transparency.

## Common Mistakes

- No backup
- Backup on same disk / region
- Never tested
- No runbook
- Single restore path

## Best Practices

- Velero + CSI snapshots
- Off-region storage
- Schedule daily minimum
- Tested quarterly
- Per-namespace + cluster-level
- Documented runbook
- Game day drills
- Multi-region for tier-0

## Cost

Backup storage:
- S3 cheap
- Snapshots: per-GB
- DR cluster: 1× or 2× workload cost

For tier-0: 2× cost; budget accordingly.

## DR Tools

- Velero
- Kasten K10 (Veeam-owned)
- Trilio
- Portworx PX-Backup
- Operator-specific

For most: Velero (free + standard).

## Recovery Validation

After restore:
- App responds
- Data integrity (count records, hash)
- External integrations work
- Performance acceptable

Document checks per app.

## Multi-Cluster DR

For K8s + region-level DR:
- Active cluster in region A
- Standby cluster in region B (or new on demand)
- Velero restores to standby
- Switch traffic (Route 53 / mesh)

## EKS DR

```bash
# Backup
velero backup create eks-backup --include-namespaces='*' --snapshot-volumes

# Restore (new cluster)
velero restore create --from-backup eks-backup --restore-volumes=true
```

EKS itself: cluster recreated via eksctl / Terraform.

## RDS DR

For DBs (RDS):
- Cross-region read replica
- Automated backup
- Snapshot to other region
- Promote replica on disaster

For app DR: combine with K8s workload DR.

## Cluster-as-Code

Cluster definition in Git:
- Terraform for cluster
- ArgoCD for workloads
- DR: re-apply

For: rebuild from scratch in hours.

## Quick Refs

```bash
# Velero
velero install --provider aws --bucket B
velero backup create NAME --include-namespaces='*'
velero restore create --from-backup NAME
velero schedule create daily --schedule='@daily'

# CSI Snapshot
kubectl apply -f volumesnapshot.yaml

# Cluster rebuild
terraform apply
argocd app sync root
```

## Interview Prep

**Mid**: "K8s DR strategy."

**Senior**: "Velero workflow."

**Staff**: "Multi-region DR for K8s platform."

## Next Topic

→ [T03 — Cost Controls](T03-Cost-Controls.md)
