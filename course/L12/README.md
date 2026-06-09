# L12 — Docker & Container Internals

## Overview

Containers are the foundational unit of modern compute. This lecture goes from "I can run `docker run`" to "I understand exactly how containers work and could implement runc from scratch."

**10 chapters, 35 topics.**

## Chapter Map

### [C01](C01/) — Container First Principles
- T01 What a Container Actually Is
- T02 Namespaces (Recap from L02)
- T03 Cgroups (Recap from L02)
- T04 Union Filesystems (overlayfs)
- T05 Capabilities & Seccomp

### [C02](C02/) — Docker Architecture
- T01 dockerd, containerd, runc
- T02 OCI Image & Runtime Spec
- T03 Docker vs Podman vs nerdctl

### [C03](C03/) — Dockerfile Mastery
- T01 Base Images (distroless, alpine, scratch, ubi)
- T02 Layer Caching Strategy
- T03 Multi-Stage Builds
- T04 BuildKit & Build Secrets
- T05 ARG vs ENV
- T06 HEALTHCHECK, USER, ENTRYPOINT vs CMD

### [C04](C04/) — Image Optimization
- T01 Reducing Image Size
- T02 Reproducible Builds
- T03 SBOMs & Provenance

### [C05](C05/) — Container Networking
- T01 Bridge, Host, None, Overlay Networks
- T02 Port Mapping vs Host Networking
- T03 DNS Inside Docker

### [C06](C06/) — Storage in Containers
- T01 Volumes vs Bind Mounts vs tmpfs
- T02 Volume Drivers

### [C07](C07/) — Docker Compose
- T01 docker-compose.yml Anatomy
- T02 Networks, Volumes, Profiles
- T03 Compose for Local Dev

### [C08](C08/) — Container Security
- T01 Rootless Containers
- T02 Image Scanning (Trivy, Grype, Snyk)
- T03 Signed Images (Cosign, Notary v2)
- T04 Runtime Security (Falco, Tetragon)

### [C09](C09/) — Registries
- T01 Docker Hub, ECR, GCR, Artifact Registry, ACR, Harbor
- T02 Image Replication
- T03 Pull-Through Caches

### [C10](C10/) — Alternative Runtimes
- T01 Podman (Daemonless)
- T02 Buildah for Image Building
- T03 Kata Containers, gVisor (Sandboxed)
- T04 Firecracker microVMs

## The OCI Stack

```
docker CLI / nerdctl / podman
       │
       ▼
   containerd (or CRI-O)        ← high-level runtime
       │
       ▼
       runc (or crun, kata, gVisor)  ← low-level runtime
       │
       ▼
     kernel (namespaces, cgroups, capabilities)
```

## Production-Grade Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.6
FROM golang:1.22-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -ldflags='-s -w' -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /out/app /usr/local/bin/app
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/app"]
```

Key practices:
- Multi-stage to drop build deps
- BuildKit `--mount=type=cache` for dep caching
- Distroless for tiny, secure runtime
- Non-root user
- Explicit ENTRYPOINT (exec form)
- `.dockerignore` to exclude noise

## Image Size Examples

| Base | Size | Use |
|---|---|---|
| `scratch` | 0 B | Statically-linked Go |
| `gcr.io/distroless/static` | ~2 MB | Go, Rust |
| `alpine:3.20` | ~7 MB | When you need a shell |
| `debian:12-slim` | ~80 MB | Standard glibc |
| `ubuntu:24.04` | ~80 MB | Familiar |
| `ubuntu:24.04 + tools` | hundreds of MB | Real apps with deps |

## Networking Modes

| Mode | Description | Use |
|---|---|---|
| bridge (default) | Per-container veth on docker0 | Most apps |
| host | Container uses host network | Performance-critical, simple |
| none | No network | Worker / batch only |
| overlay | Multi-host (Swarm or K8s) | Multi-host |
| macvlan | Container has L2 MAC on host LAN | Legacy needs |

## Common Security Hardening

```bash
docker run \
  --read-only \
  --tmpfs /tmp \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --security-opt no-new-privileges \
  --security-opt seccomp=default.json \
  --user 1000:1000 \
  -v ./data:/data:ro \
  myimage
```

## Recommended Reading

- *Docker Deep Dive* — Nigel Poulton
- OCI Specifications (image, runtime, distribution)
- "Linux Containers from Scratch" Liz Rice talk
- Docker BuildKit documentation

## Interview Relevance

- "What is a container at the kernel level?" — gold-standard question
- "Optimize this Dockerfile" — practical exercise
- "Write a Dockerfile for a Python app" — basic
- "Compare Docker, Podman, containerd, runc"
- "How does multi-stage build work and what does it save?"

## Next

→ [L13 — Kubernetes (Beginner to Internals)](../L13/README.md)
