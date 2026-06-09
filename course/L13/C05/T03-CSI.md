# L13/C05/T03 — CSI (Container Storage Interface)

## Learning Objectives

- Understand CSI architecture
- Reason about driver behavior

## CSI

Standard for plugging storage into orchestrators (K8s, Mesos, etc.).

Replaces in-tree volume plugins (deprecated; removed gradually).

## Architecture

Two main components per driver:

### Controller Plugin
- Runs as Deployment (typically 1-3 replicas)
- Creates / deletes / attaches volumes (calls cloud API)
- Snapshots
- Expansion

### Node Plugin
- DaemonSet (one per node)
- Mounts / unmounts on local node
- Stage / publish operations

## Operations

Controller:
- `CreateVolume`: provision volume in cloud
- `DeleteVolume`: delete
- `ControllerPublishVolume`: attach to node
- `ControllerUnpublishVolume`: detach
- `CreateSnapshot`, `DeleteSnapshot`
- `ControllerExpandVolume`: resize

Node:
- `NodeStageVolume`: prep on node (mount to global path)
- `NodeUnstageVolume`
- `NodePublishVolume`: bind-mount into pod
- `NodeUnpublishVolume`
- `NodeExpandVolume`: extend FS

## Lifecycle

For RWO block volume (EBS):
1. Pod scheduled with PVC
2. Scheduler picks node
3. CSI Controller: create EBS volume; attach to node
4. CSI Node: stage (mount to /var/lib/kubelet/plugins/...)
5. CSI Node: publish (bind-mount to /var/lib/kubelet/pods/<pod-uid>/...)
6. Container runs; sees volume at mountPath
7. Pod deleted: unpublish → unstage → detach → (depending on policy) delete

## Standard Drivers

- AWS EBS CSI
- AWS EFS CSI
- AWS FSx CSI
- GCP PD CSI
- Azure Disk / Files CSI
- Ceph CSI (rbd, cephfs)
- NFS CSI
- vSphere CSI
- Portworx
- Longhorn (Rancher)
- OpenEBS

## Install (AWS EBS Example)

```bash
# IAM role for service account
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster mycluster \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve

# Helm install
helm install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver \
  -n kube-system \
  --set controller.serviceAccount.create=false \
  --set controller.serviceAccount.name=ebs-csi-controller-sa
```

EKS add-on:
```bash
aws eks create-addon --cluster-name mycluster --addon-name aws-ebs-csi-driver
```

## CSI Driver Object

Cluster-scoped:
```yaml
apiVersion: storage.k8s.io/v1
kind: CSIDriver
metadata:
  name: ebs.csi.aws.com
spec:
  attachRequired: true
  podInfoOnMount: false
  fsGroupPolicy: File
```

Registered by driver install.

## CSI Node Object

Per-node:
```yaml
apiVersion: storage.k8s.io/v1
kind: CSINode
metadata:
  name: node-1
spec:
  drivers:
  - name: ebs.csi.aws.com
    nodeID: i-0abc123
    topologyKeys:
    - topology.ebs.csi.aws.com/zone
```

Reports driver capability per node.

## Topology

Driver reports node's topology (AZ, zone, region):
- Used by scheduler to pick correct zone for zonal volumes
- WaitForFirstConsumer needs this

## Volume Attributes

Custom attrs in PVC StorageClass.parameters → flow to driver.

## fsGroupPolicy

```yaml
fsGroupPolicy: File   # change ownership of mounted files
fsGroupPolicy: None
fsGroupPolicy: ReadWriteOnceWithFSType
```

Per security model.

For RWO: usually File (change perms for pod).

## Snapshots

CSI snapshots:
1. VolumeSnapshotClass references driver
2. VolumeSnapshot created
3. Driver calls CreateSnapshot
4. VolumeSnapshotContent generated

Restore:
- New PVC `dataSource: VolumeSnapshot/snap-x`
- New volume from snapshot

## Cloning

```yaml
spec:
  dataSource:
    kind: PersistentVolumeClaim
    name: source-pvc
  resources:
    requests:
      storage: 50Gi
```

Driver clones source.

For: spin up test DB from prod data.

## Generic Ephemeral Volumes

```yaml
spec:
  volumes:
  - name: scratch
    ephemeral:
      volumeClaimTemplate:
        spec:
          accessModes: [ReadWriteOnce]
          storageClassName: gp3
          resources: {requests: {storage: 10Gi}}
```

PVC created with pod; deleted with pod.

For: large scratch space (more than emptyDir).

## CSI Migration

In-tree → CSI:
- AWS EBS: migrated
- GCP PD: migrated
- Azure Disk: migrated

PVs still work; underneath uses CSI.

## Driver Issues

### Pod Stuck ContainerCreating
- Volume not attached
- Mount failing

```bash
kubectl describe pod <pod>
# Events show volume issue

kubectl logs -n kube-system <csi-controller-pod>
kubectl logs -n kube-system <csi-node-pod>
```

### Attach Failures
- Cloud API errors (quota, permissions)
- AZ mismatch
- Volume already attached elsewhere

### Performance
- Driver overhead
- Underlying storage perf

## Volume Reconciliation

Driver retries on transient errors. Some operations idempotent.

For stuck: manual cleanup may be needed (cloud console).

## Best Practices

- Use cloud-native CSI for cloud
- Multi-AZ aware
- Snapshots scheduled
- Backup tested
- Monitor driver
- Latest driver versions

## Common Mistakes

- Outdated CSI (missing features / bugs)
- No IAM for driver (operations fail)
- Volume Snapshot CRDs not installed
- Driver pod not running on all nodes

## Operations

```bash
# Driver status
kubectl get csidriver
kubectl get csinodes
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver

# Logs
kubectl logs -n kube-system <ebs-csi-controller>
kubectl logs -n kube-system <ebs-csi-node-xxx>

# Test
kubectl apply -f pvc.yaml
kubectl get pvc
kubectl get pv
```

## Multiple CSI Drivers

Multiple drivers per cluster:
- EBS for block
- EFS for shared file
- Local for performance

Each StorageClass picks one.

## CSI for Hybrid

CSI drivers for on-prem:
- Ceph
- vSphere
- NFS
- Portworx (managed)

For: K8s on bare metal / VMs.

## CSI Add-Ons

Tools:
- Velero: backup using CSI snapshots
- Stash: backup with CSI
- Kanister: snapshot orchestration

## Quick Refs

```bash
# Install (EBS)
aws eks create-addon --cluster-name mycluster --addon-name aws-ebs-csi-driver

# Verify
kubectl get csidriver
kubectl get pods -n kube-system | grep ebs

# Snapshot CRD check
kubectl get crd | grep snapshot

# Test
kubectl apply -f pvc.yaml
kubectl get pvc -w
```

## Interview Prep

**Mid**: "What is CSI."

**Senior**: "CSI driver architecture."

**Staff**: "CSI for multi-tier storage."

## Next Topic

→ [T04 — Stateful Workloads & Data Gravity](T04-Stateful-Data-Gravity.md)
