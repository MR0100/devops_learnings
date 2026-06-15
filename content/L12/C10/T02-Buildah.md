# L12/C10/T02 — Buildah for Image Building

## Learning Objectives

- Build images without daemon
- Use Buildah scripting

## Buildah

Image building tool:
- No daemon
- Rootless
- Scriptable (not Dockerfile-only)
- Builds OCI images
- Companion to Podman

## Install

```bash
sudo dnf install -y buildah
sudo apt install -y buildah
```

## Build from Dockerfile

```bash
buildah bud -t myapp:v1 .
```

`bud` = build-using-dockerfile.

Same Dockerfile as Docker; no compatibility issues.

## Scripted Build

```bash
#!/bin/bash
ctr=$(buildah from alpine:3.20)
buildah run $ctr apk add --no-cache nginx
buildah copy $ctr config /etc/nginx
buildah config --entrypoint '["nginx"]' $ctr
buildah commit $ctr myapp:v1
buildah rm $ctr
```

Imperative; powerful.

For: Dockerfile-resistant builds (dynamic content, complex flows).

## From Scratch

```bash
ctr=$(buildah from scratch)
mnt=$(buildah mount $ctr)
# Build filesystem
cp -r rootfs/* $mnt/
buildah unmount $ctr
buildah commit $ctr base:latest
```

Build minimal image from nothing.

## Mount

```bash
mnt=$(buildah mount $ctr)
# $mnt = path to container's rootfs on host
# Modify directly
buildah unmount $ctr
```

For: file manipulations without rebuilding.

## Multi-Arch Build

```bash
buildah build --platform linux/amd64,linux/arm64 \
  -t myapp:v1 \
  --manifest myapp:v1 \
  .

buildah manifest push --all myapp:v1 docker://registry/myapp:v1
```

Builds for multiple arches; pushes manifest list.

## OCI vs Docker Format

```bash
buildah commit --format oci $ctr myapp
buildah commit --format docker $ctr myapp
```

Default: OCI.
For compatibility with old tools: docker.

## Layer Squashing

```bash
buildah commit --squash $ctr myapp
```

All layers merged into one. Smaller; less cacheable.

## Use Cases

### Custom Provisioning
```bash
ctr=$(buildah from ubi8)
buildah run $ctr -- /opt/installer.sh
buildah commit $ctr custom-image
```

Run arbitrary scripts; commit result.

### Dockerfile-less
For complex builds:
```bash
# Generate config dynamically
config=$(generate-config)
ctr=$(buildah from base)
echo "$config" | buildah run $ctr -- tee /etc/app.conf
buildah commit $ctr myapp
```

### Image Manipulation
```bash
ctr=$(buildah from existing-image)
buildah run $ctr -- patch-cve
buildah commit $ctr existing-image:patched
```

## Performance

- Faster than Docker (no daemon round-trips)
- Parallelizable
- Less memory

For CI: faster builds.

## Buildah in CI

```yaml
- name: Build
  run: |
    buildah bud -t myapp:${{ github.sha }} .
    buildah push myapp:${{ github.sha }}
```

In GitHub Actions: works rootless.

## Rootless

```bash
buildah bud -t myapp .
# Already rootless; no special setup
```

User namespace; no privileged container.

## Buildah vs docker build

| | docker build | buildah |
|---|---|---|
| Daemon | yes | no |
| Rootless | partial | default |
| Dockerfile | yes | yes (bud) |
| Scriptable | no | yes |
| OCI native | sort of | yes |

## Integration

```bash
# Build with buildah, push to registry
buildah bud -t REG/image:v1 .
buildah push REG/image:v1

# Run with Podman
podman run REG/image:v1
```

## Cache

```bash
buildah bud --layers -t myapp .
```

`--layers` enables layer caching (similar to Docker).

For repeated builds.

## Common Mistakes

- Not using --layers (slow rebuild)
- Forgetting to rm intermediate containers
- Mount manipulation while container is running

## Best Practices

- Buildah for daemonless CI
- Use bud unless scripting needed
- Multi-stage Dockerfiles (work as expected)
- Multi-arch with --manifest
- Combine with skopeo for push

## Quick Refs

```bash
# Dockerfile
buildah bud -t IMAGE .

# Scripted
ctr=$(buildah from BASE)
buildah run $ctr -- CMD
buildah commit $ctr IMAGE
buildah rm $ctr

# Push
buildah push IMAGE REGISTRY/IMAGE
```

## Interview Prep

**Mid**: "Buildah purpose."

**Senior**: "When scripted build."

**Staff**: "Buildah in CI architecture."

## Next Topic

→ [T03 — Kata Containers, gVisor (Sandboxed)](T03-Kata-gVisor.md)
