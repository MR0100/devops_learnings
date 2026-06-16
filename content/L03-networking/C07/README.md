# L03/C07 — Cloud & Data Center Networking

## Chapter Overview

Cloud networking is its own discipline. VPCs, peering, Transit Gateway, PrivateLink, Direct Connect — these are the building blocks of every production cloud architecture.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-VPC-Subnets.md) | VPC, Subnets, Route Tables, IGW, NAT | 1.5 hr |
| [T02](T02-Peering-TGW-PrivateLink.md) | VPC Peering, Transit Gateway, PrivateLink | 1.5 hr |
| [T03](T03-Direct-Connect-VPN.md) | Direct Connect, VPN | 1 hr |
| [T04](T04-BGP-Anycast.md) | BGP and Anycast | 1 hr |
| [T05](T05-SDWAN.md) | SD-WAN | 0.5 hr |
| [T06](T06-Load-Balancing-L4-L7.md) | Load Balancing (L4 vs L7) | 1 hr |

## VPC Mental Model

A VPC is a virtual private network in the cloud:
- CIDR block (e.g., `10.0.0.0/16`)
- Subnets per AZ (smaller CIDRs from the VPC range)
- Route tables determine where traffic goes
- Internet Gateway (IGW) for public internet
- NAT Gateway (NAT GW) for private→public outbound

## Reference Layout

```
VPC 10.0.0.0/16 in us-east-1
├── AZ a
│   ├── Public subnet  10.0.1.0/24   (route 0/0 → IGW)
│   ├── Private subnet 10.0.11.0/24  (route 0/0 → NAT GW in 1.0/24)
│   └── Isolated subnet 10.0.21.0/24 (no internet route)
├── AZ b
│   ├── 10.0.2.0/24
│   ├── 10.0.12.0/24
│   └── 10.0.22.0/24
└── AZ c
    └── ...

Common:
- ALB / NLB → public subnets
- App servers → private subnets
- Databases → isolated subnets
- One NAT GW per AZ (NAT GW is AZ-scoped)
```

## Security Groups vs NACLs

| | Security Group | Network ACL |
|---|---|---|
| Stateful | Yes | No |
| Per | ENI/instance | Subnet |
| Rules | Allow only | Allow + deny |
| Default | Deny inbound, allow outbound | Allow all |
| Use | Application-level | Subnet-level coarse |

> Modern practice: rely on SGs. Use NACLs only for explicit subnet-wide deny or compliance.

## NAT Gateway

- Translates private→public for outbound from private subnets
- AZ-scoped (separate NAT GW per AZ for HA + cost)
- Costs: $0.045/hr + $0.045/GB data processed
- High-volume egress (S3, ECR, package mgrs) racks up cost

### Mitigations
- **VPC Endpoints (Gateway)** for S3 and DynamoDB — free, traffic skips NAT
- **VPC Endpoints (Interface)** for AWS APIs — cheaper than NAT egress
- **Centralized egress** via Transit Gateway in a shared egress VPC

## VPC Connectivity Options

### VPC Peering
- 1:1 connection between two VPCs
- No transitive routing (A↔B and B↔C doesn't give A↔C)
- Best for: few VPCs, simple topology
- CIDRs must not overlap

### Transit Gateway (TGW)
- Hub-and-spoke for many VPCs and on-prem
- Transitive routing
- Route tables on TGW for traffic policy
- Best for: 5+ VPCs

```
        ┌──────────────────┐
        │  Transit Gateway │
        └────┬───┬───┬─────┘
             │   │   │
        VPC A VPC B VPC C ... On-Prem (via DX/VPN)
```

### PrivateLink (VPC Endpoint Services)
- Expose service in one VPC to another VPC privately
- Producer puts ENI in consumer's VPC
- No CIDR conflicts (since traffic goes through ENI, not routed)
- Best for: SaaS/Service exposure to customers

## Direct Connect

Dedicated 1/10/100 Gbps connection from on-prem to AWS.

- Lower, consistent latency vs Internet
- Lower egress costs (~$0.02/GB vs $0.09/GB)
- Multi-port for HA
- Hosted connections (partner-provided) vs Dedicated

Setup: cross-connect at a DX location, configure BGP, attach to VPC via Virtual Interface (VIF) or to TGW.

## Site-to-Site VPN

IPSec tunnel from on-prem to AWS VPN Gateway or TGW. Uses Internet underneath; encrypted.

- Per tunnel: ~1.25 Gbps cap on AWS side
- Best for: lower-volume hybrid or DX backup

## BGP Basics

Border Gateway Protocol — how the Internet routes between Autonomous Systems (ASes).

- eBGP: between ASes (Internet)
- iBGP: within an AS
- Each AS advertises prefixes it owns
- Path attributes: AS_PATH, local preference, MED
- Decisions: shortest AS_PATH, then MED, etc.

Misconfigurations cause global outages (Facebook 2021, Cloudflare 2019).

In AWS: BGP runs on DX VIFs and VPN tunnels. You advertise your on-prem prefixes; AWS advertises VPC CIDRs.

## Anycast

Same IP advertised from many locations. Internet routes to nearest.

Used for:
- DNS (1.1.1.1, 8.8.8.8)
- CDN edges
- DDoS absorption
- AWS Global Accelerator
- Cloudflare and many CDNs

The "nearest" routing uses BGP — clients connect to wherever shortest AS path leads.

## SD-WAN

Software-defined WAN. Orchestrates branch-to-cloud connectivity with policy:
- Application-aware routing
- Multiple underlay options (MPLS, Internet, LTE)
- Centralized control plane

Vendors: Cisco, Aruba, Versa, VMware (VeloCloud), Cisco Meraki, Fortinet.

Cloud-native variants: AWS Cloud WAN, Azure Virtual WAN.

## Common Production Patterns

### Multi-AZ HA App
```
[Public ALB across all AZs]
        │
[Private app subnets, ASG across AZs]
        │
[Isolated DB (RDS Multi-AZ)]
```

### Centralized Egress
```
Each spoke VPC → TGW → Egress VPC (NAT GW, FW) → Internet
```

### Service Producer
```
Producer VPC ── PrivateLink ── Consumer VPC (no CIDR conflict)
```

## Cost Traps

| Trap | Cost |
|---|---|
| NAT GW chatty workload | $1000s/mo |
| Cross-AZ DB calls | $0.01/GB × volume |
| ALB ↔ Backend in different AZ | Same |
| Inter-region replication | $0.02/GB |
| Egress to Internet | $0.05-0.09/GB |
| VPN with redundant tunnels | $0.05/hr each |

## Interview Themes

- "Design a multi-AZ VPC"
- "Compare VPC Peering, TGW, PrivateLink"
- "How does NAT Gateway work and how do you avoid its cost?"
- "Why do BGP misconfigurations take down the Internet?"
- "What is Anycast and how does it work?"
- "When DX vs VPN?"
