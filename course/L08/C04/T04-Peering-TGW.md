# L08/C04/T04 — VPC Peering vs Transit Gateway

## Learning Objectives

- Connect VPCs
- Pick peering vs TGW

## VPC Peering

Point-to-point connection between two VPCs.

```bash
aws ec2 create-vpc-peering-connection --vpc-id vpc-A --peer-vpc-id vpc-B
# Accept in peer
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-xxx
```

Then add routes:
```
VPC-A route table: VPC-B CIDR → pcx-xxx
VPC-B route table: VPC-A CIDR → pcx-xxx
```

## Constraints

- CIDRs must NOT overlap
- Same or different regions (cross-region peering)
- Same or different accounts
- **Non-transitive**: A↔B, B↔C ≠ A↔C
- DNS: optional cross-VPC DNS resolution

## When Peering

- Small number of VPCs (1-10)
- Bilateral connections
- Need lowest cost (free intra-region; small charge cross-region)

## Limitations

For N VPCs to fully connect: N(N-1)/2 connections.
- 5 VPCs: 10 peerings
- 10 VPCs: 45
- 50 VPCs: 1225 (unmanageable)

Each peering separate config.

## Transit Gateway (TGW)

Hub connecting many VPCs + on-prem.

```bash
aws ec2 create-transit-gateway
aws ec2 create-transit-gateway-vpc-attachment --transit-gateway-id tgw-xxx --vpc-id vpc-A --subnet-ids ...
```

VPC has route to TGW; TGW routes to other attached VPCs.

## TGW Pricing

- $0.05/hour per attachment
- $0.02/GB processed

For 10 VPC attachments: ~$360/mo + traffic.

Peering cheaper but less manageable.

## TGW Features

- Transitive routing (A → B → C through TGW)
- Up to 5000 attachments per TGW
- Multiple route tables (segmentation)
- Cross-region peering (TGW-to-TGW)
- Multicast support
- VPN attachment
- DX attachment
- Direct Connect Gateway integration

## TGW Route Tables

Segment networks:
```
TGW Route Table 1 (prod):
  prod-vpc-A
  prod-vpc-B
  shared-vpc

TGW Route Table 2 (dev):
  dev-vpc-A
  dev-vpc-B
  shared-vpc
```

Prod and dev isolated; both reach shared.

For: env separation, tenant isolation.

## When TGW

- 5+ VPCs
- Need transitive
- Multiple environments
- On-prem connectivity
- Multi-region

## Cross-Region TGW Peering

```bash
aws ec2 create-transit-gateway-peering-attachment \
  --transit-gateway-id tgw-A \
  --peer-transit-gateway-id tgw-B \
  --peer-region us-west-2
```

Connect TGWs across regions. Single hop instead of VPC peering mesh.

## TGW vs Peering Cost

For 10 VPCs intra-region, 1 GB/day each:
- Peering: 45 peerings, $0/hr base, ~$0/data = ~$0
- TGW: 10 attachments × $0.05 × 24 × 30 + 10 × 30 × $0.02 = ~$366/mo

Peering MUCH cheaper for static, intra-region.
TGW better for transit, scale.

## VPC Peering Tips

- Use Name tags on peering connections (default empty)
- Cross-account: requester + accepter agree
- Cross-region: traffic encrypted automatically
- DNS resolution: enable both sides for resolution

## TGW Tips

- Default route tables (association + propagation)
- Custom route tables for segmentation
- VPC must have subnet in each AZ that uses TGW

## Hybrid Connectivity

For on-prem:
- VPN: tgw-vpn attachment
- DX: dx-tgw attachment
- TGW connects on-prem to all VPCs

## Cross-Account TGW

Share TGW via RAM with other accounts:
```bash
aws ram create-resource-share --name shared-tgw --resource-arns arn:aws:ec2:...:transit-gateway/tgw-xxx
```

Other accounts attach their VPCs.

## CloudWAN

AWS managed wide-area network. TGW++ for global multi-region.

For: global enterprise, branch offices, multi-region complex.

Higher cost; more management.

## Routing Inside TGW

TGW attachment can:
- Send routes to TGW (propagation)
- Receive routes from TGW (association)

```
VPC-A:
  Send: vpc-A CIDR to TGW
  Receive: all routes
```

Selective: receive only certain routes.

## Cross-Account Peering

VPC peering across accounts: requester sends request; accepter approves.

```bash
aws ec2 create-vpc-peering-connection --vpc-id vpc-A --peer-vpc-id vpc-B --peer-owner-id OTHER_ACCT
```

Same process; cross-account.

## Limit Watch

VPC Peering:
- 125 active per VPC (raise to 250)
- 50 routes per route table

TGW:
- 5000 attachments per TGW
- 10000 routes per RT
- 50 TGWs per account

## Anti-Patterns

- Full mesh peering for 20+ VPCs (manage chaos)
- TGW for 2 VPCs (overkill cost)
- Forgetting routes on both sides
- Overlapping CIDRs (peering / TGW won't work)

## Best Practices

- TGW for 5+ VPCs or transit
- Peering for 1-1 lightweight
- IP allocation strategy org-wide (no overlap)
- Segment with TGW route tables
- Tag connections clearly
- Monitor TGW data processed (cost)

## Monitoring

CloudWatch TGW metrics:
- BytesIn / BytesOut per attachment
- PacketDropCount

VPC Flow Logs from VPC perspective.

Alert if cost / data anomaly.

## DNS

For cross-VPC name resolution:
- Route53 Private Hosted Zones shared via RAM
- Or each VPC has own DNS; peer for resolution

## Common Mistakes

- Forgetting routes on both ends
- DNS resolution disabled on peering
- TGW attachment without subnet in AZ
- Overlapping CIDRs
- No tagging

## Quick Refs

```bash
# Peering
aws ec2 create-vpc-peering-connection --vpc-id vpc-A --peer-vpc-id vpc-B
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-xxx

# TGW
aws ec2 create-transit-gateway
aws ec2 create-transit-gateway-vpc-attachment --transit-gateway-id tgw-xxx --vpc-id vpc-xxx --subnet-ids ...

# Route to peer
aws ec2 create-route --route-table-id rtb-xxx --destination-cidr-block 10.1.0.0/16 --vpc-peering-connection-id pcx-xxx
```

## Interview Prep

**Mid**: "Peering vs TGW."

**Senior**: "Migrate 20 peerings to TGW."

**Staff**: "Multi-account, multi-region network."

## Next Topic

→ [T05 — PrivateLink & VPC Endpoints (Interface, Gateway)](T05-PrivateLink-Endpoints.md)
