# L12/C10/T03 — Kata Containers, gVisor (Sandboxed)

## Learning Objectives

- Understand sandboxed runtimes
- Use Kata / gVisor

## Why Sandbox

Standard containers: shared kernel.
- Escape = host compromise
- Kernel vulns affect all containers

Sandboxed:
- Container has its own kernel (Kata) or syscall filter (gVisor)
- Escape stops at sandbox boundary
- Defense in depth

For: multi-tenant, untrusted code.

## Kata Containers

Each container = lightweight VM:
- QEMU / Firecracker / Cloud Hypervisor underneath
- Real kernel per pod
- VT-x / AMD-V hardware virtualization
- ~125 MB memory overhead
- ~3 sec startup

## Architecture

```
podman/containerd → kata-runtime → VM (QEMU)
                                    └─ Linux kernel
                                       └─ container processes
```

## Install

```bash
# K8s with kata
kubectl apply -f https://github.com/kata-containers/kata-containers/.../runtime-class.yaml
```

## Use in K8s

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata
handler: kata
---
apiVersion: v1
kind: Pod
spec:
  runtimeClassName: kata
  containers:
  - name: app
    image: nginx
```

Per-pod runtime selection.

## gVisor

Google's user-space kernel:
- Intercepts syscalls
- Implements subset in Go
- Doesn't pass to host kernel directly
- Lighter than VM
- Some performance cost

## Architecture

```
container → runsc → sandbox process
                    └─ implements syscalls
                       └─ filtered passthrough to host kernel
```

## Install

```bash
# Binary
curl -fsSL https://gvisor.dev/.../runsc -o runsc
chmod +x runsc
```

Configure containerd:
```toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
  runtime_type = "io.containerd.runc.v2"
```

## Use in K8s

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
---
apiVersion: v1
kind: Pod
spec:
  runtimeClassName: gvisor
```

## Kata vs gVisor

| | Kata | gVisor |
|---|---|---|
| Tech | VM | Userspace kernel |
| Isolation | Hardware | Software (intercept) |
| Overhead memory | ~125 MB | ~10-30 MB |
| Overhead CPU | Low | Higher syscall cost |
| Startup | ~3 sec | ~1 sec |
| Compat | Excellent | Some syscalls unsupported |
| K8s native | Yes | Yes |
| Maturity | Strong | Strong |

## When Each

### Kata
- Max isolation
- Untrusted code (CI runners, FaaS)
- Compat critical
- HW virt available

### gVisor
- Multi-tenant SaaS
- Lower overhead
- Mostly app code (HTTP servers)
- Don't need exotic syscalls

## Workloads That Fail gVisor

- DBs needing specific syscalls
- Strace, perf, BPF tools
- Kernel modules
- Some debugging

For: test first.

## Performance

### Kata
- CPU: ~5% overhead
- Network: virtio (slight cost)
- Disk: similar
- Memory: +125 MB per pod

### gVisor
- CPU: 10-30% syscall-heavy workloads
- Network: similar
- Memory: lower
- Throughput: lower for I/O heavy

## Use Cases

### CI Runners
GitHub Actions: gVisor underneath.
Per-job sandboxed; can't break out.

### FaaS
Lambda: Firecracker (similar to Kata).
Per-function VM; isolated.

### Multi-Tenant SaaS
Customer A's container can't access customer B's host.

### Untrusted Code Execution
Browser-like execution: math problem solver, code playgrounds.

## Firecracker

AWS's microVM:
- Used by Lambda, Fargate
- Minimal device emulation (much smaller than QEMU)
- ~125 ms startup
- Very lightweight

For: serverless and tenant isolation.

## OpenShift / Containerd Integration

containerd: pluggable runtimes.
Add Kata or gVisor as RuntimeClass; deploy pods.

## Cost

- Kata: more CPU/RAM per pod; lower density
- gVisor: medium overhead

For multi-tenant: justified.

## Monitoring

Different metrics:
- Kata: VM events
- gVisor: sandbox process events

Existing tools work but adapt.

## Best Practices

- Sandbox untrusted only (cost)
- Test workloads (gVisor compat)
- Monitor sandbox health
- RuntimeClass selection per workload
- Pod Security Standards still apply

## Common Mistakes

- Sandbox everything (expensive)
- gVisor for incompatible workload
- Forget HW virt requirements (Kata)
- Skipping monitoring

## Real Use

- AWS Lambda: Firecracker
- Google Cloud Run: gVisor
- Fly.io: Firecracker
- Many CI runners: gVisor or microVM

## Quick Refs

```bash
# Pod with sandboxed runtime
spec:
  runtimeClassName: kata|gvisor

# RuntimeClass
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: NAME
handler: HANDLER
```

## Interview Prep

**Senior**: "Kata vs gVisor."

**Staff**: "Multi-tenant security architecture."

**Principal**: "Production sandboxed runtime strategy."

## Next Topic

→ [T04 — Firecracker microVMs](T04-Firecracker.md)
