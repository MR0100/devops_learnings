# L03/C07/T01 — VPC, Subnets, Route Tables, IGW, NAT

## Learning Objectives

- Design a VPC layout
- Understand route tables
- Choose subnet placement strategy

## VPC Basics

A VPC is your own private virtual network in the cloud. Top-level container for:
- Subnets
- Route tables
- Internet gateway
- NAT
- Security groups, NACLs
- VPC endpoints

CIDR assigned at creation (e.g., 10.0.0.0/16). Plan generously — can't shrink later.

## Subnets

Slices of the VPC. Each subnet:
- Belongs to ONE Availability Zone
- Has its own CIDR (subset of VPC CIDR)
- Has its own route table (or uses VPC's default)
- Cannot span AZs

For Multi-AZ HA: create subnets in 2-3 AZs.

## Reference Layout

```
VPC 10.0.0.0/16 in us-east-1
├── AZ a (us-east-1a)
│   ├── public  10.0.1.0/24    ← public IPs; ALB
│   ├── private 10.0.11.0/24   ← app tier
│   └── data    10.0.21.0/24   ← DB tier
├── AZ b (us-east-1b)
│   └── (parallel set)
└── AZ c (us-east-1c)
    └── (parallel set)
```

3 AZs × 3 tiers = 9 subnets.

## Internet Gateway (IGW)

- One per VPC; attached
- Required for public Internet (in or out)
- Routing target: `0.0.0.0/0` → IGW makes a subnet "public"
- Itself free; bandwidth metered for some paths

## NAT Gateway

- AZ-scoped (one per AZ for HA)
- $0.045/hr + $0.045/GB processed
- Allows outbound-only from private subnets
- Highly available within AZ (AWS managed)

### Cost Trap
Chatty workloads can rack up data processing fees. See L08 for mitigations.

## Route Tables

Define where traffic goes for each destination.

Each subnet has ONE route table. Default route table created with VPC; you may add custom ones.

Sample public subnet route table:
| Destination | Target |
|---|---|
| 10.0.0.0/16 | local (VPC) |
| 0.0.0.0/0 | IGW |

Sample private subnet:
| Destination | Target |
|---|---|
| 10.0.0.0/16 | local |
| 0.0.0.0/0 | NAT GW (in same AZ) |

Sample data tier:
| Destination | Target |
|---|---|
| 10.0.0.0/16 | local |
| (no Internet route) | |

## Subnet Size

For typical apps:
- /24 (256 IPs, 251 usable) per tier per AZ
- /22 (1024) for high-pod-density EKS
- /20 (4096) for very large

AWS reserves 5 IPs per subnet: .0 (network), .1 (router), .2 (DNS), .3 (future), .255 (broadcast).

EKS with VPC CNI: each pod gets a VPC IP. Subnet exhaustion possible. Use larger subnets or custom networking.

## Reserved IPs Per Subnet

For /24 with 256 addresses:
- AWS reserves 5 → 251 usable
- Network address (.0) and broadcast (.255) are conceptual; AWS uses them internally too

## Internet Gateway Placement

```
Single VPC: one IGW
Multi-VPC: each VPC has its own IGW (or attached via Transit Gateway)
```

Cross-VPC routing through TGW handles different IGWs.

## NAT Strategies

### NAT GW per AZ (default)
Three AZs → three NAT GWs ($300+/mo before data).

### Single NAT GW
Cheaper but single point of failure across AZs.

### NAT Instance (Self-Managed)
EC2 with iptables MASQUERADE.
- Cheaper (just instance cost)
- Operational burden (no AWS HA)
- Mostly historical; use NAT GW

### Centralized Egress
- Spoke VPCs route through TGW to Egress VPC
- One set of NAT GWs serves all spokes
- Significant cost saving at scale

## VPC Endpoints (Brief)

Reach AWS services privately without IGW/NAT:
- **Gateway endpoint** (S3, DynamoDB): free; route table entry
- **Interface endpoint** (most AWS APIs): $0.01/hr + $0.01/GB

Avoid NAT data processing for AWS API calls.

## DHCP and DNS

AWS provides DHCP automatically. Each subnet has a default DNS resolver (VPC CIDR + 2).

Custom DNS via DHCP Options Set (rare; for on-prem AD integration etc.).

## Connectivity Patterns

```
Public ALB on public subnets
    ↓ via Security Group on private app subnets
App tier (EC2 / ECS / EKS pods)
    ↓
Database tier (RDS on data subnets, no Internet route)
```

Most modern: only ALB exposed; everything else private.

## Practical CIDR Allocation

For a multi-account org, reserve large blocks:
```
10.0.0.0/8 = your space
  10.0.0.0/16 = shared services
  10.1.0.0/16 = prod-us-east-1
  10.2.0.0/16 = prod-us-west-2
  10.3.0.0/16 = staging
  10.4.0.0/16 = dev
```

Within a VPC:
```
10.1.0.0/16 = prod-us-east-1
  10.1.0.0/20 = public subnets (one per AZ)
  10.1.16.0/20 = private app subnets
  10.1.32.0/20 = data subnets
```

## VPC Limits (default; soft)

- 5 VPCs per region
- 200 subnets per VPC
- 5 IGWs per region
- 5 NAT GWs per AZ
- 50 routes per route table

Most are soft limits; raise via support.

## Interview Prep

**Mid**: "Design a multi-AZ VPC."

**Senior**: "Why per-AZ NAT GW?"

**Staff**: "Reduce NAT cost for a large estate."

## Next Topic

→ [T02 — VPC Peering, Transit Gateway, PrivateLink](T02-Peering-TGW-PrivateLink.md)
