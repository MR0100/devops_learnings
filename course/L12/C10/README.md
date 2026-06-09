# L12/C10 — Alternative Runtimes

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Podman.md) | Podman (Daemonless) | 0.5 hr |
| [T02](T02-Buildah.md) | Buildah for Image Building | 0.5 hr |
| [T03](T03-Kata-gVisor.md) | Kata Containers, gVisor (Sandboxed) | 1 hr |
| [T04](T04-Firecracker.md) | Firecracker microVMs | 0.5 hr |

## Podman

Daemonless container engine. Rootless by default. CLI-compatible with Docker.

### Differences from Docker
- No daemon (each container is a process tree)
- Rootless by default
- Pods (group of containers sharing namespaces — K8s-style)
- Generates K8s YAML (`podman generate kube`)
- systemd integration (services per container)

```bash
podman run -d --name web nginx
podman pod create --name myapp
podman run -d --pod myapp --name api myimage
podman run -d --pod myapp --name db postgres
# Containers in pod share network namespace
```

### Use Case
- Single-host workloads where Docker daemon overhead unwanted
- RHEL/Fedora environments (default)
- CI/CD runners (rootless safety)
- Air-gapped (smaller install)

## Buildah

Build OCI images without a daemon. More flexible than Dockerfile.

```bash
buildah from alpine            # base
buildah copy <id> ./bin/app /usr/local/bin/
buildah config --entrypoint '["/usr/local/bin/app"]' <id>
buildah commit <id> myimage:tag
```

Or use Dockerfile:
```bash
buildah bud -t myimage .
```

Pairs with Podman for daemonless build + run.

## Kata Containers

VM-isolated containers. Each container in its own lightweight VM (hypervisor: QEMU or Firecracker).

### Architecture
```
Container A (in VM A)
Container B (in VM B)
   ↑                       ↑
   │ kata-runtime         │
   ▼                       ▼
   Hypervisor (Firecracker / QEMU / Cloud Hypervisor)
   ▼
   Host kernel
```

### Properties
- True kernel isolation (each container = separate kernel)
- Boot ~1 second (vs raw VM minutes)
- Larger overhead than runc (~ms latency)
- Use when: multi-tenant K8s, untrusted workloads, compliance

### K8s Integration
```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata
handler: kata
```

```yaml
spec:
  runtimeClassName: kata
  containers: ...
```

## gVisor

Userspace kernel — intercepts container syscalls and handles them in userspace.

```
Container
   ↓ syscall
gVisor (runsc) → emulates kernel syscalls
   ↓
Host kernel (limited surface)
```

### Properties
- Much smaller attack surface than direct host kernel
- Slower than runc for syscall-heavy workloads
- Used by Google Cloud Run, App Engine

### Trade-Offs vs Kata
| | gVisor | Kata |
|---|---|---|
| Isolation | Userspace kernel | Hardware VM |
| Performance | Better for simple workloads | Better for I/O-heavy |
| Compatibility | Some syscalls unsupported | Full kernel |
| Memory | Lower | Higher (per-VM) |

## Firecracker

AWS's microVM. Started for Lambda; now widely used.

### Properties
- Microsecond boot
- ~5 MB memory overhead
- KVM-based
- API-controllable

### Used By
- **Lambda** (under the hood)
- **Fargate** (containers in microVMs)
- **Kata Containers** (as hypervisor)
- **Fly.io** (their containers are Firecracker VMs)
- **Weave Ignite** (microVMs that look like containers)

### Why
- VM-grade isolation
- Container-grade boot speed
- Sweet spot for multi-tenant FaaS

## Choosing a Runtime

| Runtime | Isolation | Performance | Use |
|---|---|---|---|
| runc | Process | Fastest | Default for trusted workloads |
| crun | Process | Fastest (Rust+C) | Drop-in for runc; faster, less memory |
| Kata | VM | Slower I/O | Multi-tenant, untrusted, compliance |
| gVisor | Userspace kernel | Slower syscalls | Multi-tenant, untrusted |
| Firecracker | microVM | Fast | FaaS, isolation-required |

## Setting Runtime Class in K8s

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
---
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  runtimeClassName: gvisor
  containers: [...]
```

## Real-World Use Cases

### Multi-Tenant K8s
- Untrusted tenants → Kata or gVisor
- Trusted SaaS workloads → runc

### Public-Facing Sandboxing
- User code execution (notebooks, CI runners) → gVisor or Firecracker

### Edge / Constrained
- runc or crun for resource efficiency

## Interview Themes

- "Compare runc, Kata, gVisor"
- "Why Firecracker for Lambda?"
- "When do you need VM isolation in containers?"
- "Podman vs Docker"
- "How to run gVisor in K8s?"
