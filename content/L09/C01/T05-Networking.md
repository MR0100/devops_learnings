# L09/C01/T05 — Networking (VNets, NSGs, Application Gateway, Front Door)

## Learning Objectives

- Build Azure networks
- Compare to AWS VPC

## VNet

Virtual Network = VPC:
```bash
az network vnet create \
  --resource-group myrg \
  --name myvnet \
  --address-prefix 10.0.0.0/16 \
  --subnet-name web --subnet-prefix 10.0.1.0/24
```

Subnets within VNet (regional).

## Differences vs AWS VPC

- VNets are **regional** like VPCs
- Subnets are **regional** (vs AWS subnets per-AZ)
  - Azure handles AZ distribution per resource
- One default route table per subnet
- No default IGW (Internet via load balancer or NAT or public IP)

## NSG (Network Security Group)

= SG / NACL:
```bash
az network nsg create --resource-group myrg --name mynsg
az network nsg rule create --nsg-name mynsg --resource-group myrg \
  --name allow-https --priority 100 \
  --source-address-prefixes Internet \
  --destination-port-ranges 443 \
  --access Allow --protocol Tcp
```

Stateful (like AWS SG).

Apply at:
- NIC
- Subnet

## NSG Priorities

Lower number = higher priority.
Range: 100-4096.

Default rules at 65000+ (allow VNet, deny Internet inbound).

## Application Security Groups (ASG)

Logical grouping of NICs:
```bash
az network asg create --resource-group myrg --name web-asg
# Assign NIC
az network nic update --name mynic --resource-group myrg --add ipConfigurations[0].applicationSecurityGroups id=/.../web-asg

# Use in NSG rule
az network nsg rule create --source-asg web-asg --destination-asg db-asg ...
```

For: app-tier-based rules; like AWS SG references.

## Public IP

```bash
az network public-ip create --resource-group myrg --name mypip --sku Standard
```

For: VM, LB, App Gateway.

SKUs:
- **Basic**: legacy
- **Standard**: AZ-aware; better SLA

## Internet Access

Outbound options:
1. **NAT Gateway**: managed NAT
2. **LB outbound rules**: via LB
3. **Public IP on VM**: each VM gets own
4. **Default outbound**: deprecating; explicit needed

## NAT Gateway

```bash
az network nat gateway create \
  --resource-group myrg --name mynat \
  --public-ip-addresses mypip
```

Attach to subnet:
```bash
az network vnet subnet update \
  --vnet-name myvnet --name web --resource-group myrg \
  --nat-gateway mynat
```

For: subnet outbound.

## VNet Peering

```bash
az network vnet peering create \
  --resource-group myrg --name peer-a-b \
  --vnet-name vnet-a \
  --remote-vnet vnet-b --allow-vnet-access
```

For: cross-VNet (regions, accounts).

## Hub-Spoke

```
Hub VNet
├─ ExpressRoute / VPN Gateway
├─ Firewall
├─ DNS resolver
└─ Bastion

Spokes (peered):
├─ Spoke 1 (app A)
├─ Spoke 2 (app B)
└─ Spoke 3 (shared services)
```

Standard architecture for enterprise.

## Azure Virtual WAN

Managed hub-spoke at scale:
- Cross-region
- ExpressRoute
- VPN
- Routing

For: large multi-region.

## ExpressRoute

= AWS Direct Connect:
- Private connection on-prem ↔ Azure
- Bypasses Internet
- Up to 100 Gbps

For: dedicated bandwidth.

## VPN Gateway

= AWS VPN:
- Site-to-site (S2S)
- Point-to-site (P2S; user VPN)
- IPsec / IKEv2

## Load Balancer (L4)

```bash
az network lb create \
  --resource-group myrg \
  --name mylb \
  --sku Standard \
  --public-ip-address mypip
```

L4: TCP / UDP. = AWS NLB.

## Application Gateway (L7)

```bash
az network application-gateway create \
  --resource-group myrg \
  --name myag \
  --location eastus \
  --vnet-name myvnet --subnet ag-subnet \
  --public-ip-address mypip \
  --sku WAF_v2 --capacity 2
```

