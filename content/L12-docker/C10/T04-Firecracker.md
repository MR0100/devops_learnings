# L12/C10/T04 — Firecracker microVMs

## Learning Objectives

- Understand Firecracker
- Use for serverless / tenant isolation

## Firecracker

AWS-built VMM (Virtual Machine Monitor):
- Written in Rust
- Minimal device emulation
- ~125 ms boot
- ~5 MB memory overhead per VM
- Open source

For: Lambda, Fargate, Fly.io, etc.

## vs Standard VM

Standard VM (QEMU): emulates many devices, slower boot.

Firecracker:
- virtio-only devices
- No graphics, no USB, no BIOS, no PCI
- Fast boot
- Low overhead
- Strong isolation

## Architecture

```
Firecracker process
└─ KVM (HW virtualization)
   └─ Guest kernel
      └─ Guest processes (e.g. function code)
```

One Firecracker per microVM.

## Use

```bash
firecracker --api-sock /tmp/fc.sock
```

API-driven via Unix socket:
```bash
# Set kernel
curl --unix-socket /tmp/fc.sock -X PUT 'http://localhost/boot-source' \
  -H 'Content-Type: application/json' \
  -d '{"kernel_image_path": "vmlinux", "boot_args": "console=ttyS0"}'

# Set rootfs
curl --unix-socket /tmp/fc.sock -X PUT 'http://localhost/drives/rootfs' \
  -H 'Content-Type: application/json' \
  -d '{"drive_id": "rootfs", "path_on_host": "rootfs.img", "is_root_device": true}'

# Boot
curl --unix-socket /tmp/fc.sock -X PUT 'http://localhost/actions' \
  -H 'Content-Type: application/json' \
  -d '{"action_type": "InstanceStart"}'
```

## Boot Time

~125 ms typical.

Compared:
- Standard container: 100 ms - 1 sec
- Standard VM: 10-60 sec
- Firecracker: 125 ms

For: function-as-a-service viability.

## Memory

~5 MB Firecracker overhead.
Plus guest kernel (10-30 MB) + workload.

For: dense packing.

## Snapshot/Restore

```bash
# Snapshot
curl -X PUT .../snapshot/create \
  -d '{"snapshot_path": "/snap.bin", "mem_file_path": "/mem.bin"}'

# Resume
curl -X PUT .../snapshot/load \
  -d '{"snapshot_path": "/snap.bin", "mem_file_path": "/mem.bin"}'
```

VM restore in ~10 ms.

For: cold-start mitigation.

## Use Cases

### AWS Lambda
Each function invocation → microVM.
Boot quickly, run code, freeze/destroy.

### AWS Fargate
ECS tasks: microVM per task.
Strong tenant isolation.

### Fly.io
App per microVM.
Fast deploy.

### Containerd Integration
Kata + Firecracker = Kata-VM containers.

## Density

Linux host:
- 1000s of microVMs concurrently
- Each isolated
- Low overhead

For: cost-efficient multi-tenant.

## Networking

Tap device:
```
firecracker tap → host bridge → external
```

Each microVM: separate tap; isolated.

## Storage

```json
{
  "drives": [{
    "drive_id": "rootfs",
    "path_on_host": "rootfs.img",
    "is_root_device": true
  }]
}
```

Block device backed by host file.

## Containers in Firecracker

Kata + Firecracker:
- Kata wraps OCI
- Uses Firecracker as VMM
- Container experience + VM isolation

For: best of both.

## firecracker-containerd

```bash
# Install
firecracker-containerd --config config.toml
```

Containerd shim that runs containers in Firecracker.

For: K8s with Firecracker.

## Performance

- Network: virtio; near-native
- Disk: virtio; near-native
- CPU: KVM passthrough; near-native
- Boot: 125 ms

Excellent throughput; minor latency.

## Limitations

- x86_64 + ARM64 only
- KVM required (host must support)
- No GPU passthrough (yet)
- Less feature-rich than QEMU

For: serverless and tenant isolation; not general-purpose VMs.

## Comparison

| | Firecracker | QEMU | gVisor | runc |
|---|---|---|---|---|
| Type | VMM | VMM | Userspace kernel | Container |
| Isolation | Strong (HW) | Strong (HW) | Medium | Weak (kernel-shared) |
| Boot | 125 ms | seconds | ~1 sec | <1 sec |
| Memory | ~5 MB+kernel | ~50 MB+ | low | low |
| Density | high | medium | high | very high |
| Compat | full kernel | full kernel | partial | full |

## Open Source

Apache 2.0; AWS-led.

GitHub: firecracker-microvm/firecracker.

## Real Use

- Lambda: ~10^9 invocations/day
- Fargate: container per task
- Fly.io: app per VM
- Vercel/Cloudflare: similar

## Cloud Hypervisor

Similar: Cloud Hypervisor.
- Intel-led
- Rust
- VMM
- Better device support
- Used by Kata

## Best Practices

- Snapshot for warm starts
- Right-size VM (RAM/CPU)
- Image bake (rootfs)
- Tap networking
- Health checks

## Common Mistakes

- Use for long-running general workloads (overkill)
- Snapshot pollution (state leaks)
- Forget HW virt requirement
- Slow rootfs

## Building Rootfs

```bash
# minimal rootfs
docker export $(docker create alpine) | tar -x -C rootfs/
mksquashfs rootfs rootfs.img
```

## Quick Refs

```bash
firecracker --api-sock /tmp/fc.sock

# API calls
curl --unix-socket /tmp/fc.sock -X PUT 'http://localhost/...' -d '{}'

# Containerd
firecracker-containerd
```

## Interview Prep

**Senior**: "Why Firecracker."

**Staff**: "Lambda architecture."

**Principal**: "Multi-tenant compute platform design."

## Next Topic

→ Move to [L13 — Kubernetes Deep](../../L13-kubernetes/README.md)
