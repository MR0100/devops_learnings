# L09/C04/T04 — Networking Equivalents

## Learning Objectives

- Map networking
- Choose per use case

## VPC / Network

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | VPC | VPC | VNet |
| Scope | Regional | Global | Regional |
| Subnets | Per-AZ | Regional | Regional |
| CIDR | Multiple per VPC | Multiple per VPC | One primary + secondary |

## Firewall / Security

| | AWS | GCP | Azure |
|---|---|---|---|
| Stateful, instance | Security Group | VPC Firewall (VPC-level) | NSG |
| Stateless, subnet | NACL | (no direct) | NSG (also at subnet) |
| Hierarchical | (SCP for accts) | Hierarchical FW | Azure Policy / Firewall Manager |
| Managed FW | Network Firewall | Cloud Firewall | Azure Firewall |
| WAF | WAF | Cloud Armor | WAF (Front Door / App GW) |

## Load Balancer

| | AWS | GCP | Azure |
|---|---|---|---|
| L4 (TCP/UDP) | NLB | Network LB (regional/global) | LB |
| L7 (HTTP) | ALB | Application LB (regional/global) | App Gateway |
| Global L7 | CloudFront + ALB | Global Application LB | Front Door |
| Cross-region L4 | Global Accelerator | Global Network LB | Traffic Manager |

## CDN

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | CloudFront | Cloud CDN | Azure CDN / Front Door |
| Origins | S3, ALB, custom | LB, GCS, custom | Storage, LB, custom |
| Edge compute | Lambda@Edge, CloudFront Functions | Cloud CDN + Cloud Functions | Front Door Rules |

## DNS

| | AWS | GCP | Azure |
|---|---|---|---|
| Public DNS | Route 53 | Cloud DNS | Azure DNS |
| Private DNS | Route 53 PHZ | Cloud DNS Private Zone | Private DNS Zone |
| Traffic | Route 53 (latency, geo) | Traffic Director | Traffic Manager |
| GSLB | Route 53 / Global Accelerator | Traffic Director | Front Door / Traffic Manager |

## NAT

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | NAT Gateway | Cloud NAT | NAT Gateway |
| Source NAT for VMs | yes | yes | yes |

## Private Connect

| | AWS | GCP | Azure |
|---|---|---|---|
| Service Access | VPC Endpoint (Interface) | Private Service Connect | Private Endpoint |
| S3-like (bucket) | VPC Endpoint (Gateway) | (no direct) | Service Endpoint |

For: accessing PaaS without Internet.

## Peering

| | AWS | GCP | Azure |
|---|---|---|---|
| VPC peering | yes | yes | VNet peering |
| Cross-region | yes | yes (global VPC) | yes |
| Transitive | no | no | no |

For transitive: Transit Gateway / SDN / VWAN.

## Transit / Hub

| | AWS | GCP | Azure |
|---|---|---|---|
| Hub | Transit Gateway | Network Connectivity Center | Virtual WAN |
| Cloud WAN | Cloud WAN | NCC | VWAN |

For: many VPCs/regions.

## VPN

| | AWS | GCP | Azure |
|---|---|---|---|
| Site-to-Site | Site-to-Site VPN | Cloud VPN | VPN Gateway |
| Client VPN | Client VPN | (3rd party) | VPN Gateway (P2S) |

## Direct Connect

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Direct Connect | Cloud Interconnect | ExpressRoute |
| Sizes | 50 Mbps - 100 Gbps | 10/100 Gbps | 50 Mbps - 100 Gbps |
| Partners | yes | Partner Interconnect | ExpressRoute Direct/Partner |

## Cross-Cloud

- Via Megaport / Equinix Fabric
- Via 3rd party SD-WAN (Aviatrix)
- Via Internet + VPN

For high-bandwidth: fabric.

## DDoS

| | AWS | GCP | Azure |
|---|---|---|---|
| Basic (free) | Shield Standard | Cloud Armor (always) | Basic DDoS (free) |
| Advanced | Shield Advanced | Cloud Armor Premium | DDoS Protection Standard |

## WAF

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | WAF | Cloud Armor | WAF (on Front Door / App GW) |
| Managed rules | yes | yes | yes |
| Bot mgmt | yes | yes | yes |
| Rate limit | yes | yes | yes |

## Anycast IPs

| | AWS | GCP | Azure |
|---|---|---|---|
| Anycast | Global Accelerator | Global LB | Front Door, Cross-region LB |

For: single IP, global routing.

## Service Mesh

All clouds support Istio / Linkerd on K8s.

### Managed
- AWS: App Mesh (deprecating); recommend Istio
- GCP: Anthos Service Mesh (Istio)
- Azure: Open Service Mesh (deprecated); recommend Istio

For: standard Istio with K8s.

## Cilium

eBPF-based CNI; works on all clouds.

For: high-performance K8s networking.

## DNS Routing

Across clouds:
- Route 53 health checks → failover to other cloud
- Cloud DNS + Traffic Director
- Azure Traffic Manager

For: multi-cloud HA.

## CDN Pricing

| | AWS CloudFront | GCP Cloud CDN | Azure CDN |
|---|---|---|---|
| Pricing | Per GB + per request | Per GB cache fill + egress | Per GB |
| Free tier | 1 TB | (limited) | (limited) |

For: CDN often cheaper than direct origin egress.

## Best Practices

- Same patterns: VPC + subnets + NAT
- Private connectivity over Internet
- WAF + DDoS for public
- CDN for static
- DNS for failover
- Transit / hub for many VPCs
- Direct Connect for hybrid

## Common Mistakes

- Overlapping CIDRs (peering breaks)
- No WAF on public
- No DDoS plan
- Public DB endpoints
- Single VPN tunnel (no HA)

## Quick Refs

```
VPC: VPC / VPC / VNet
Subnets: per-AZ / regional / regional
SG/Firewall: SG / FW rule / NSG
LB L7: ALB / App LB / App GW
LB L4: NLB / Network LB / LB
Global L7: CloudFront / Global App LB / Front Door
CDN: CloudFront / Cloud CDN / Azure CDN
DNS: Route 53 / Cloud DNS / Azure DNS
NAT: NAT GW / Cloud NAT / NAT GW
VPN: VPN GW / Cloud VPN / VPN GW
DX: Direct Connect / Interconnect / ExpressRoute
WAF: WAF / Cloud Armor / WAF
```

## Interview Prep

**Junior**: "Map networking services."

**Mid**: "LB types per cloud."

**Senior**: "Multi-region networking."

**Staff**: "Multi-cloud network architecture."

## Next Topic

→ Move to [L11 — Configuration Management](../../L11/README.md)
