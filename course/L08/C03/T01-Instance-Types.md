# L08/C03/T01 — Instance Types & Families

## Learning Objectives

- Pick EC2 instance type confidently
- Understand naming

## Naming Convention

`m6i.xlarge`:
- `m`: family (general purpose)
- `6`: generation (newer = better perf/$)
- `i`: variant (i = Intel; a = AMD; g = Graviton/ARM)
- `xlarge`: size

Modifiers:
- `n`: high network bandwidth
- `d`: NVMe local SSD instance store
- `z`: high clock speed
- `b`: high storage (i3en.b)

## Families

| | Optimized for | Examples | Use |
|---|---|---|---|
| T | Burstable, cheap | t3, t4g | Dev, small services |
| M | General | m6i, m7i | Web apps, small DBs |
| C | Compute (CPU) | c6i, c7i | Batch, HPC, video |
| R | Memory | r6i, r7i | DBs, caches |
| X | Massive memory | x2gd, x2idn | In-memory DBs |
| I | High IOPS (NVMe) | i3, i4i | NoSQL, analytics |
| D | High storage HDD | d3 | Hadoop, big data |
| H | High storage HDD/SSD | h1 | Distributed FS |
| Z | High clock | z1d | Sub-ms apps |
| G | GPU | g5, g6 | ML inference, graphics |
| P | High GPU | p4, p5 | ML training |
| Inf | Inferentia (ML inference) | inf1, inf2 | ML inference |
| Trn | Trainium (ML training) | trn1, trn2 | ML training |
| F | FPGA | f1 | Genomics, finance |
| HPC | High-perf cluster | hpc7g | Tightly-coupled compute |
| Mac | macOS | mac1, mac2 | iOS/macOS builds |
| U | Bare metal SAP HANA | u-* | Massive enterprise |

## Generation

Newer = better. Always prefer latest:
- m4 → m5 → m6 → m7 (gradual improvements: faster CPU, more network)

m7i: latest Intel; m7a: AMD; m7g: Graviton.

## Graviton (ARM)

AWS custom CPU. Cheaper, better perf/watt.
- m7g, c7g, r7g

Most Linux apps recompile easily. Worth trying.

40-60% better perf/$ vs Intel often.

## Burstable (T family)

Earn CPU credits when idle (<baseline %); spend when busy.
- t3.micro: baseline 10% CPU; 30 credits/hour earned
- Saved credits used when above baseline

Cheap for spiky workloads. Bad for sustained:
- After credits exhausted: throttled
- Unless `unlimited` mode (pay for over-baseline)

For unpredictable: T family OK. For predictable steady: M family.

## Sizes

```
nano    < micro < small < medium < large < xlarge < 2xlarge < 4xlarge ... 32xlarge
```

Each size doubles vCPU + memory.

Pricing: linear with size.

## Pick Process

1. Workload type:
   - General → M
   - CPU-heavy → C
   - Memory-heavy → R
   - GPU → G/P
2. Size: start small; grow
3. Generation: latest
4. Variant: try Graviton first (cost)
5. Run; monitor; right-size

## Real Examples

### Web App
m6i.large (2 vCPU, 8 GB). Or m7g.large (Graviton, cheaper).

### High-Traffic Web
c6i.xlarge (4 vCPU, 8 GB) or c7g.xlarge.

### Postgres DB
r6i.large minimum (memory matters). r6i.xlarge or r6i.2xlarge typical.

### Cache (Redis)
r6i / r7g; or use ElastiCache.

### Analytics ETL
c6i.4xlarge or r6i.4xlarge.

### ML Training
p4d.24xlarge (8x A100 GPUs).

### Build Servers
c6i.2xlarge or m6i.2xlarge with high disk.

## Specialized

### Z1D (High Clock)
4.0+ GHz. For latency-sensitive single-threaded (financial, gaming).

### F1 (FPGA)
Custom hardware acceleration. Genomics, video, cryptocurrency.

### Mac
For iOS/macOS CI. Bare-metal Mac mini. 24-hour minimum.

### Bare Metal
*.metal: full instance; no virtualization. For nested virtualization or hardware-direct.

## Networking Tiers

Higher instances: more network bandwidth:
- m6i.large: up to 12.5 Gbps
- m6i.4xlarge: up to 50 Gbps
- m6i.16xlarge: up to 100 Gbps
- m6in.* (network variant): up to 200 Gbps

Network-heavy workloads: bigger instance for more bandwidth OR `n` variant.

## EBS Bandwidth

Higher instances: more EBS bandwidth. For DB performance: larger instance.

## Enhanced Networking

ENA (Elastic Network Adapter): default on modern instances. Up to 100 Gbps.

EFA (Elastic Fabric Adapter): for HPC; low-latency / high-throughput; bypass OS for MPI workloads.

## Placement Groups

Affect physical placement:
- Cluster: same rack; low latency; high throughput
- Spread: different racks; failure isolation
- Partition: groups of racks (Hadoop, Cassandra)

For: tightly-coupled compute (cluster), critical instances (spread).

## Hibernate

Stop with RAM saved to EBS. Resume faster than fresh boot.

Limited support; specific instance families. Edge cases (long-running processes that take time to warm).

## Right-Sizing Tools

- CloudWatch CPU / memory metrics
- AWS Compute Optimizer: recommendations
- Spotinst / vendor tools

Goals: avg 40-60% CPU at peak. Sustained <30% → downsize.

## Spot Eligibility

Most families work as Spot. Specific are sometimes preferred (older gen often more capacity).

Diversify across types/AZs to reduce interruption.

## Common Mistakes

- Too big (over-provisioned; expensive)
- Too small (saturated; perf issues)
- Old generation (paying more for less)
- Burstable for sustained (throttled silently)
- Network-heavy without `n` variant

## Per-Service Required

Some services require specific:
- EKS managed nodes: limited types
- RDS: own type list
- Aurora Serverless: not user-pickable

Check service docs.

## Quick Refs

```bash
# List available
aws ec2 describe-instance-types --filters Name=processor-info.supported-architecture,Values=arm64

# Pricing
aws pricing get-products --service-code AmazonEC2 ...
```

## Interview Prep

**Junior**: "M vs C vs R."

**Mid**: "Pick instance for web app + Redis."

**Senior**: "Graviton — when to switch."

**Staff**: "Cost / perf model for 10k instance fleet."

## Next Topic

→ [T02 — AMIs, Launch Templates, Auto Scaling Groups](T02-AMI-ASG.md)
