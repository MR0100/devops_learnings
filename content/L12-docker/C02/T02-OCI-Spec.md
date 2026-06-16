# L12/C02/T02 — OCI Image & Runtime Spec

## Learning Objectives

- Understand OCI standards
- Inspect images at low level

## OCI

Open Container Initiative. Standards for:
- Image format
- Runtime spec
- Distribution (registry)

For: Docker, Podman, containerd, K8s, etc. interoperate.

## OCI Image Spec

Image = ordered set of layers + config.

```
image/
├── manifest.json (per arch)
├── config.json (image metadata)
└── layers/
    ├── sha256:abc.tar.gz
    ├── sha256:def.tar.gz
    └── ...
```

## Manifest

```json
{
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:abc...",
    "size": 1234
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:def...",
      "size": 56789
    }
  ]
}
```

References config + layers by digest.

## Config

```json
{
  "architecture": "amd64",
  "os": "linux",
  "config": {
    "Cmd": ["/bin/sh"],
    "Env": ["PATH=..."],
    "WorkingDir": "/app",
    "Entrypoint": ["./entrypoint.sh"],
    "ExposedPorts": {"80/tcp": {}}
  },
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:layer1...",
      "sha256:layer2..."
    ]
  },
  "history": [...]
}
```

Defines: how to run + filesystem composition.

## Layers

Each: tarball of filesystem changes.

```bash
# Inspect
docker save nginx -o nginx.tar
tar -xf nginx.tar
# layer/layer.tar
tar -tf layer.tar | head
# usr/share/nginx/html/...
```

Stacked: each layer adds/modifies/removes files.

## Digests

SHA256 hash of content.

For: content-addressable storage. Same content = same digest.

```bash
docker inspect nginx --format '{{.Id}}'
# sha256:abc...

docker images --digests
# Shows digest
```

## Multi-Arch Images (Manifest List)

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    {
      "digest": "sha256:amd64...",
      "platform": {"architecture": "amd64", "os": "linux"}
    },
    {
      "digest": "sha256:arm64...",
      "platform": {"architecture": "arm64", "os": "linux"}
    }
  ]
}
```

One tag; many architectures.

Runtime picks correct.

## OCI Runtime Spec

How to launch container:
```json
{
  "ociVersion": "1.0.0",
  "process": {
    "args": ["/bin/sh"],
    "env": ["PATH=..."],
    "user": {"uid": 0, "gid": 0},
    "capabilities": {...}
  },
  "root": {
    "path": "/path/to/rootfs"
  },
  "mounts": [...],
  "linux": {
    "namespaces": [
      {"type": "pid"},
      {"type": "network"},
      ...
    ],
    "resources": {
      "memory": {"limit": 268435456},
      "cpu": {"cpus": "0-3"}
    },
    "seccomp": {...},
    "capabilities": {...}
  }
}
```

runc reads this; sets up container.

## Generate Spec

```bash
runc spec
# Creates config.json template
```

Modify; run:
```bash
runc run mycontainer
```

For: low-level container creation.

## Distribution Spec

OCI registry API:
- `GET /v2/<name>/manifests/<reference>`
- `GET /v2/<name>/blobs/<digest>`
- `PUT /v2/<name>/manifests/<reference>`
- ...

Used by registries (Docker Hub, ECR, etc.).

For: standard pull/push behavior.

## crane

Tool for OCI images:
```bash
brew install crane

crane manifest nginx
crane config nginx
crane ls nginx
crane copy src:tag dst:tag
```

For: image manipulation without Docker daemon.

## skopeo

Similar; image copy without daemon:
```bash
skopeo copy docker://nginx:latest docker://myregistry/nginx:latest
```

For: moving between registries.

## OCI Artifacts

Beyond images:
- Helm charts in OCI
- WASM modules in OCI
- Container Volumes
- SBOMs

OCI registry = generic artifact store.

```bash
oras push registry/repo:tag file.bin
oras pull registry/repo:tag
```

## OCI Image Layout

Local directory:
```
oci-layout/
├── oci-layout
├── index.json
└── blobs/
    └── sha256/
        ├── <digest>
        └── ...
```

Standard format; portable.

## Building OCI Images

Tools:
- docker build
- BuildKit
- Buildah
- Kaniko (in K8s)
- Bazel rules_docker
- Nix dockerTools

All produce OCI-compliant.

## Inspect Image

```bash
# Docker
docker inspect IMAGE
docker history IMAGE

# crane
crane manifest IMAGE
crane config IMAGE

# skopeo
skopeo inspect docker://IMAGE
```

## Image Layers vs Distribution Layers

Same content; different format:
- Image: filesystem changes
- Distribution: tarball

Hash differs; same content semantically.

## Reproducible Builds

Same source → same image (digest).

Requires:
- Pinned versions
- No timestamps
- Sorted file lists
- Deterministic compression

For: SLSA compliance.

## SBOM in OCI

Attach SBOM:
```bash
syft myimage -o spdx-json > sbom.json
cosign attach sbom --sbom sbom.json myimage
```

For: supply chain.

## Signatures in OCI

```bash
cosign sign myimage
cosign verify --certificate-identity-regexp '.*' myimage
```

Sigstore-based.

## Provenance

Build attestations attached to image:
- Builder identity
- Source repo / commit
- Materials

For: SLSA L3.

## Compression

Default: gzip (per layer).
Alternative: zstd (faster decompression).

```dockerfile
# syntax=docker/dockerfile:1.5
# uses zstd if BuildKit supports
```

For: faster pull on container start.

## Multi-Arch Build

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t myimage --push .
```

Produces manifest list.

## Image Inspection Workflow

```bash
# What's in image?
docker image inspect IMAGE
docker history IMAGE --no-trunc

# Run + explore
docker run -it IMAGE sh
ls /
env

# Or dive (TUI for image inspection)
dive IMAGE
```

## ENTRYPOINT vs CMD (Image Config)

```json
"Entrypoint": ["./main"],
"Cmd": ["--port", "8080"]
```

Container runs: `./main --port 8080`.

CMD: default args; overridable.
ENTRYPOINT: command; not overridable.

## Image Optimization

Smaller is better:
- Multi-stage build
- Distroless base
- Squash unnecessary layers (rare; sharing benefit)
- Compression

Covered C04.

## OCI Compliance

Test:
```bash
crane validate IMAGE
```

For: ensure standard compliance.

## Common Mistakes

- Hardcoded :latest (mutable)
- No digest pinning (drift)
- Big images (slow start)
- No multi-arch (limits deployment)
- No SBOM / signing (supply chain)

## Best Practices

- Pin to digest in prod (`@sha256:...`)
- Multi-arch (amd64 + arm64)
- Sign with cosign
- Attach SBOM
- Small base images
- Provenance attestations

## Pull by Digest

```yaml
image: nginx@sha256:abc...
```

Immutable. Even if tag re-pushed; this digest stays same.

For supply chain critical.

## Quick Refs

```bash
# Inspect
docker inspect IMAGE
docker history IMAGE
crane manifest IMAGE
skopeo inspect docker://IMAGE
dive IMAGE

# Copy
crane copy src dst
skopeo copy src dst

# Multi-arch build
docker buildx build --platform linux/amd64,linux/arm64 ...

# Sign / SBOM
cosign sign IMAGE
syft IMAGE > sbom.json
```

## Interview Prep

**Mid**: "OCI image format."

**Senior**: "Multi-arch manifest list."

**Staff**: "Supply chain with OCI."

## Next Topic

→ [T03 — Docker vs Podman vs nerdctl](T03-Docker-Podman-Nerdctl.md)
