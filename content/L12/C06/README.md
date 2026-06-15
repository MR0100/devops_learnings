# L12/C06 — Storage in Containers

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Volumes.md) | Volumes vs Bind Mounts vs tmpfs | 1 hr |
| [T02](T02-Volume-Drivers.md) | Volume Drivers | 0.5 hr |

## Three Mount Types

### 1. Volume (Docker-managed)
```bash
docker volume create mydata
docker run -v mydata:/var/lib/mysql mysql
# Or:
docker run --mount type=volume,src=mydata,dst=/var/lib/mysql mysql
```

Stored under `/var/lib/docker/volumes/` (or in a driver-backed location).

Pros:
- Docker manages lifecycle
- Backup/restore via Docker
- Cross-platform (Linux/Mac/Win)
- Performant
- Volume drivers for cloud / NFS

### 2. Bind Mount
```bash
docker run -v /host/path:/container/path nginx
docker run -v "$PWD":/app -w /app node:20 npm test
```

A host path mounted into container.

Pros:
- Easy local dev (live-reload from host)
- See/modify files outside container

Cons:
- Tied to host filesystem
- Permission issues across UIDs

### 3. tmpfs
```bash
docker run --tmpfs /tmp nginx
docker run --mount type=tmpfs,destination=/tmp,tmpfs-size=100m nginx
```

In-memory; gone on container stop.

Use: scratch data, secrets that shouldn't hit disk.

## Volume Drivers

Volumes can use drivers to back storage:

- **local** (default): on host disk
- **NFS**: shared NFS export
- **AWS EFS**: via Docker plugin or volume mount
- **Cloud-specific**: GCE PD, Azure File via plugins
- **Cluster storage**: Portworx, Ceph RBD

```bash
docker volume create --driver local \
  -o type=nfs \
  -o o=addr=10.0.0.1,rw \
  -o device=:/exports/data \
  shared-data
```

### Plugin Architecture
Docker volume plugins implement `/Plugin.Activate`, `/VolumeDriver.Create`, `/VolumeDriver.Mount`, etc.

## Best Practices

### Use Volumes for State
For databases, message queues, caches that need to survive container restarts.

### Use Bind Mounts for Dev
Live-reload code from host into container.

### Avoid Writing to Container Filesystem
Writes go to overlay's upper layer; slower than volumes; lost on `docker rm`. Either:
- Mount a volume for data
- Or write to `/tmp` with `--tmpfs`

### Volume Permissions

Common pain: host UID 1000, container UID 1000 — but they're not the SAME user/group in different system contexts.

Mitigations:
- `--user $(id -u):$(id -g)` to match host UID
- Idempotent init script that chowns the volume mount at startup
- Use named volumes (Docker-managed) which avoid host UID problems

## Backup Strategy

```bash
# Backup volume
docker run --rm -v mydata:/source -v $(pwd):/backup alpine \
  tar czf /backup/mydata-backup.tar.gz -C /source .

# Restore
docker run --rm -v mydata:/dest -v $(pwd):/backup alpine \
  tar xzf /backup/mydata-backup.tar.gz -C /dest
```

## Performance

| Type | Linux native | Mac (via VM) |
|---|---|---|
| Volume (Docker-managed) | Fast | Fast |
| Bind mount | Fast | Slow! (especially many small files) |
| tmpfs | Fastest (RAM) | Fastest |

Mac/Windows Docker uses a Linux VM; bind mounts use file sharing protocols. Use:
- `:cached` / `:delegated` flags for Mac to relax consistency
- Or use named volumes for data, bind only for code

## K8s Equivalents

| Docker | K8s |
|---|---|
| Volume | PersistentVolume (PV) + PersistentVolumeClaim (PVC) |
| Bind mount | hostPath (avoid) |
| tmpfs | emptyDir with `medium: Memory` |
| (none direct) | ConfigMap/Secret mount |

K8s storage abstraction is richer; CSI plugins handle cloud volumes.

## Interview Themes

- "Compare volumes and bind mounts"
- "How would you back up a Docker volume?"
- "Mac is slow at bind mounts — why?"
- "When tmpfs?"
- "Docker → K8s storage mapping"
