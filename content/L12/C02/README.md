# L12/C02 — Docker Architecture

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Docker-Architecture.md) | dockerd, containerd, runc | 1 hr |
| [T02](T02-OCI-Spec.md) | OCI Image & Runtime Spec | 0.5 hr |
| [T03](T03-Docker-Podman-Nerdctl.md) | Docker vs Podman vs nerdctl | 0.5 hr |

## The Stack

```
$ docker run ...
       │ CLI
       ▼
┌──────────────────┐
│ dockerd          │ HTTP API; image mgmt; networking; volumes
│ (Docker Engine)  │
└─────────┬────────┘
          │ gRPC (CRI / Docker shim historically)
          ▼
┌──────────────────┐
│ containerd       │ Container lifecycle manager
│                  │ Image pull, image cache, runtime supervisor
└─────────┬────────┘
          │
          ▼
┌──────────────────┐
│ containerd-shim  │ Decouples container's lifetime from containerd
└─────────┬────────┘
          │
          ▼
┌──────────────────┐
│ runc             │ OCI runtime — actually creates the container
│ (or crun, kata)  │ unshare + cgroups + chroot + setup
└──────────────────┘
          │
          ▼
   Your processes
```

## What Each Does

### dockerd (Docker Engine)
- Receives CLI/API calls
- Manages images, containers, networks, volumes
- Pre-2020: also did K8s CRI translation; now containerd does it directly

### containerd
- Industrial-strength container runtime
- Image pull, store
- Runtime mgmt via OCI runtime (runc)
- Used by Docker, Kubernetes (via CRI), nerdctl
- Started life inside Docker; spun out to CNCF

### containerd-shim
- One per container
- Allows containerd to be upgraded/restarted without killing containers
- Forwards signals, manages stdio

### runc
- Reference OCI runtime implementation
- Reads `config.json` (OCI runtime spec)
- Sets up: namespaces, cgroups, mounts, capabilities, seccomp
- Forks the actual process

### Alternative Runtimes
- **crun** — Rust+C, faster, less memory
- **gVisor** (runsc) — userspace kernel for sandbox isolation
- **Kata Containers** — VM-isolated containers (microVM per container)
- **Firecracker** — AWS's microVM (used by Fargate, Lambda)

## OCI Specifications

### Image Spec
An OCI image is:
- **Index** (multi-arch) → multiple **Manifests**
- **Manifest** → references **Config** + **Layers**
- **Config**: JSON with env, cmd, entrypoint, labels, history
- **Layers**: tar archives (one per filesystem change)

```
my-image
├── index.json
├── blobs/sha256/
│   ├── abc... (manifest)
│   ├── def... (config)
│   ├── ghi... (layer 1)
│   ├── jkl... (layer 2)
│   └── mno... (layer 3)
```

### Runtime Spec
- `config.json` describes how to run a container
- Bundle = config.json + rootfs/
- `runc run <bundle>` executes

### Distribution Spec
- HTTP API for registries
- `/v2/<name>/manifests/<reference>`, `/v2/<name>/blobs/<digest>`
- All registries (Docker Hub, ECR, GCR, Harbor) implement this

## Docker vs Podman vs nerdctl

### Docker
- The original; Docker Inc. commercial backing
- `dockerd` daemon
- Docker Desktop on Mac/Windows (VM under the hood)
- Largest ecosystem

### Podman
- **Daemonless** (no long-running daemon)
- **Rootless by default** (better security)
- `podman run` syntax similar to Docker
- `podman-compose` for compose
- Pods (group of containers sharing namespaces — K8s-style)
- RHEL/Fedora default

### nerdctl
- containerd's native CLI
- Drop-in for docker syntax
- No daemon (uses containerd directly)
- Good for K8s nodes (you already have containerd)

### Comparison

| | Docker | Podman | nerdctl |
|---|---|---|---|
| Daemon | Yes (dockerd) | No | No (uses containerd) |
| Rootless | Supported (extra setup) | Default | Yes |
| Pods | No | Yes | No |
| `docker` compat | Yes | Yes | Yes |
| Default in | Most laptops | RHEL/Fedora | K8s nodes |
| Docker Desktop alt | — | Podman Desktop | — |

## Container Runtime in Kubernetes

K8s uses **CRI** (Container Runtime Interface):
- containerd (default on most managed K8s)
- CRI-O (Red Hat's; used in OpenShift)
- Docker (deprecated; dockershim removed in 1.24)

CRI → containerd → runc → kernel.

## Why Docker Lost K8s

Originally K8s used Docker via "dockershim". Docker had unnecessary layers for K8s (engine API, networking, volumes that K8s replaced). K8s 1.24 dropped dockershim. Now K8s uses containerd directly.

Docker Inc. still dominant on developer desktops (Docker Desktop).

## License Note

Docker Desktop is paid for companies > 250 employees / > $10M revenue. Alternatives: Podman Desktop, Rancher Desktop, OrbStack (Mac).

## Interview Themes

- "Walk me through dockerd, containerd, runc"
- "What is OCI?"
- "Why did K8s deprecate Docker?"
- "Compare Docker, Podman, nerdctl"
- "What does runc actually do?"
- "Kata vs gVisor vs runc"
