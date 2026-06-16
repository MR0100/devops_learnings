# L03/C07/T02 — VPC Peering vs Transit Gateway

## Learning Objectives

- Choose between VPC peering, TGW, and PrivateLink
- Understand transitive routing limitations
- Design hub-and-spoke at scale

## VPC Peering

Direct connection between TWO VPCs.

- 1:1
- Cross-account or cross-region
- Same or different region
- Non-transitive (A↔B and B↔C does NOT enable A↔C)
- CIDR cannot overlap
- Free; you pay only for data transfer

```hcl
resource "aws_vpc_peering_connection" "main" {
  vpc_id      = aws_vpc.a.id
  peer_vpc_id = aws_vpc.b.id
  peer_region = "us-west-2"   # cross-region
}
```

Add routes on each side:
```
A's route table: B's CIDR → peering connection ID
B's route table: A's CIDR → peering connection ID
```

## Transit Gateway (TGW)

Hub-and-spoke router for many VPCs.

- Transitive routing
- Up to 5,000 attachments
- Cross-account, cross-region (via peering attachment)
- Route tables on TGW for segmentation
- $0.05/hr per attachment + $0.02/GB processed

```
        ┌──────────────────┐
        │  Transit Gateway │
        └────┬───┬───┬─────┘
             │   │   │
         VPC A VPC B VPC C ... + On-Prem (DX/VPN)
```

### TGW Route Tables
- Default route table (or custom)
- Each attachment associates with one RT
- Each attachment propagates to one or many RTs

Enables segmentation: prod VPCs talk to each other; dev VPCs separate.

### TGW Connectivity Patterns

- **Flat**: all VPCs in same RT (simple, less secure)
- **Segmented**: prod RT + non-prod RT
- **Spoke-to-Egress**: spokes route through TGW to centralized egress
- **Inspection**: traffic through a firewall VPC for security

## PrivateLink

Expose service in one VPC to another without peering.

- Producer: NLB
- Endpoint service in producer VPC
- Consumer: Interface VPC Endpoint (ENI)
- One-way (consumer → producer)
- No CIDR conflict possible (traffic terminates at ENI)
- Cross-account, cross-region

```
Consumer VPC                   Producer VPC
  ENI (private IP) ─── PrivateLink ─── NLB ─── Service
```

Use case: SaaS provider; internal shared service.

## When Which

| Need | Use |
|---|---|
| 2 VPCs connect, simple | Peering |
| 5+ VPCs, hub-and-spoke | TGW |
| Hybrid (on-prem + VPC) | TGW with DX/VPN attachments |
| Cross-region many VPCs | TGW peering between TGWs |
| Producer/consumer with isolation | PrivateLink |
| CIDR overlap problem | PrivateLink |
| One-way service access | PrivateLink |

## Routing Pattern Cost Comparison

### Peering (2 VPCs)
- Free attachment
- Data: cross-region rates if applicable

### TGW (5+ VPCs)
- $50/attachment/mo (5 VPCs ≈ $250/mo)
- $0.02/GB processed
- Worth it for transitive routing and centralization

### PrivateLink
- $0.01/hr per AZ per endpoint
- $0.01/GB processed
- Costs more than peering for high-traffic; less than full VPC peering setup

## Cross-Region

### Peering
- Direct cross-region; no extra service
- Uses AWS backbone
- $0.02/GB cross-region transfer

### TGW Peering
- Connect TGWs in different regions
- Pay for both TGW attachments + cross-region transfer
- Used for global mesh

## Transitive Routing

Peering: A↔B, B↔C, but A cannot reach C through B.
TGW: A↔TGW↔B, A↔TGW↔C, A reaches C through TGW.

## Common Mistakes

- **CIDR overlap**: causes ambiguous routing
- **Missing route table updates**: peering / TGW attached but no traffic
- **Security groups don't span peering**: need IP rules or use shared SG via attachment
- **Asymmetric routing**: A sends through peering; reply through different path
- **TGW route limits**: 10,000 routes per RT; large estates need careful design

