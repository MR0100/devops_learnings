# L07/C07/T01 — VPC, Subnets, Route Tables (Across Clouds)

## Learning Objectives

- Build VPC architecture
- Understand routing

## VPC

Virtual Private Cloud: isolated network in cloud. CIDR block; subdivides into subnets.

AWS terminology; Azure: VNet; GCP: VPC (similar across).

## CIDR Planning

VPC: /16 (65k IPs) or /20 (4k).
Subnets: /24 (256 IPs) typical.

Allocate by AZ:
- 10.0.0.0/16 VPC
- 10.0.1.0/24 public AZ-A
- 10.0.2.0/24 public AZ-B
- 10.0.10.0/24 private AZ-A
- 10.0.11.0/24 private AZ-B

Reserve room for future subnets.

## Public vs Private Subnets

**Public**: has route to Internet Gateway (IGW). Instances with public IP reachable.

**Private**: no IGW route. Instances need NAT Gateway for outbound; not reachable from Internet.

## Typical 3-Tier

```
Public subnets (LB, bastion)
  ↓
Private subnets (app tier)
  ↓
Private subnets (DB tier)
```

LB faces Internet (public); apps in private; DBs deeper.

## Internet Gateway (IGW)

Logical attachment to VPC; allows Internet ingress/egress for resources with public IPs.

One per VPC. Free.

## NAT Gateway

For private subnets to reach Internet (outbound only):
```
Private instance → NAT GW (in public subnet) → IGW → Internet
```

Costs:
- $0.045/hour
- $0.045/GB processed

One per AZ for HA. Often biggest cloud bill item (NAT processing).

## NAT Instance

Old way: an EC2 doing NAT. Cheaper but you manage. Mostly deprecated.

## Route Tables

Map CIDRs to next hop:
```
Destination       Target
10.0.0.0/16       local
0.0.0.0/0         igw-xxx        (public subnet)

Destination       Target
10.0.0.0/16       local
0.0.0.0/0         nat-xxx        (private subnet)
```

Each subnet associated with one route table.

## Security Groups

Stateful firewall at instance level. Allow rules only.
- Inbound: from CIDR or SG; ports
- Outbound: to CIDR or SG; ports

Reference other SGs: "allow port 5432 from app-sg".

## NACLs

Stateless firewall at subnet level. Allow + deny rules; ordered.

Less common; mostly SGs. NACLs for explicit subnet boundaries.

## VPC Endpoints

Private connection to AWS services without Internet:
- Gateway endpoints: S3, DynamoDB (free)
- Interface endpoints: most other services ($0.01/hour/endpoint, $0.01/GB)

Why: cost (no NAT), security (no public exposure), perf.

## VPC Peering

Two VPCs talk directly:
```
VPC A (10.0.0.0/16) ←→ peering ←→ VPC B (10.1.0.0/16)
```

Non-overlapping CIDRs required. Routes added explicitly. Not transitive (A↔B, B↔C ≠ A↔C).

## Transit Gateway

Hub connecting many VPCs and on-prem. Transitive routing. Cleaner than mesh of peerings.

Pricing: per attachment + per GB.

## VPN

Site-to-site VPN:
- Customer Gateway: on-prem device
- Virtual Private Gateway / TGW: cloud side
- IPSec tunnel

Throughput up to ~1.25 Gbps per tunnel.

## Direct Connect

Dedicated line from your DC to AWS. 1-100 Gbps. Lower latency; predictable.

Cost: $$$ but consistent vs Internet variance.

## Cross-Cloud

| Service | AWS | Azure | GCP |
|---|---|---|---|
| Private network | VPC | VNet | VPC |
| Subnet | Subnet | Subnet | Subnet (regional) |
| Public gateway | IGW | (implicit) | (implicit) |
| Egress NAT | NAT GW | NAT GW | Cloud NAT |
| Inter-VPC | Peering, TGW | VNet peering | VPC peering, Network Connectivity Center |
| To on-prem | VPN, DX | VPN, ExpressRoute | VPN, Interconnect |

GCP VPC: global (subnets per region in one VPC). AWS / Azure: VPC per region.

## IP Address Management

AWS: VPC IPAM for managing IP space across orgs.

Track:
- Allocated CIDRs
- Available
- Documented purpose

Avoid CIDR overlap (blocks peering / VPN).

## DNS

VPC has built-in DNS (`AmazonProvidedDNS`):
- Instances resolve EC2 hostnames
- Resolve public DNS

Route53 Private Hosted Zone: custom internal DNS.

## DHCP Options

Set DNS server, domain name, NTP server for VPC.

## Flow Logs

Capture metadata about traffic:
```
src-ip src-port dst-ip dst-port protocol bytes packets action
```

Use for:
- Security audit
- Debugging
- Cost analysis (where traffic going)

Send to CloudWatch or S3.

## Reachability Analyzer

AWS tool: simulate "can A talk to B"; reports yes/no with reasons (SG, NACL, route, etc.). Saves debugging time.

## Architecture Patterns

### Single VPC
Small app. All in one VPC; subnets split by tier.

### VPC per Environment
dev / staging / prod each isolated. Common.

### VPC per Service
Microservices isolated. Tighter security; harder operations.

### Landing Zone
Org with many accounts; each gets standard VPC. AWS Control Tower automates.

### Hub-and-Spoke
TGW central; many VPCs spokes. Shared services in hub VPC (security, logging).

## Common Mistakes

- Overlapping CIDRs (peering breaks)
- Single AZ (no HA)
- Single NAT (SPOF)
- Public DB
- SG with 0.0.0.0/0 on critical ports
- No flow logs
- Too small CIDR (run out)

## Cost Optimization

- NAT GW expensive: route to S3/DynamoDB via Gateway endpoint
- VPC endpoints for high-traffic services
- Consolidate NAT (one per AZ vs per subnet)
- Right-size VPN/DX

## Limit Watch

Per VPC:
- Route table entries: 50 (raise to 1000)
- Security groups: 2500
- Subnets: 200
- Endpoints: 50

Hit limits at large scale.

## IPv6

Modern: dual-stack. Some services IPv6-only.
- Allocates /56 to VPC
- /64 to subnet
- No NAT needed (each instance has public-routable IPv6)

Adoption growing.

## Interview Prep

**Junior**: "Public vs private subnet."

**Mid**: "VPC design for 3-tier app."

**Senior**: "Cost of NAT — alternatives."

**Staff**: "Multi-account VPC strategy."

## Next Topic

→ [T02 — Load Balancers (L4, L7)](T02-Load-Balancers.md)
