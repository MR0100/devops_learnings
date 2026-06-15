# L13/C05 — Storage in Kubernetes

## Topics

- **T01 Volumes, PersistentVolumes, PersistentVolumeClaims** — Volume = on-pod, ephemeral. PV = cluster-wide resource (admin-provisioned or dynamic). PVC = user request matched to PV. AccessModes: ReadWriteOnce, ReadOnlyMany, ReadWriteMany, ReadWriteOncePod.
- **T02 StorageClasses & Dynamic Provisioning** — SC defines how to provision (driver, parameters). PVC references SC → PV created automatically. `reclaimPolicy: Delete | Retain`.
- **T03 CSI (Container Storage Interface)** — Plugin standard. EBS CSI, GCE PD CSI, Ceph RBD, Portworx, OpenEBS, Longhorn.
- **T04 Stateful Workloads & Data Gravity** — Where data lives constrains where compute runs. Multi-AZ pods need volume that crosses AZs (or replicas per AZ).
- **T05 Snapshots** — VolumeSnapshot, VolumeSnapshotContent, VolumeSnapshotClass. Cloud-native backups.

## Access Modes Reality Check

| Mode | Reality |
|---|---|
| RWO (ReadWriteOnce) | Single node mounts; standard for cloud block storage |
| ROX (ReadOnlyMany) | Multiple nodes read-only; rare |
| RWX (ReadWriteMany) | Multiple nodes RW; needs NFS, EFS, Ceph, GlusterFS |
| RWOP (ReadWriteOncePod) | Only ONE pod can mount RW (1.22+) |

## Common Pitfalls

- Cloud volumes (EBS, GCE PD) are RWO and AZ-scoped — a multi-AZ StatefulSet needs per-AZ topology
- Retain reclaim policy with deleted PVC orphans the underlying disk
- `volumeBindingMode: WaitForFirstConsumer` is essential for AZ-scoped storage with multi-AZ schedulers

## Interview Themes

- "How does dynamic provisioning work?"
- "Design persistent storage for a multi-AZ Postgres on K8s"
- "What's CSI and why does it exist?"
