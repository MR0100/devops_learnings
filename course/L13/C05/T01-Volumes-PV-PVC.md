# L13/C05/T01 — Volumes, PersistentVolumes, PersistentVolumeClaims

## Learning Objectives

- Use volumes correctly
- Understand PV / PVC

## Volumes

Per-pod storage. Many types:

### emptyDir
Ephemeral; pod lifetime:
```yaml
volumes:
- name: cache
  emptyDir: {}
```

For scratch space. Deleted on pod removal.

### hostPath
Mount node directory:
```yaml
volumes:
- name: logs
  hostPath:
    path: /var/log
```

Tight coupling. For: DaemonSets reading host files.

### configMap / secret
Mount K8s objects:
```yaml
volumes:
- name: config
  configMap:
    name: app-config
```

### downwardAPI
Pod metadata as files (covered earlier).

### persistentVolumeClaim
Reference PVC; abstracted persistent storage.

## PersistentVolume (PV)

Cluster-wide resource. Represents storage:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: gp3
  awsElasticBlockStore:
    volumeID: vol-xxxxx
    fsType: ext4
```

Or via CSI:
```yaml
spec:
  csi:
    driver: ebs.csi.aws.com
    volumeHandle: vol-xxxxx
```

## PersistentVolumeClaim (PVC)

User request for storage:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: gp3
```

K8s binds PVC to suitable PV.

## Pod Uses PVC

```yaml
volumes:
- name: data
  persistentVolumeClaim:
    claimName: my-pvc

containers:
- name: app
  volumeMounts:
  - name: data
    mountPath: /data
```

## Access Modes

- **ReadWriteOnce (RWO)**: single node R/W (typical for block)
- **ReadOnlyMany (ROX)**: many nodes read-only
- **ReadWriteMany (RWX)**: many nodes R/W (EFS, NFS, CephFS)
- **ReadWriteOncePod (RWOP)**: single pod R/W (newer; stricter)

Most block volumes: RWO.
For shared: RWX (file storage).

## Static Provisioning

Admin creates PV manually:
```yaml
# PV: EBS volume vol-xxx
kind: PersistentVolume
spec:
  capacity: {storage: 100Gi}
  awsElasticBlockStore:
    volumeID: vol-xxx
```

PVC requests; binds to existing PV.

For: pre-existing storage.

## Dynamic Provisioning

StorageClass triggers automatic PV creation:
```yaml
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
```

PVC references:
```yaml
spec:
  storageClassName: gp3
```

CSI driver creates EBS, makes PV, binds.

Most common modern.

## ReclaimPolicy

What happens when PVC deleted:
- **Retain**: PV stays; data preserved; manual cleanup
- **Delete**: PV + underlying storage deleted
- **Recycle**: deprecated; rm -rf

Per PV (default for dynamic: based on StorageClass).

For production data: Retain.

## StorageClass

Defines class of storage:
```yaml
kind: StorageClass
metadata:
  name: gp3-encrypted
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
  kmsKeyId: alias/myKey
  iops: "5000"
  throughput: "250"
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

PVC references by name.

## VolumeBindingMode

- **Immediate**: bind PVC ASAP (may pick wrong AZ before pod scheduled)
- **WaitForFirstConsumer**: bind when pod scheduled (correct AZ)

For EBS (zonal): WaitForFirstConsumer mandatory.

## Volume Expansion

```yaml
allowVolumeExpansion: true   # in StorageClass
```

Then:
```bash
kubectl patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'
```

PVC updated; underlying volume grown; FS extended.

For: scaling DBs without restart.

## Volume Types (CSI)

Cloud-managed CSI drivers:
- AWS EBS CSI
- AWS EFS CSI (RWX)
- GCP PD CSI
- Azure Disk / Files CSI
- Ceph CSI
- NFS CSI
- Hostpath CSI (dev only)

## Lifecycle

```
1. User creates PVC
2. PV controller finds / creates PV
3. PVC binds to PV (Bound phase)
4. Pod uses PVC
5. CSI attaches volume to node (if not attached)
6. kubelet mounts to pod
7. Pod uses
8. Pod deleted → kubelet unmounts; CSI detaches
9. PVC deleted → reclaimPolicy applies
```

## Phases

PV phases:
- Available
- Bound (to PVC)
- Released (PVC deleted; reclaim pending)
- Failed

PVC phases:
- Pending
- Bound
- Lost

## EmptyDir Variants

```yaml
emptyDir:
  medium: Memory   # tmpfs in RAM
  sizeLimit: 1Gi
