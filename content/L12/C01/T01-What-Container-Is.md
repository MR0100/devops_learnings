# L12/C01/T01 — What a Container Actually Is

## Learning Objectives

- Demystify "container"
- Understand vs VM

## Container Definition

A container is just a process (or set of processes) running with:
- Isolated namespaces
- Resource limits (cgroups)
- Restricted capabilities + seccomp
- Layered filesystem (typically)

It's NOT magic. It's a Linux process with restrictions.

## vs VM

| | VM | Container |
|---|---|---|
| Boot | OS + apps | Just process |
| Size | GB | MB-100s of MB |
| Start | Minutes | Seconds |
| Isolation | Hardware-level | Kernel-level |
| Overhead | High | Low |
| Density | 10s per host | 100s-1000s per host |

VM = whole OS in software.
Container = process with isolation.

## The "Container" is a Lie

There's no kernel `container()` syscall. Containers are:
- Namespaces
- Cgroups
- Filesystems
- Capabilities
- Seccomp profiles

Together: feels like isolated environment.

## Layers

```
┌────────────────────────┐
│ Container runtime (runc)│
├────────────────────────┤
│ Linux kernel features:  │
│ - Namespaces            │
│ - Cgroups               │
│ - Seccomp               │
│ - Capabilities          │
│ - LSM (AppArmor/SELinux)│
└────────────────────────┘
```

Runtime configures kernel features; starts process.

## Container Lifecycle

```bash
docker run nginx
```

What happens:
1. dockerd contacts containerd
2. containerd checks image; pulls if needed
3. Image layers mounted (overlayfs)
4. Network configured (CNI)
5. containerd calls runc
6. runc: create namespaces, cgroups, seccomp
7. runc: execve(nginx)
8. Process running

## Verify

Run container; inspect from host:
```bash
# Container PID 1
docker run -d nginx
docker inspect <container> --format '{{.State.Pid}}'
# PID: 12345

# Same PID on host
ps -p 12345
# nginx process

# In container's PID namespace
docker exec <container> ps
# PID 1: nginx
```

Same process; different PID namespace.

## Single Process Default

Container should be single process (or one root process tree).

For multi-process:
- Use systemd / supervisord (heavy)
- Or split into multiple containers (better)

## Container vs Image

- **Image**: filesystem snapshot + metadata (read-only)
- **Container**: running instance of image (writable layer + process)

Like:
- Class : Object
- Recipe : Cake

## Image Layers

```
┌──────────────────┐
│ Container layer  │ (read/write; ephemeral)
├──────────────────┤
│ App layer        │
├──────────────────┤
│ Dependencies     │
├──────────────────┤
│ Base OS layer    │
└──────────────────┘
```

Image = layers (each immutable).
Container = layers + thin RW layer on top.

## Why Containers Won

- Fast (seconds vs minutes)
- Lightweight (KB-MB overhead)
- Portable (run anywhere with kernel)
- Reproducible (same image = same env)
- Dense (many per host)

## What Containers Don't Solve

- App design issues
- Stateful complexity
- Distributed systems hard problems
- Security inherently

Just: package + run consistently.

## Container vs chroot

chroot: filesystem namespace only. Old (1979).
Container: chroot + many other namespaces + cgroups.

Modern Linux: way more isolation.

## OCI

Open Container Initiative: standards for:
- Image format
- Runtime
- Distribution

Standardized → Docker, Podman, K8s, etc. interoperate.

## Container Process Isolation

What's isolated:
- PID (own process tree)
- Network (own interfaces)
- Mount (own filesystem view)
- UTS (hostname)
- IPC (semaphores, queues)
- User (UID mapping)
- Cgroup (resource controllers)

What's shared (with host):
- Kernel
- Hardware

For: kernel security important; container ≠ VM.

## Kernel Sharing Risk

If app exploits kernel vulnerability:
- VM: limited to that VM
- Container: can escape (kernel == host kernel)

Mitigations:
- Seccomp (restrict syscalls)
- AppArmor / SELinux
- gVisor / Kata (containers with VM isolation)
- Runtime security (Falco)

## When Container Beats VM

- Microservices
- CI/CD
- Dev environments
- Stateless apps
- Density matters
- Fast scaling

## When VM Beats Container

- Stronger isolation (multi-tenant SaaS)
- Different OS kernels
- Legacy apps not container-friendly
- Specific OS features

## Modern Cloud

- VM: cloud instance (EC2, GCE)
- Containers run inside VMs
- K8s orchestrates containers
- Pods group containers

VMs underneath; containers on top.

## Container Density Real

For 1 VM (4 vCPU, 16 GB):
- Run 50-200 small containers
- vs 1 VM = 1 app

For: efficient resource use.

## State of Containers (2026)

- Standardized (OCI)
- Production-ready
- Multi-arch (ARM + amd64)
- Mature ecosystem (K8s, Helm, ArgoCD)
- Secure (with policies)

## Examples

### Run nginx
```bash
docker run -d -p 80:80 nginx
```

Pulls image, starts container, exposes port.

### Build + run
```bash
docker build -t myapp .
docker run -d -p 8080:8080 myapp
```

## Inspect

```bash
# Running
docker ps

# Specific
docker inspect <container>

# Resources
docker stats

# Logs
docker logs <container>

# Process tree
docker top <container>
```

## Best Practices

- One concern per container — a single root process tree, not a pile of services behind supervisord.
- Treat containers as immutable and ephemeral — rebuild the image to change them, don't `docker exec` fixes into a running one.
- Don't rely on the container boundary for security isolation — the kernel is shared; add seccomp/AppArmor/SELinux, drop capabilities, and run rootless.
- Reach for stronger isolation (gVisor, Kata, or a VM) for untrusted/multi-tenant workloads instead of assuming a container contains a hostile process.
- Keep images small and layered for cache reuse (deps before code); a smaller image is a smaller attack surface.
- Make state explicit — put it in volumes or external stores, never in the writable container layer.

## Common Mistakes

- Believing a container is a lightweight VM — it is a host process; a kernel exploit can escape it.
- Running many services in one container, making logs, restarts, and scaling unmanageable.
- Storing data in the container's writable layer and losing it on the next `docker rm`/redeploy.
- Assuming "it's in a container" means "it's secure" — without seccomp/caps/rootless, an escape is one CVE away.
- Confusing image (read-only template) with container (running instance + RW layer) when reasoning about state.
- Running as root inside the container by default, so a breakout lands as root on the host namespace.

## Quick Refs

```bash
# Run
docker run IMAGE
docker run -d --name NAME IMAGE
docker run -it IMAGE bash

# Manage
docker ps
docker ps -a
docker stop CONTAINER
docker rm CONTAINER

# Image
docker images
docker pull IMAGE
docker rmi IMAGE
```

## Interview Prep

**Junior**: "What's a container."

**Mid**: "Container vs VM."

**Senior**: "Container internals."

**Staff**: "When use container vs VM."

## Next Topic

→ [T02 — Namespaces (Recap from L02)](T02-Namespaces.md)
