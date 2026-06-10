# L12/C01/T04 — Union Filesystems (overlayfs)

## Learning Objectives

- Understand layer storage
- Apply overlayfs

## Layered Storage

Container image = stack of read-only layers.
Container = layers + thin writable layer on top.

```
┌─────────────────────────┐
│ Container layer (R/W)    │
├─────────────────────────┤
│ Layer N (read-only)      │
├─────────────────────────┤
│ Layer N-1                │
├─────────────────────────┤
│ Base layer               │
└─────────────────────────┘
```

Union filesystem merges into single view.

## overlayfs

Modern Linux union FS. Used by Docker / containerd.

Components:
- **lowerdir**: read-only layers (image)
- **upperdir**: writable layer (container)
- **workdir**: scratch (internal)
- **merged**: presented to container

```bash
mount -t overlay overlay \
  -o lowerdir=/lower1:/lower2:/lower3,upperdir=/upper,workdir=/work \
  /merged
```

## How Docker Uses

For each container:
- Image layers in lowerdir
- New writable layer in upperdir
- Container sees merged

Multiple containers can share lowerdir (image layers) → space-efficient.

## Storage Location

```bash
/var/lib/docker/overlay2/
├── <image_layer_1>/
├── <image_layer_2>/
└── <container_layer>/
    ├── upper/   # writable
    ├── work/    # internal
    └── merged/  # mounted into container
```

## CoW (Copy-on-Write)

Read: from any layer.
Write to existing file: copy to upper; modify there.

For: image layers immutable; per-container changes isolated.

## Layer Sharing

```bash
docker pull nginx
docker pull node
# Both share same base image layers (if same)
```

```bash
docker images
# Shows layers; same digest = same layer
```

For: space savings.

## Image Layers

Built per Dockerfile instruction:
```dockerfile
FROM ubuntu              # layer 1
RUN apt update           # layer 2
RUN apt install nginx    # layer 3
COPY . /app              # layer 4
CMD ["nginx"]            # config; not a layer
```

Each: separate layer.

## Layer Caching

Build:
- Per instruction: check if layer exists
- If yes: reuse (cache hit)
- If no: build + save

For: fast rebuilds.

```bash
docker build -t myapp .
# Pulls cached layers; only builds changed
```

## Layer Order Matters

```dockerfile
# BAD
COPY . /app
RUN npm install   # invalidates cache on any file change

# GOOD
COPY package.json /app/
RUN npm install   # cached if package.json unchanged
COPY . /app
```

Cache invalidates from changed layer down.

## Image Inspect

```bash
docker history nginx
# Shows layers + sizes

docker inspect nginx | jq .RootFS
# Layer digests
```

## Container Writable Layer

```bash
docker run -d --name web nginx
# Container started

docker exec web touch /tmp/myfile
# Writes to upper layer

docker diff web
# Shows changes from image
```

When container deleted: writable layer gone.

For persistence: volumes (covered C06).

## Storage Drivers

Docker storage drivers:
- overlay2 (default modern; recommended)
- devicemapper (legacy)
- btrfs (advanced)
- zfs (advanced)
- vfs (slow; fallback)
- aufs (older)

For Linux: overlay2.
For Mac/Windows: VM-based.

## Check Driver

```bash
docker info | grep "Storage Driver"
# Storage Driver: overlay2
```

## overlayfs Limits

- Max ~128 layers (configurable but slow)
- Inode count
- No layer modification (only add)

For: most images <30 layers.

## Inspect Layers

```bash
# List image layers
docker history nginx --no-trunc

# Layer paths
docker inspect nginx | jq '.[].GraphDriver.Data'
```

## Container Layer Size

```bash
docker ps -s
# Shows SIZE: <container layer> (virtual <total>)
```

`SIZE`: writable layer only.
Virtual: + image size (counted once).

## Multi-Container Same Image

```bash
docker run -d --name web1 nginx
docker run -d --name web2 nginx
docker run -d --name web3 nginx
```

All share nginx image layers.
Each: own writable layer.

For: minimal disk.

## Prune

Old containers + images accumulate:
```bash
docker system prune     # remove stopped containers, unused images
docker system prune -a  # all unused images
docker volume prune     # volumes
```

For: free disk.

## Layer Deduplication

Same content hash = single physical layer.

For: storage efficiency at scale.

## Performance

overlayfs:
- Read: fast (passthrough)
- Write to new file: fast
- Write to existing: copy-up (slow first time)
- Delete: whiteout (delete in upper)

For: most workloads fine. Heavy write to large files: consider volumes.

## Volumes Bypass Layers

Volume mounted: not in layer system. Direct disk access.

For: databases, write-heavy apps.

## Build Cache

```bash
docker build --cache-from myapp:latest -t myapp:new .
```

For CI: reuse layers from previous build.

## BuildKit Cache

Modern; better cache:
```bash
DOCKER_BUILDKIT=1 docker build .
```

Or:
```dockerfile
# syntax=docker/dockerfile:1.4
RUN --mount=type=cache,target=/root/.cache/go-build go build
```

Persistent cache between builds.

## Container Filesystem View

In container:
```
/        ← merged view of all layers + upperdir
```

Looks normal. Layered underneath.

## Modify Image Layer? No

Can't. Image layers immutable.

For changes:
- Edit Dockerfile
- Rebuild
- New layer

## Squash

Optional: combine layers:
```bash
docker build --squash -t myapp .
```

Reduces layer count; loses sharing benefit.

For: small images; not common.

## Best Practices

- Use overlay2
- Order Dockerfile (cache-friendly)
- COPY package files before code
- Use volumes for write-heavy
- Prune regularly
- Multi-stage builds (cleaner layers)

## Common Mistakes

- Many layers (slow)
- Inefficient order (cache miss)
- Writing to layered FS heavily (slow)
- Forgot prune (disk full)
- Modifying image inline (no persistence)

## Alternatives

- AUFS: older; replaced
- devicemapper: legacy
- ZFS / Btrfs: feature-rich but complex
- overlayfs2: default; recommended

## Disk Usage

```bash
docker system df
# Shows image, container, volume disk use

docker system df -v
# Detailed
```

## Inspecting Layers

```bash
# Image
docker history IMAGE --no-trunc

# Specific layer
docker save IMAGE | tar -tv | head

# Container
docker diff CONTAINER
# A: added, C: changed, D: deleted
```

## Quick Refs

```bash
docker history IMAGE
docker inspect IMAGE
docker diff CONTAINER
docker system df
docker system prune
ls /var/lib/docker/overlay2/
mount | grep overlay
```

## Interview Prep

**Junior**: "What are image layers."

**Mid**: "overlayfs purpose."

**Senior**: "Layer caching in build."

**Staff**: "Storage strategy for high-density nodes."

## Next Topic

→ [T05 — Capabilities & Seccomp](T05-Capabilities-Seccomp.md)
