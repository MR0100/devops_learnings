# L07/C04/T01 — VMs (EC2, Compute Engine, Azure VMs)

## Learning Objectives

- Choose VM types and sizes
- Manage VM lifecycle

## VM Anatomy

Virtual Machine: software emulation of physical server. Hypervisor (Xen, KVM, Nitro) allocates slice of host hardware to guest OS.

```
Guest OS
↑
Hypervisor (host OS or bare-metal)
↑
Physical hardware
```

You get: dedicated vCPU, RAM, storage. Run any compatible OS.

## EC2 (AWS)

### Families
- **General** (M, T): balanced. T family burstable; cheaper but throttled if used 100%.
- **Compute** (C): more CPU per $. Web servers, batch.
- **Memory** (R, X): more RAM per $. DBs, caches.
- **Storage** (I, D, H): high disk IO. NoSQL, analytics.
- **GPU** (P, G, Inf): ML, graphics.
- **HPC** (Hpc): tightly coupled compute.

### Naming
`m6i.xlarge`
- `m`: family
- `6`: generation (newer = better perf/$)
- `i`: Intel (`a` AMD, `g` Graviton/ARM)
- `xlarge`: size (nano, micro, small, medium, large, xlarge, 2xlarge, ...)

### Picking Size
Start small; monitor CPU/RAM; right-size. Compute Optimizer recommends.

### Burstable (T family)
Earn CPU credits when idle; spend when active. Good for spiky low-avg workloads (small services, dev). Bad for sustained load.

## Compute Engine (GCP)

Naming: `n2-standard-4` = N2 gen, balanced family, 4 vCPU.
Families: N (general), C (compute-optimized), M (memory), A (GPU), E (cost-optimized).

Custom machine types: pick exact vCPU + RAM.

## Azure VMs

Naming: `Standard_D4s_v5` = standard tier, D series (general), 4 vCPU, premium storage support, v5.

Series: D (general), E (memory), F (compute), M (massive memory), L (storage), N (GPU).

## Lifecycle Operations

### Launch
```bash
aws ec2 run-instances \
  --image-id ami-xxxxx \
  --instance-type t3.micro \
  --key-name my-key \
  --security-groups my-sg \
  --subnet-id subnet-xxx
```

### Stop / Start
Stop: shut down OS; keep storage; pay only for storage. Public IP changes.
Start: resume; new IP unless using EIP.

### Reboot
OS restart; same instance; same IP.

### Terminate
Destroy. Data on instance store gone. EBS persists (per setting).

## AMI / Image

Snapshot of OS + apps. Boot from it.

Sources:
- AWS-provided (Amazon Linux, Ubuntu, Windows)
- Marketplace (RHEL, SUSE, etc.)
- Your custom (built with Packer)

Building custom AMIs avoids per-launch install delays. Includes:
- OS hardening
- Agents (monitoring, security)
- Pre-loaded app code (or pull on boot)

## User Data

Script run on first boot:
```bash
#!/bin/bash
yum update -y
yum install -y nginx
systemctl start nginx
```

Or use cloud-init for richer config.

Limit: ~16 KB. For more: pull from S3.

## IAM Role for EC2

Don't put keys on EC2. Use instance profile:
```bash
aws ec2 run-instances ... --iam-instance-profile Name=MyRole
```

App accesses AWS via SDK; SDK uses Instance Metadata Service:
```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/MyRole
```

Returns temp creds. Auto-rotates.

Use IMDSv2 (session-based) — IMDSv1 vulnerable.

## Networking

VM in VPC subnet. SG (firewall) attached. Private IP always; public IP optional.

For SSH:
- Bastion host (jump box)
- SSM Session Manager (no SSH; uses IAM)
- VPN

Best practice: no SSH inbound from Internet; use SSM.

## Storage Options

### Root Volume
EBS volume; persists across stop/start. Snapshot for backup.

