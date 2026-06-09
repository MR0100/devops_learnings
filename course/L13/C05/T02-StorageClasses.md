# L13/C05/T02 — StorageClasses & Dynamic Provisioning

## Learning Objectives

- Configure StorageClass
- Use dynamic provisioning

## StorageClass

Template for creating PVs dynamically:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

## How It Works

1. PVC references `storageClassName: gp3`
2. SC provisioner (CSI driver) sees pending PVC
3. CSI provisions storage (EBS volume in AWS)
4. CSI creates PV pointing to volume
5. PV bound to PVC
6. Pod uses PVC

Vs static: admin creates PV manually.

## Common Provisioners

| Provisioner | Storage |
|---|---|
| ebs.csi.aws.com | AWS EBS |
| efs.csi.aws.com | AWS EFS |
| pd.csi.storage.gke.io | GCP PD |
| disk.csi.azure.com | Azure Disk |
| file.csi.azure.com | Azure Files |
| nfs.csi.k8s.io | NFS |
| ceph.com/rbd | Ceph RBD |
| openebs.io/local | Local (OpenEBS) |
| topolvm.io | LVM |

## Default StorageClass

Mark as default:
```yaml
metadata:
  name: gp3
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
```

PVCs without storageClassName get default.

## Parameters (CSI-Specific)

### EBS
```yaml
parameters:
  type: gp3                # gp2, gp3, io1, io2, st1, sc1
  iops: "5000"
  throughput: "250"
  encrypted: "true"
  kmsKeyId: alias/myKey
  fsType: ext4             # xfs
  reclaimPolicy: Delete
```

### EFS
```yaml
parameters:
  provisioningMode: efs-ap
  fileSystemId: fs-xxx
  directoryPerms: "700"
```

## ReclaimPolicy

Per-PV; SC sets default for dynamic:
- **Delete**: delete underlying storage on PVC removal
- **Retain**: keep PV + storage; manual cleanup

For prod data: Retain (often via override).

## VolumeBindingMode

### Immediate
PVC binds ASAP. Risk: wrong AZ if pod scheduled elsewhere.

### WaitForFirstConsumer
PVC waits until pod scheduled. Then bind in correct AZ.

For zonal storage (EBS): mandatory.

## allowVolumeExpansion

```yaml
allowVolumeExpansion: true
```

Then PVC can be patched to larger:
```bash
kubectl patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'
```

CSI driver expands; filesystem grows.

Doesn't shrink.

## Multiple Storage Classes

Common setup:
- `gp3`: general (default)
- `gp3-encrypted`: KMS-encrypted
- `io2`: high IOPS
- `efs`: shared file storage
- `local`: local NVMe (high perf)
- `glacier-backup`: archive (uncommon)

App picks via PVC.

## Patterns

### Per-Tier
- `tier-0`: io2 + multi-AZ replication
- `tier-1`: gp3 high IOPS + backup
- `tier-2`: gp3 standard

### Multi-Region (DR)
For cross-region: snapshots replicated; cluster-specific PVs in each region.

## Topology

CSI reports topology:
```yaml
allowedTopologies:
- matchLabelExpressions:
  - key: topology.ebs.csi.aws.com/zone
    values: [us-east-1a, us-east-1b]
```

Restrict where PVs created.

## Snapshots

VolumeSnapshotClass for snapshots:
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snap-class
driver: ebs.csi.aws.com
deletionPolicy: Retain
```

VolumeSnapshot uses this class.

## Local Storage

For node-local SSDs:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

PV per local disk; manual provisioning.

For: high-perf DBs (Cassandra on local SSD).

Cons: data tied to node; pod can only run there.

## TopoLVM

LVM-based local storage. Auto-provisioning of logical volumes per PVC. Better than static local PVs.

## Cost

Cloud storage:
- EBS gp3: $0.08/GB/mo
- EBS io2: $0.125/GB/mo + IOPS
- EFS: $0.30/GB/mo (standard)

For 100 GB on gp3: $8/mo.

For high-perf: io2 + provisioned IOPS = $$.

## CSI Driver Installation

```bash
# AWS EBS
eksctl create iamserviceaccount --name ebs-csi-controller-sa --namespace kube-system --cluster mycluster --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy --approve

helm install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver -n kube-system --set controller.serviceAccount.create=false --set controller.serviceAccount.name=ebs-csi-controller-sa
```

Plus node-level DaemonSet.

## EFS Specifics

EFS in K8s:
- Pre-create EFS filesystem
- Configure mount targets per AZ
- EFS CSI driver
- StorageClass with file system ID

```yaml
parameters:
  provisioningMode: efs-ap
  fileSystemId: fs-xxxxx
  directoryPerms: "700"
```

Each PVC gets EFS Access Point under fs.

## Volume Mode

- Filesystem (default): block formatted; mounted as FS
- Block: raw block; pod handles

For DBs: usually Filesystem (ext4, xfs).
For specialty: Block.

## Common Mistakes

- No default SC (PVCs Pending forever)
- Immediate binding mode for zonal (wrong AZ)
- Delete reclaim for prod data
- No expansion enabled
- Same SC for all tiers (no flexibility)

## Best Practices

- Default SC set
- WaitForFirstConsumer for zonal
- Retain for important data
- Expansion enabled
- Multiple SCs for tiers
- Encryption default (cloud KMS)
- Topology constraints

## Operations

```bash
# List SCs
kubectl get sc

# Describe
kubectl describe sc gp3

# Make default
kubectl annotate sc gp3 storageclass.kubernetes.io/is-default-class="true"

# Unmark default
kubectl annotate sc gp3 storageclass.kubernetes.io/is-default-class-

# Delete
kubectl delete sc gp3
```

## Migration

Move from one SC to another:
1. Create new PVC with new SC
2. Copy data (snapshot + restore, or sync)
3. Update pod / StatefulSet
4. Delete old PVC

Or use `pv-migrate` tool.

## Anti-Patterns

- Hardcoded fs-IDs in pods (use SC abstraction)
- Same SC for prod + dev (different SLAs)
- No backup strategy
- Locked to one cloud's SC

## Multi-Cloud

For portability:
- Use abstract names (`fast`, `shared`)
- Per-cloud SC definitions
- Helm values per env

## Quick Refs

```yaml
# Standard SC
kind: StorageClass
metadata: {name: gp3}
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

# Use
kind: PersistentVolumeClaim
spec:
  storageClassName: gp3
  accessModes: [ReadWriteOnce]
  resources: {requests: {storage: 50Gi}}
```

## Interview Prep

**Mid**: "StorageClass purpose."

**Senior**: "Dynamic vs static provisioning."

**Staff**: "Storage strategy for stateful platform."

## Next Topic

→ [T03 — CSI (Container Storage Interface)](T03-CSI.md)