L7: HTTP/HTTPS, path-based routing, WAF.

= AWS ALB + WAF.

## Front Door

Global L7:
- Multi-region
- Anycast
- WAF
- CDN
- Edge

= AWS CloudFront + ALB + WAF + Route 53.

```bash
az afd profile create --profile-name myfd --resource-group myrg --sku Standard_AzureFrontDoor
```

For: global apps.

## Traffic Manager

DNS-based load balancing:
- Geographic
- Performance
- Priority

Like AWS Route 53 latency-based.

For: simple multi-region.

## Private DNS

```bash
az network private-dns zone create --resource-group myrg --name myorg.internal
az network private-dns link vnet create --resource-group myrg --zone-name myorg.internal --name mylink --virtual-network myvnet --registration-enabled true
```

For: internal DNS.

## Azure DNS (Public)

```bash
az network dns zone create --resource-group myrg --name example.com
az network dns record-set a add-record --resource-group myrg --zone-name example.com --record-set-name www --ipv4-address 1.2.3.4
```

= Route 53.

## Bastion

Browser-based VM access:
- No public IP on VM
- SSH/RDP via Azure portal
- No bastion host to manage

```bash
az network bastion create --resource-group myrg --name mybastion --vnet-name myvnet --public-ip-address mypip
```

For: secure VM access.

## Firewall

Managed L4-L7:
- Stateful inspection
- Threat intel
- TLS inspection (premium)

```bash
az network firewall create --resource-group myrg --name myfw
```

For: centralized network security.

## Service Endpoints / Private Endpoints

### Service Endpoints
Extend VNet identity to Azure services. Free.

```bash
az network vnet subnet update --vnet-name myvnet --name web \
  --service-endpoints Microsoft.Storage
```

### Private Endpoints
Private IP for Azure service in VNet. NIC.

```bash
az network private-endpoint create ...
```

For: bypass Internet to access Azure PaaS.

## DDoS Protection

Standard:
- Always-on monitoring
- Tuned per workload
- Cost protection

For: public-facing.

## Network Watcher

Monitoring:
- Topology
- IP flow verify
- Packet capture
- NSG flow logs

```bash
az network watcher show --resource-group myrg --name mywatcher
```

## Comparison to AWS

| Azure | AWS |
|---|---|
| VNet | VPC |
| NSG | Security Group |
| ASG | SG referencing |
| App Gateway | ALB |
| Load Balancer | NLB |
| Front Door | CloudFront + R53 + ALB + WAF |
| Traffic Manager | R53 (advanced routing) |
| VPN Gateway | VPN |
| ExpressRoute | Direct Connect |
| Bastion | Session Manager / Bastion |
| Firewall | Network Firewall |
| Private Endpoint | PrivateLink |
| Service Endpoint | VPC Endpoint (Gateway) |

## CIDR Planning

```
Hub:     10.0.0.0/16
Prod:    10.1.0.0/16
Staging: 10.2.0.0/16
Dev:     10.3.0.0/16
```

Avoid overlap across peers.

## Best Practices

- Hub-Spoke for enterprise
- NSG at subnet (broader); ASG for app-tier
- Private Endpoints for PaaS
- NAT Gateway not default outbound
- Bastion (no public VM IPs)
- DDoS Standard for public
- NSG flow logs (audit)

## Common Mistakes

- Default outbound (deprecating)
- Public IPs on VMs (use bastion)
- Overlapping CIDRs (peering breaks)
- No DDoS protection
- NSG on NIC only (forget subnet level)

## Quick Refs

```bash
# VNet
az network vnet / subnet
# NSG
az network nsg / nsg rule
# LB
az network lb
az network application-gateway
# Front Door
az afd profile

# Connectivity
az network vnet peering
az network vpn-gateway
```

## Interview Prep

**Junior**: "VNet basics."

**Mid**: "App Gateway vs LB vs Front Door."

**Senior**: "Hub-Spoke design."

**Staff**: "Enterprise Azure network architecture."

## Next Topic

→ [T06 — Bicep & ARM Templates](T06-Bicep-ARM.md)
