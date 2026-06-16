# L12/C06/T01 — Volumes vs Bind Mounts vs tmpfs

## Learning Objectives

- Pick storage type
- Apply per use case

## Three Types

| | Volume | Bind Mount | tmpfs |
|---|---|---|---|
| Managed by | Docker | You (host path) | Memory |
| Persistence | Yes | Yes | No (RAM) |
| Host access | /var/lib/docker/ | Anywhere | n/a |
| Portable | Yes | No (path-specific) | Yes |
| Performance | Native | Native | Fast (RAM) |

## Volumes

Docker-managed:
```bash
docker volume create mydata
docker run -v mydata:/data alpine
```

Or anonymous:
```bash
docker run -v /data alpine   # auto-named
```

Located at `/var/lib/docker/volumes/`.

Pros:
- Managed
- Portable
- Driver support
- Best practice

For: persistent app data.

## Bind Mount

Host directory:
```bash
docker run -v /host/path:/container/path alpine
```

Direct mount.

Pros:
- Real-time host file access
- Useful for dev (live edits)
- Existing data accessible

Cons:
- Path-specific
- Host filesystem layout matters
- Security (if container has access)

For: development, host configs.

## tmpfs

Memory-backed:
```bash
docker run --tmpfs /cache alpine
```

Or:
```bash
docker run --mount type=tmpfs,destination=/cache,tmpfs-size=100m alpine
```

Pros:
- Fast (RAM)
- No disk writes
- Ephemeral (security)

Cons:
- Volatile
- Limited by RAM

For: caches, secrets at runtime, scratch.

## --mount Syntax

Modern:
```bash
docker run --mount type=volume,source=mydata,destination=/data alpine
docker run --mount type=bind,source=/host/path,destination=/data alpine
docker run --mount type=tmpfs,destination=/cache,tmpfs-size=100m alpine
```

More explicit than `-v`.

## Compose

```yaml
services:
  app:
    volumes:
    - mydata:/data           # volume
    - ./code:/app            # bind
    - /tmp/cache:/cache      # bind
    tmpfs:
    - /run

volumes:
  mydata:
```

## Volume Drivers

```bash
docker volume create -d local mydata
docker volume create -d nfs --opt type=nfs --opt o=addr=server,rw --opt device=:/path nfsvol
```

Drivers: local (default), nfs, ceph, custom plugins.

For: cloud storage; networked.

## Volume Operations

```bash
# Create
docker volume create NAME

# List
docker volume ls

# Inspect
docker volume inspect NAME

# Remove
docker volume rm NAME

# Prune (unused)
docker volume prune
```

## Bind Mount Options

```bash
docker run -v /host:/container:ro alpine    # read-only
docker run -v /host:/container:rw alpine    # read-write (default)
docker run -v /host:/container:Z alpine     # SELinux
```

## Read-Only Root

```bash
docker run --read-only -v /tmp:/tmp alpine
```

Root FS read-only; specific writable mounts.

For: security.

## File Permissions

Host file owned by UID 1000.
Container running as UID 1000: can write.
Container as different UID: permission denied.

For: align UIDs or use `chown`.

## SELinux Context

For SELinux systems (RHEL):
```bash
docker run -v /host:/container:Z alpine
# :Z labels as private; :z shared
```

Without: SELinux blocks.

## Volume Backup

```bash
# Backup
docker run --rm -v mydata:/source -v $(pwd):/backup alpine \
  tar -czf /backup/mydata.tar.gz -C /source .

# Restore
docker run --rm -v mydata:/destination -v $(pwd):/backup alpine \
  tar -xzf /backup/mydata.tar.gz -C /destination
```

For: data preservation.

## Multi-Container Volume

```bash
docker volume create shared
docker run -d --name writer -v shared:/data alpine sh -c 'while true; do date >> /data/log; sleep 5; done'
docker run -d --name reader -v shared:/data alpine sh -c 'tail -f /data/log'
```

Both: same volume. Shared state.

## Volume Lifecycle

- Created explicitly: persists
- Anonymous: removed with container (-v) or not
- Removed: data lost

```bash
docker run --rm -v anonymous:/data alpine
# Anonymous volume orphaned
```

Use named for persistence.

## Bind Mount vs Volume

Bind: dev / specific paths.
Volume: production / portable.

For: stateless app + DB → DB uses volume.

## tmpfs Use Cases

```bash
docker run --tmpfs /tmp:size=100m,mode=1777 alpine
```

- Cache (Redis-style)
- Secrets at runtime (decrypt; write tmpfs)
- Build artifacts (CI)
- Reset on restart (security)

## Volume Plugins

For cloud:
- aws-ecs-volume-plugin
- gce-docker (GCP)
- rexray (multi-cloud)

For container persistent state across hosts.

In K8s: CSI drivers (covered L13/C05).

## Data Volume Container

Old pattern:
```bash
docker create -v /data --name datavol alpine
docker run --volumes-from datavol myapp
```

Modern: use named volumes directly.

## Anonymous vs Named

```bash
# Anonymous (auto-removed with --rm)
docker run --rm -v /data alpine

# Named (persists)
docker volume create mydata
docker run -v mydata:/data alpine
```

For prod: named.

## Inspect

```bash
# Volume location
docker volume inspect mydata
# /var/lib/docker/volumes/mydata/_data

# What's in it
sudo ls /var/lib/docker/volumes/mydata/_data
```

## Performance

Volumes on local disk: native speed.
Bind mounts on local disk: native speed.
tmpfs: faster (RAM).
NFS volume: network latency.

## Best Practices

- Volumes for persistent app data (DBs)
- Bind mounts for dev (live code edit)
- tmpfs for caches / secrets / scratch
- Named volumes (not anonymous)
- :ro when possible
- Backup volumes regularly

## Common Mistakes

- Anonymous volumes (lost data)
- Bind mount in prod (path-specific)
- No backup
- :rw when :ro suffices
- Volume in image layer (defeats purpose)

## Dev vs Prod

Dev:
```yaml
volumes:
- ./code:/app   # live edit
```

Prod:
```yaml
volumes:
- code-vol:/app   # immutable
```

## K8s Equivalents

K8s:
- Volume (ephemeral; pod lifetime)
- PersistentVolume / PVC (similar to Docker volume)
- emptyDir (similar to tmpfs)

Covered in L13/C05.

## Quick Refs

```bash
# Volume
docker volume create NAME
docker run -v NAME:/path IMAGE
docker volume inspect NAME
docker volume rm NAME

# Bind
docker run -v /host:/container IMAGE

# tmpfs
docker run --tmpfs /path IMAGE
docker run --mount type=tmpfs,destination=/path,tmpfs-size=100m IMAGE

# Inspect
docker inspect CONTAINER --format '{{.Mounts}}'
```

## Interview Prep

**Junior**: "Volume vs bind mount."

**Mid**: "Storage for DB container."

**Senior**: "Backup strategy."

**Staff**: "Persistent storage architecture."

## Next Topic

→ [T02 — Volume Drivers](T02-Volume-Drivers.md)
