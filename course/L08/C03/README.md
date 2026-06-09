# L08/C03 — EC2 & Compute

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Instance-Types.md) | Instance Types & Families | 1 hr |
| [T02](T02-AMIs-LT-ASGs.md) | AMIs, Launch Templates, Auto Scaling Groups | 1.5 hr |
| [T03](T03-Placement-Groups.md) | Placement Groups (Cluster, Spread, Partition) | 0.5 hr |
| [T04](T04-EBS.md) | EBS Types (gp3, io2, st1, sc1) and Performance | 1 hr |
| [T05](T05-Spot-SP-RI.md) | Spot, Savings Plans, Reserved Instances | 1 hr |
| [T06](T06-Nitro.md) | Nitro System Architecture | 0.5 hr |
| [T07](T07-IMDS.md) | EC2 Metadata Service (IMDSv1 vs IMDSv2) | 0.5 hr |

## Instance Type Naming

```
m6i.large
│ │ │  └ size (nano, micro, small, medium, large, xlarge, 2xlarge, ..., 24xlarge, metal)
│ │ └ additional features (i=intel, a=AMD, g=Graviton, n=enhanced networking, d=local NVMe, e=extended)
│ └ generation (1, 2, 3, ..., 6, 7)
└ family
```

### Families

- **T (burstable)** — CPU credits, cheapest
- **M (general)** — balanced ratio CPU:RAM (1:4)
- **C (compute)** — 1:2 ratio
- **R (memory)** — 1:8
- **X (mem-optimized)** — 1:30+
- **I (storage)** — local NVMe
- **D, H** — HDD
- **P, G** — GPU
- **Inf, Trn** — ML accelerators
- **HPC** — HPC clusters
- **Mac** — Mac mini

### Graviton (ARM)
g, m7g, c7g, r7g — 20-40% cheaper than Intel/AMD equivalent. Most modern workloads run on ARM (especially Linux containers).

## AMIs

Amazon Machine Image — VM template.

```bash
aws ec2 describe-images --owners amazon \
  --filters "Name=name,Values=al2023-ami-*-x86_64" \
            "Name=state,Values=available" \
  --query "sort_by(Images,&CreationDate)[-1].ImageId" \
  --output text
```

### Building AMIs
- Packer (HashiCorp) — define in HCL, build images for any cloud
- EC2 Image Builder — AWS-native pipeline
- "Golden AMI" pipeline: base → harden → install agents → snapshot → publish + share to org

### Best Practice
- Versioned, tagged AMIs
- Replace, don't patch (immutable infra)
- Bake AMIs in CI; cache image registry

## Launch Templates & ASGs

### Launch Template
Reusable instance launch config.
- AMI, instance type, key pair, SG, IAM profile, user data, etc.
- Versioned (you can update LT and ASG references new version)

### Auto Scaling Group (ASG)
- min/max/desired counts
- Subnets to launch into (AZ-distribution)
- Health checks (EC2 or ELB-based)
- Scaling policies (target tracking, step, scheduled)
- Mixed instances policy (spot + on-demand mix)
- Lifecycle hooks (pause for setup/drain)

```yaml
# Mixed Instances Policy
OnDemandBaseCapacity: 2
OnDemandPercentageAboveBaseCapacity: 30
Overrides:
- InstanceType: m6i.large
- InstanceType: m6a.large
- InstanceType: m6g.large
SpotAllocationStrategy: capacity-optimized
```

Target tracking is the easy default:
```
Maintain CPU utilization at 60%
ASG scales pod count to keep there
```

## Placement Groups

Influence instance placement for performance or resilience.

| Type | Behavior | Use |
|---|---|---|
| Cluster | All instances in same AZ, close hardware | Low-latency HPC |
| Spread | All instances on different hardware (max 7 per AZ) | Critical small fleets |
| Partition | Logical partitions, each on different hardware | Big distributed (Cassandra, HDFS) |

## EBS Types

| Type | Max IOPS | Max Throughput | Cost (US-east-1) | Use |
|---|---|---|---|---|
| gp3 | 16K (provisioned) | 1000 MB/s (provisioned) | $0.08/GB-mo | General default |
| gp2 | 16K (size-tied) | 250 MB/s | $0.10/GB-mo | Legacy |
| io2 | 256K | 1000 MB/s | $0.125/GB-mo + IOPS | High-IOPS DB |
| io2 Block Express | 256K | 4000 MB/s | Premium | Critical DB |
| st1 | low | 500 MB/s | $0.045/GB-mo | Big data sequential |
| sc1 | low | 250 MB/s | $0.015/GB-mo | Cold |

**gp3 vs gp2**: gp3 is 20% cheaper, lets you provision IOPS/throughput independently. Migrate.

### EBS Performance

- Baseline + burst (gp3 doesn't burst — provision for peak)
- Instance has EBS bandwidth cap (check instance specs)
- Multi-attach (io2) — limited use cases (cluster filesystems)

## Spot, RIs, Savings Plans

### Spot
- Up to 90% off
- 2-min interruption warning via metadata + EventBridge
- Use: stateless, batch, K8s autoscale-out
- Pair with on-demand baseline for criticality

### Reserved Instances
- 1-yr or 3-yr commit
- Standard (no flex) or Convertible (change family)
- Up to 72% off (3-yr standard, no upfront)

### Savings Plans
- $X/hr commit, 1-yr or 3-yr
- Compute SP (any family/region/OS) — most flexible
- EC2 Instance SP (specific family) — better discount

**Recommendation**: 1-yr Compute SPs for the baseline; RIs only if you need to lock specific families; Spot for elastic scale.

## Nitro

AWS's modern hypervisor (replaces Xen). Key wins:
- Almost all hardware acceleration: networking, storage, security
- Hypervisor footprint is tiny
- Enables: many cores, much network bandwidth, NVMe at instance speeds
- Foundation for Nitro Enclaves (isolated environments for secrets)

All modern (5th gen+) instances are Nitro.

## IMDSv2

EC2 Instance Metadata Service — link-local 169.254.169.254 endpoint.

### v1 (Legacy, Vulnerable)
```bash
curl http://169.254.169.254/latest/meta-data/instance-id
```

### v2 (Token-Required)
```bash
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
   -H "X-aws-ec2-metadata-token-ttl-seconds: 600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
   http://169.254.169.254/latest/meta-data/instance-id
```

v2 prevents SSRF attacks — an attacker can't make IMDS calls via a vulnerable web server without the token.

**Always enforce v2-only**:
```bash
aws ec2 modify-instance-metadata-options \
  --instance-id i-123 \
  --http-tokens required \
  --http-put-response-hop-limit 1
```

## Interview Themes

- "Pick an instance type for X workload"
- "Spot — when not to use?"
- "Walk me through ASG scaling decision"
- "Compare placement group types"
- "Why is IMDSv2 important?"
- "gp3 vs gp2 — what changed?"
