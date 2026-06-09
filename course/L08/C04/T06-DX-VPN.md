# L08/C04/T06 — Direct Connect & Site-to-Site VPN

## Learning Objectives

- Pick between DX and VPN
- Design hybrid connectivity

## Site-to-Site VPN

IPSec tunnel between your DC and AWS.

```
Your DC (Customer Gateway) <-IPSec-> AWS (Virtual Private Gateway or TGW)
```

Over Internet. Encrypted. Sub-Gbps throughput per tunnel.

Setup:
1. Create Customer Gateway (CGW): represents your edge device
2. Create Virtual Private Gateway (VGW) or use TGW
3. Create Site-to-Site VPN connection: 2 tunnels (HA)
4. Configure your CGW with parameters AWS provides

```bash
aws ec2 create-customer-gateway --type ipsec.1 --public-ip 1.2.3.4 --bgp-asn 65000
aws ec2 create-vpn-gateway --type ipsec.1
aws ec2 create-vpn-connection --customer-gateway-id cgw-xxx --vpn-gateway-id vgw-xxx --type ipsec.1
```

Each connection has 2 tunnels (in different AZs).

## VPN Pricing

- $0.05/hour per connection
- $0.05/GB out (egress)

~$40/mo + traffic.

## VPN Throughput

Per tunnel: up to 1.25 Gbps.
Per connection (2 tunnels): up to 2.5 Gbps theoretical; in practice ~1-2 Gbps real.

For more: multiple connections.

## VPN HA

2 tunnels in different AZ-equivalents. CGW should support both endpoints.

For higher HA: 2 CGWs on your side.

## BGP vs Static

BGP routing: dynamic; failover automatic.
Static routing: manual.

BGP preferred.

## Direct Connect (DX)

Dedicated fiber from your DC to AWS partner location.

- 1, 10, 100 Gbps
- Lower latency than VPN
- More predictable
- Not over Internet

Setup:
1. Order from AWS or partner
2. Cross-connect at colo
3. Configure router (BGP)
4. Create Virtual Interface (VIF):
   - Private VIF: to VPC via VGW or DX Gateway
   - Public VIF: to AWS public services
   - Transit VIF: to TGW

## DX Pricing

Port charges:
- 1 Gbps: ~$220/mo
- 10 Gbps: ~$1700/mo

Plus data transfer (cheaper than Internet):
- $0.02/GB outbound

Cross-connect from colo: extra fee.

## DX vs VPN

| | VPN | DX |
|---|---|---|
| Setup time | Hours | Weeks-months |
| Cost | $40/mo | $200-2000/mo |
| Throughput | <2 Gbps | Up to 100 Gbps |
| Latency | Variable | Consistent low |
| Reliability | Internet-dependent | Provider SLA |
| Encryption | Yes (IPSec) | No (use MACsec) |
| Use | Bursty / dev / backup | Production heavy / consistent |

## DX with VPN Backup

Use VPN as backup for DX (extra cost; instant failover).

## DX Gateway

Connects DX to multiple VPCs in multiple regions:
```
DX VIF → DX Gateway → many VPCs / regions
```

Avoids per-VPC private VIF.

For multi-region: DX Gateway + TGW.

## DX SiteLink

Multiple DX locations communicate via AWS backbone (faster than your provider).

For: global enterprises with multiple offices.

## Public VIF

Access AWS public IPs over DX (instead of Internet):
- S3
- DynamoDB
- Public Lambda endpoints

Save Internet egress; better latency.

## CloudHub

Old hub-and-spoke VPN. Mostly deprecated; use TGW.

## VPN to TGW

Modern: VPN attaches to TGW (not VGW). Routes to all attached VPCs.

```bash
aws ec2 create-transit-gateway-vpn-attachment ...
```

## DX to TGW

Transit VIF + DX Gateway + TGW.

```
On-prem → DX → DX Gateway → TGW → VPCs
```

## On-Prem to AWS Patterns

### VPN (Quick)
For: dev, small scale, lift-and-shift.

### DX (Production)
For: heavy traffic, latency-sensitive, regulated.

### DX + VPN Backup
For: max availability.

### Multi-DX
For: multi-region, redundancy.

### SD-WAN Overlay
Customer SD-WAN with cloud-onramps.

## BGP

Border Gateway Protocol: dynamic routing.

You advertise: your CIDRs to AWS.
AWS advertises: VPC CIDRs to you.

Best path selected; failover automatic if path drops.

## ASN

Autonomous System Number for BGP:
- Public ASN (if you have)
- Private ASN range 64512-65534 (most use)

AWS uses 64512 for VGW by default.

## Hybrid DNS

For DNS across:
- Route53 Resolver: forward queries between VPC and on-prem
- Outbound endpoints (resolve on-prem from VPC)
- Inbound endpoints (resolve VPC from on-prem)

```bash
aws route53resolver create-resolver-endpoint --direction OUTBOUND ...
```

## DX Speed Options

Available speeds:
- Dedicated: 1, 10, 100 Gbps (you order port; full bandwidth)
- Hosted: 50 Mbps to 25 Gbps (from partner; sub-port; cheaper)

Hosted: easier, smaller commitment. Dedicated: bigger orgs.

## Connection HA Best Practice

For DX critical: 2 dedicated connections in different colos.

Or: 1 DX + VPN backup.

## Latency

DX latency to AWS region: 1-10 ms typical (depends on distance to colo + AWS endpoint).

VPN latency: 10-100 ms (Internet-dependent).

For low-latency apps: DX matters.

## MACsec

Layer 2 encryption on DX (10/100 Gbps connections). For compliance.

## DX Locations

100s of partner colos worldwide. Choose one near your DC.

## Costs

DX Setup:
- Port fee
- Cross-connect (colo charge; varies)
- Data egress (cheaper than Internet)

VPN setup:
- Connection hourly
- Egress

## Common Mistakes

- VPN for high traffic (saturated)
- DX without redundancy (SPOF)
- Static routes everywhere (use BGP)
- DX overlapping CIDRs
- Forgetting cross-connect fees

## Best Practices

- BGP over static
- Dual tunnels (VPN HA)
- Dual DX for production
- DX + VPN backup
- DNS resolver for hybrid
- Monitor tunnel health

## Quick Refs

```bash
# VPN
aws ec2 create-customer-gateway --type ipsec.1 --public-ip 1.2.3.4 --bgp-asn 65000
aws ec2 create-vpn-connection --customer-gateway-id cgw-xxx --vpn-gateway-id vgw-xxx --type ipsec.1

# DX
aws directconnect create-connection --location EqDA2 --bandwidth 1Gbps --connection-name my-dx
```

## Interview Prep

**Mid**: "VPN vs DX."

**Senior**: "Hybrid network design."

**Staff**: "Multi-region multi-DC connectivity."

## Next Topic

→ [T07 — Egress Controls & Centralized Egress](T07-Egress-Controls.md)
