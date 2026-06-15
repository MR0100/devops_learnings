# L12/C06/T02 — Volume Drivers

## Learning Objectives

- Use volume drivers
- Pick for use case

## Volume Drivers

Plugins providing storage:
- local (default)
- nfs
- ceph
- glusterfs
- aws-ebs (community)
- azure-file
- gcp-pd

For: networked, cloud, advanced storage.

## Local Driver

Default; on host:
```bash
docker volume create -d local mydata
```

Located at `/var/lib/docker/volumes/`.

For: single-host workloads.

## NFS Driver

```bash
docker volume create -d local \
  --opt type=nfs \
  --opt o=addr=nfs-server.com,rw \
  --opt device=:/exports/data \
  nfsvol

docker run -v nfsvol:/data alpine
```

For: shared across hosts.

## Compose with NFS

```yaml
volumes:
  nfsvol:
    driver_opts:
      type: "nfs"
      o: "addr=nfs.example.com,rw,nfsvers=4"
      device: ":/exports/data"
```

## Cloud Drivers

### AWS EBS
```bash
docker plugin install rexray/ebs
docker volume create -d rexray/ebs --opt size=20 myvol
```

Auto-creates EBS; mounts.

### Azure File
Plugin similar.

### Google PD
Plugin similar.

For: container persistence on cloud VMs.

## Ceph / GlusterFS

For: enterprise distributed storage.

```bash
docker plugin install ceph/cephfs-volume-plugin
docker volume create -d cephfs/v1 mydata
```

For: K8s-like clusters; replicated storage.

## docker-volume-netshare

Plugin for NFS, CIFS, etc.

```bash
docker plugin install ContainX/docker-volume-netshare
docker volume create -d nfs --opt share=server/path mydata
```

For: multi-protocol.

## K8s Equivalent

K8s doesn't use Docker volume drivers. Uses CSI:
- EBS CSI
- GCE PD CSI
- Azure Disk CSI
- Ceph CSI
- NFS CSI

Same concepts; K8s-native.

Covered in L13/C05.

## Backup Drivers

Some drivers support snapshots:
- EBS: AWS snapshots
- Ceph: native

For: data protection.

## Plugin Install

```bash
docker plugin install <plugin>
docker plugin ls
docker plugin disable <plugin>
docker plugin enable <plugin>
docker plugin rm <plugin>
```

## Custom Plugin

Write your own:
- Implements Docker Volume Plugin protocol
- HTTP API
- Hooks: Create, Mount, Unmount, Remove, etc.

For: specialty storage.

## When NOT Drivers

For most:
- Local driver
- Bind mounts
- tmpfs

Drivers add complexity. Use only when needed.

## Sharing Across Hosts

For multi-host:
- NFS (networked)
- Cloud-managed (EFS, FileStore, Azure Files)
- Storage cluster (Ceph)

Single-host: local driver fine.

## EFS Example

For AWS:
```bash
# Mount EFS on host
sudo mount -t nfs4 fs-xxx.efs.us-east-1.amazonaws.com:/ /mnt/efs

# Use as bind
docker run -v /mnt/efs/myapp:/data alpine
```

Simpler than EFS Docker driver.

## ECS

ECS Fargate uses task volumes:
- Volume types: efs, fsxWindowsFileServer, etc.
- Managed by AWS

For: production AWS containers.

## Best Practices

- Local driver for most
- NFS for sharing
- Cloud-managed for cloud (EFS direct mount)
- K8s + CSI for orchestrated
- Test driver in staging

## Common Mistakes

- Wrong driver for use case
- Forgot dependencies (NFS server running?)
- Plugin not installed on all hosts
- Permission issues (UID across hosts)

## Plugin Management

For multi-host: plugin on every host.

For: consistent storage.

## Storage Performance

| Type | IOPS | Latency |
|---|---|---|
| Local SSD | High | Low |
| Local HDD | Low | Higher |
| NFS | Medium | Network |
| EBS gp3 | 3000-16000 | Sub-ms |
| EFS | Medium | Higher |

For DBs: local SSD or EBS.
For shared: EFS / NFS.

## Snapshots

For driver supporting:
```bash
docker volume snapshot mydata snap-2024-06-09
```

(varies by driver)

Or use cloud-native (EBS snapshot, etc.).

## Quotas

Some drivers support quotas:
```bash
docker volume create -d local --opt o=size=10g myvol
```

For: prevent runaway.

Not all drivers support.

## Health

```bash
docker volume inspect mydata
# Shows mount options + status
```

## Multi-Container Sharing

Same volume mounted in multiple containers:
```bash
docker run -d -v shared:/data --name writer alpine sh -c 'echo > /data/file'
docker run -d -v shared:/data --name reader alpine cat /data/file
```

Concurrent access: depends on app.

For DBs: usually not shared (corruption).

## Quick Refs

```bash
# Plugin
docker plugin install PLUGIN
docker plugin ls

# Volume with driver
docker volume create -d DRIVER --opt key=value NAME

# Use
docker run -v NAME:/path IMAGE
```

## Interview Prep

**Mid**: "When volume driver."

**Senior**: "Multi-host storage."

**Staff**: "Container storage architecture."

## Next Topic

→ Move to [L12/C07 — Docker Compose](../C07/README.md)
