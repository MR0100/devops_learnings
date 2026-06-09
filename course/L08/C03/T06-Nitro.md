# L08/C03/T06 — Nitro System Architecture

## Learning Objectives

- Understand Nitro
- Reason about EC2 performance

## What

AWS Nitro: custom hardware + lightweight hypervisor underlying modern EC2.

Pre-Nitro: Xen-based; significant overhead.
Nitro: most virtualization offloaded to dedicated cards.

## Components

### Nitro Card
Custom ASIC handling:
- VPC networking
- EBS storage
- Local NVMe
- Security

Frees CPU for VM workloads.

### Nitro Hypervisor
Lightweight Linux KVM-based; minimal overhead.

Replaces Xen.

### Nitro Security Chip
Hardware root of trust; checks integrity.

## Benefits

- More CPU/memory for VM (less hypervisor overhead)
- Native NVMe + EBS at near-bare-metal perf
- Enhanced networking (ENA, EFA)
- Better security isolation
- Bare metal support (.metal sizes)

## What Instances Are Nitro

All "modern" generations:
- m5 / m6 / m7
- c5 / c6 / c7
- r5 / r6 / r7
- T3 (most cases)

Old (m4, c4, r4): Xen.

## Bare Metal

`.metal` size: customer accesses physical hardware (Nitro card still does networking/storage).

Use:
- Nested virtualization (run own hypervisor)
- License-restricted (some Oracle, SAP)
- Hardware-specific apps

Cost: full physical box.

## EBS Performance

Pre-Nitro: EBS over network through hypervisor. Slow.
Nitro: EBS over Nitro card; near local NVMe perf.

Latency: sub-ms; throughput up to 5+ GB/s.

## ENA (Elastic Network Adapter)

Nitro-attached NIC. Default for modern instances.

Throughput: up to 100 Gbps per instance.

DPDK support for ultra-low latency.

## EFA (Elastic Fabric Adapter)

Specialized NIC for HPC / ML training:
- Bypass OS / kernel (SR-IOV)
- MPI / NCCL native support
- Lower latency than ENA

For: distributed training, HPC clusters.

Used with c5n, p4d, p5, hpc7g, etc.

## Local NVMe

Instance store on Nitro:
- Up to ~120 TB
- Up to ~3 GB/s per disk
- Ephemeral (lost on stop/terminate)

Use for: cache, scratch, ephemeral DB replicas.

i3en.metal: 60 TB local NVMe.
m6id.32xlarge: 7.5 TB local.

## Live Migration (Limited)

Nitro supports live updates of host firmware without instance reboot in some cases. Helps reduce scheduled maintenance.

## IMDSv2

Instance Metadata Service v2: session-token based; mandatory soon.

```bash
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id
```

Prevents SSRF (server-side request forgery) where attacker exploits app to read metadata.

Enforce IMDSv2 via launch template / SCP.

## NUMA

Larger instances: multiple NUMA nodes. App pinning to NUMA helps:
```bash
numactl --hardware
taskset -c 0-15 my-app
```

For HPC; usually transparent.

## Hibernation

Nitro supports hibernation: RAM dumped to EBS; resume faster than fresh boot.

Limited to specific families / sizes.

## Memory Encryption

Nitro Enclaves: isolated compute environment within instance:
- Hardware-isolated
- No persistent storage
- Cryptographic attestation
- Use: sensitive crypto operations, KMS attestation

For: payment processing, ML model protection.

## Security Isolation

Better than Xen:
- Each Nitro card has dedicated keys
- Host can't access VM memory
- Attestation verifies untampered

Important for: HIPAA, PCI workloads.

## SR-IOV

Single Root I/O Virtualization: instance directly accesses NIC; no hypervisor in network path.

Default for ENA. Faster + lower CPU.

## DPDK

Data Plane Development Kit: user-space packet processing for ultra-low latency.

Supported on ENA. Used by: telco, HFT.

## Time Sync

Nitro provides high-precision time service (PTP):
- Within microseconds across instances
- For: distributed databases, time-series

Available on .metal and large instances.

## Instance Network Performance

| Type | Network |
|---|---|
| t3 | up to 5 Gbps |
| m6i.large | up to 12.5 Gbps |
| m6i.4xlarge | up to 50 Gbps |
| m6i.16xlarge | up to 100 Gbps |
| m6in.* | up to 200 Gbps |
| p5 | 3200 Gbps (EFA) |

Larger = more network. n variant = even more.

## Choosing for Network

For network-heavy:
- Big instance for bandwidth
- `n` variant
- EFA-capable
- ENA Express (latest)

## Common Mistakes

- Old gen (m4/c4) when m6/c6 cheaper + faster
- Small instance for high network
- Forget EBS bandwidth limit (instance ceiling)
- IMDSv1 (vulnerable; force IMDSv2)
- Local NVMe data assumed persistent (it's not)

## Best Practices

- Modern generation always
- IMDSv2 enforced
- ENA/EFA where applicable
- Right size network
- Encryption (KMS + Nitro Enclaves for sensitive)

## Quick Refs

```bash
# Check Nitro
aws ec2 describe-instance-types --instance-types m6i.large --query 'InstanceTypes[*].Hypervisor'
# nitro

# IMDSv2
curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"
```

## Interview Prep

**Mid**: "What is Nitro."

**Senior**: "Nitro Enclaves use case."

**Staff**: "Architect HPC cluster with EFA."

## Next Topic

→ [T07 — EC2 Metadata Service (IMDSv1 vs IMDSv2)](T07-IMDS.md)