```

Memory-backed: fast. For caches.

## Block vs Filesystem

```yaml
spec:
  volumeMode: Block   # raw block; pod handles formatting
  # vs
  volumeMode: Filesystem   # default; FS mounted
```

Block: for DBs wanting raw devices.

## Topology

CSI plugins report topology (which nodes can attach):
- EBS: AZ-bound
- EFS: any AZ in region
- Local: specific node

Scheduler considers when WaitForFirstConsumer.

## Common Scenarios

### Stateful Workload
StatefulSet + volumeClaimTemplates:
```yaml
volumeClaimTemplates:
- metadata: {name: data}
  spec:
    accessModes: [ReadWriteOnce]
    storageClassName: gp3
    resources: {requests: {storage: 50Gi}}
```

Each pod gets own PVC.

### Shared State
RWX (EFS):
```yaml
accessModes: [ReadWriteMany]
storageClassName: efs-sc
```

Multiple pods mount same volume.

### Database
- RWO block volume (gp3, io2)
- Per-pod (StatefulSet)
- Backups via snapshots

## Snapshots

VolumeSnapshot (CSI):
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: snap-2024-06-09
spec:
  source:
    persistentVolumeClaimName: my-pvc
  volumeSnapshotClassName: csi-snap-class
```

For: backups, cloning.

Restore: create PVC from snapshot.

## Backup Strategy

Velero:
- Backup K8s resources + PV data
- Restore to same / different cluster
- Schedule
- Multiple storage backends (S3)

For: DR.

## Cost

Cloud storage:
- EBS gp3: $0.08/GB/mo
- EFS: $0.30/GB/mo

For 100 GB DB: $8/mo on EBS. Cheap.

## Common Mistakes

- RWO trying to mount across nodes
- ReclaimPolicy Delete (data lost on PVC removal)
- Single-AZ PV for multi-AZ pods
- No backups
- Hostpath (tight coupling)

## Best Practices

- Dynamic provisioning (StorageClass)
- WaitForFirstConsumer
- Retain policy for important data
- Snapshots scheduled
- Backups tested
- Right access mode
- Volume expansion enabled

## Operations

```bash
# List
kubectl get pv
kubectl get pvc
kubectl get sc

# Describe
kubectl describe pvc my-pvc
kubectl describe pv pv-xxx

# Expand
kubectl patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'

# Snapshot
kubectl apply -f snapshot.yaml
```

## When NOT PVC

- Stateless (use emptyDir or no volume)
- Cache only (emptyDir Memory)
- Config (configMap)

## CSI Drivers

For installing:
```bash
# AWS EBS
helm install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver

# AWS EFS
helm install aws-efs-csi-driver aws-efs-csi-driver/aws-efs-csi-driver
```

Plus IAM permissions for driver pod.

## Quick Refs

```yaml
# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: data}
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: gp3
  resources: {requests: {storage: 50Gi}}

# Use in pod
volumes:
- name: data
  persistentVolumeClaim: {claimName: data}
```

## Interview Prep

**Junior**: "PV vs PVC."

**Mid**: "Dynamic provisioning."

**Senior**: "WaitForFirstConsumer reason."

**Staff**: "Stateful storage for multi-region cluster."

## Next Topic

→ [T02 — StorageClasses & Dynamic Provisioning](T02-StorageClasses.md)