## Sample Design (Large Org)

```
Network Account
├── TGW (regional)
│   ├── Spoke Attachments: prod-* VPCs
│   ├── Spoke Attachments: nonprod-* VPCs
│   ├── Egress VPC Attachment
│   ├── Inspection VPC Attachment
│   ├── DX Gateway Attachment (on-prem)
│   └── Cross-Region TGW Peering
└── Route tables:
    ├── Spoke RT: routes 0/0 to egress + inspection
    ├── Prod RT: prod VPCs see each other only
    └── NonProd RT: nonprod VPCs see each other only
```

## Hybrid Connectivity

### Direct Connect
Physical link between on-prem and AWS.
- DX gateway can connect to TGW
- 1/10/100 Gbps options

### Site-to-Site VPN
IPSec over Internet.
- Lower cost; lower bandwidth (max 1.25 Gbps per tunnel)
- Often used as DX backup

## Operations

```bash
# List peering
aws ec2 describe-vpc-peering-connections

# TGW routes
aws ec2 describe-transit-gateway-route-tables
aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id tgw-rtb-... --filters Name=type,Values=static
```

## Best Practices

- **Default to TGW once you pass ~3 VPCs** — the per-VPC route-table sprawl and the non-transitive limitation of peering make a mesh unmanageable; TGW gives transitive routing and segmentation in one place.
- Keep **non-overlapping CIDRs across everything** that might ever connect; where overlap is unavoidable (M&A, SaaS), use **PrivateLink**, which terminates at an ENI and sidesteps routing entirely.
- **Segment with TGW route tables** (prod RT vs non-prod RT, plus a spoke RT pointing `0.0.0.0/0` at an inspection/egress VPC) instead of one flat table.
- Own the network from a **dedicated network account** and define attachments/route tables in IaC so changes are reviewed, not click-ops.
- For one-way "expose a service" use cases, prefer **PrivateLink over peering** — the consumer gets a single ENI, no CIDR coordination, and no broad network reachability.
- **Update both sides' route tables and security groups** as one change; SGs don't follow peering, so reference CIDRs (or use TGW-aware referencing) explicitly.

## Quick Refs

| Need | Use |
|---|---|
| 2 VPCs, simple, lowest cost | **Peering** (free attach, non-transitive) |
| Many VPCs, hub-and-spoke, segmentation | **Transit Gateway** |
| Expose one service, one-way, isolation | **PrivateLink** |
| CIDRs overlap | **PrivateLink** (terminates at ENI) |
| Hybrid (on-prem + VPCs) | **TGW** + DX/VPN attachments |
| Many VPCs across regions | **TGW peering** between regional TGWs |

Cost shape: Peering = free attachment + data transfer · TGW = ~$0.05/hr per attachment + $0.02/GB · PrivateLink = ~$0.01/hr per AZ per endpoint + $0.01/GB.

```bash
# Peering connections
aws ec2 describe-vpc-peering-connections \
  --query 'VpcPeeringConnections[].{Id:VpcPeeringConnectionId,Status:Status.Code}'

# TGW attachments and what RT they associate with
aws ec2 describe-transit-gateway-attachments
aws ec2 get-transit-gateway-route-table-associations --transit-gateway-route-table-id tgw-rtb-...

# PrivateLink: endpoint services and consumer endpoints
aws ec2 describe-vpc-endpoint-service-configurations
aws ec2 describe-vpc-endpoints
```

Remember: **peering is non-transitive** (A↔B, B↔C does *not* give A↔C); **TGW is transitive** through the hub.

## Interview Prep

**Mid**: "Peering vs TGW."

**Senior**: "Design for 50+ VPCs."

**Staff**: "Centralized egress via TGW — design."

## Next Topic

→ [T03 — Direct Connect & Site-to-Site VPN](T03-Direct-Connect-VPN.md)