### Instance Store
NVMe SSD on host. Fast. Ephemeral (lost on stop/terminate). Use for cache, tmp, scratch.

### Additional Volumes
Attach EBS volumes. Independent lifecycle.

## Auto Scaling Group

Manages fleet:
- Min, max, desired
- Health check (EC2 or ALB)
- Replacement on unhealthy
- Scaling policies (CPU > 70% → +1)

Combined with launch template (instance config).

## Pricing Levers

| Lever | Saving |
|---|---|
| Reserved/Savings Plans | 30-72% |
| Spot | 60-90% (interruptible) |
| Right-size | 20-50% |
| Off-hours dev/test | 60% |
| Graviton (ARM) | 20-40% over Intel |

## Graviton / ARM

AWS Graviton (ARM): cheaper, better perf/watt. Many apps compatible (recompile or runtime supports ARM).

GCP Tau T2A; Azure Ampere — similar.

## OS Choices

Common: Amazon Linux, Ubuntu, RHEL, CentOS Stream, SUSE, Windows.

For new: Amazon Linux 2023 or Ubuntu LTS most popular.

Windows: license cost extra. Use only if needed.

## Patching

Custom AMI rebuilt regularly OR patch in place via SSM Patch Manager, Ansible, Chef.

For long-lived instances: regular patching cadence (monthly).

For ephemeral (auto-scaled): rebuild AMI; replace.

## Monitoring

CloudWatch agent for OS metrics (memory, disk — EC2 default doesn't include).

Install via SSM:
```bash
sudo yum install -y amazon-cloudwatch-agent
```

Configure for desired metrics.

## Common Mistakes

- Hardcoded IAM keys (use roles)
- SSH from Internet (use SSM)
- Single AZ (use ASG across AZs)
- No backups (snapshot policy)
- Tinkering with running VMs (vs rebuilding)

## Cattle vs Pets

Pets: hand-managed; named; nurtured; replaced rarely.
Cattle: numbered; replaced freely; treated as fungible.

Modern: cattle. Hand-managed VMs = anti-pattern.

## Best Practices

- Build AMI in CI
- Launch from AMI
- Bootstrap via user data
- Run agent for config (SSM, Ansible)
- Replace, don't patch in place
- ASG manages replacement
- Logs/state external (not on instance)

## Quick Refs

EC2 family picker:

| Need | Family |
|---|---|
| Balanced general purpose | M (steady), T (burstable/spiky) |
| CPU-bound (web, batch) | C |
| RAM-bound (DBs, caches) | R / X |
| High disk IO (NoSQL, analytics) | I / D |
| ML / graphics | P / G / Inf |

Naming decode: `m6i.xlarge` → `m`=family, `6`=generation, `i`=Intel (`a`=AMD, `g`=Graviton/ARM), `xlarge`=size.

```bash
# Launch
aws ec2 run-instances --image-id ami-xxxx --instance-type t3.micro \
  --key-name my-key --security-group-ids sg-xxx --subnet-id subnet-xxx \
  --iam-instance-profile Name=MyRole

# Stop (keep EBS, stop compute charges) / Start / Terminate
aws ec2 stop-instances  --instance-ids i-xxxx
aws ec2 start-instances --instance-ids i-xxxx
aws ec2 terminate-instances --instance-ids i-xxxx

# Connect without SSH/bastion (IAM-based)
aws ssm start-session --target i-xxxx
```

Cost levers: Graviton (ARM) 20–40% cheaper · Spot up to 90% (interruptible) · Reserved/SP 30–72% · right-size 20–50%.

## Interview Prep

**Junior**: "VM vs container."

**Mid**: "Pick EC2 size for web app."

**Senior**: "Stateless EC2 fleet — design."

**Staff**: "Migrate VMware to EC2 strategy."

## Next Topic

→ [T02 — Containers (ECS, EKS, Fargate, Cloud Run)](T02-Containers.md)
