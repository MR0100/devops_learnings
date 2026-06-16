# L09/C03/T02 — Cross-Cloud Connectivity

## Learning Objectives

- Connect clouds
- Pick the right approach

## Options

1. Internet (encrypted)
2. VPN
3. Cloud-to-cloud direct (Megaport, Equinix)
4. Network appliance / SD-WAN
5. Service mesh

## Internet

```
AWS EC2 → Public IP → Internet → GCS public endpoint
```

Cheapest; high latency variance; security concerns.

For: dev, batch, non-critical.

## VPN

Site-to-site IPSec:
```
AWS VPN Gateway ↔ GCP Cloud VPN
                ↔ Azure VPN Gateway
```

Throughput: ~1.25 Gbps per tunnel.

For: low-volume, secure.

## Megaport / Equinix Fabric

Hosted cross-cloud:
```
AWS Direct Connect → Megaport ← Azure ExpressRoute / GCP Interconnect
```

Single fabric routes between clouds.

For: high-bandwidth, low-latency.

## SD-WAN

VPN appliances (Cisco, Aviatrix, etc.) deployed in each cloud:
```
AWS SD-WAN ↔ GCP SD-WAN ↔ Azure SD-WAN
```

Centralized network management.

For: enterprise.

## Service Mesh

Istio / Linkerd with multi-cluster:
- mTLS across clouds
- Service discovery
- Failover

For: app-level cross-cloud.

## Aviatrix

Specialist multi-cloud networking:
- Single pane of glass
- Aviatrix gateways in each cloud
- Automated routing

For: complex enterprise.

## Cloud-Native Cross-Connect

Some direct:
- Azure ExpressRoute Direct → AWS Direct Connect (via Megaport)
- GCP Partner Interconnect → similar

For: 10/100 Gbps dedicated.

## Latency

| Path | Latency |
|---|---|
| Same region cross-cloud (via Megaport) | <5 ms |
| Cross-region cross-cloud | 50-200 ms |
| VPN over Internet | 50-300 ms |
| Internet (direct) | varies |

For latency-critical: same-region peering via fabric.

## Costs

- Egress (always): $0.05-0.12/GB out of cloud
- VPN: cheap
- Direct Connect / ExpressRoute / Interconnect: hourly + per GB
- Megaport / Equinix: subscription + transit

For: egress dominates. Minimize.

## Egress Trap

```
$ AWS S3 → GCS:
  $0.09/GB out of AWS S3
```

For 100 TB: $9000.

Mitigations:
- Cache aggressively
- Avoid cross-cloud transfer
- Use Storage Transfer Service
- Compress

## CIDR Planning

Across clouds:
```
AWS:    10.0.0.0/12
Azure:  10.16.0.0/12
GCP:    10.32.0.0/12
```

No overlap; future-proof for peering.

## DNS

Cross-cloud DNS:
- External Route 53 / Cloud DNS / Azure DNS
- Or shared DNS (CoreDNS in K8s)

Service in AWS:
```
my-svc.internal.aws.example.com → ALB
```

Service in GCP:
```
my-svc.internal.gcp.example.com → LB
```

## Service Discovery

Across clouds:
- Consul (HashiCorp)
- Service mesh (Istio multi-cluster)
- DNS-based

For K8s: Linkerd multi-cluster or Istio.

## Authentication

Across clouds:
- mTLS (service mesh)
- JWT (signed by central IdP)
- WIF / OIDC federation

For: zero trust across clouds.

## Topologies

### Hub-and-Spoke
Central hub (e.g. on-prem or one cloud) connects to spokes.

### Mesh
Every cloud connects to every other.

### Transit Cloud
One cloud as transit (Azure VWAN, AWS Transit Gateway).

For: depends on scale.

## Examples

### Multi-Region SaaS
US: AWS us-east + Azure eastus.
EU: AWS eu-west + Azure westeurope.

Connected via Megaport.

### Hybrid Analytics
On-prem data → AWS for storage → GCP for BigQuery.

Cloud-to-cloud via Storage Transfer.

### Cross-Cloud DR
Primary: AWS.
DR: GCP.

Connected via VPN + replication.

## Tools

- Aviatrix: cross-cloud networking + visibility
- Alkira: similar
- Cisco Cloud OnRamp
- Megaport / Equinix fabric

## Real-World Issues

- BGP route filtering
- MTU mismatches
- NAT translation
- Encryption overhead
- Asymmetric routing
- Cost spikes (egress)

For: monitor + bandwidth alerts.

## Best Practices

- Plan CIDRs to never overlap
- Megaport for high-bandwidth low-latency
- VPN for backup / low-volume
- Service mesh for app-level
- Monitor egress costs
- Tag traffic for cost visibility
- Test failover

## Common Mistakes

- Overlapping CIDRs (peering fails)
- Internet for prod data (insecure, slow)
- No egress monitoring (bill shock)
- VPN for hot-path traffic
- Single tunnel (no HA)

## Quick Refs

```
Latency-critical: Megaport / direct
Low-volume: VPN
Migration: Storage Transfer
Real-time app traffic: service mesh + direct
```

## Interview Prep

**Mid**: "Cross-cloud options."

**Senior**: "Connectivity architecture for hybrid."

**Staff**: "Multi-cloud networking at FAANGM scale."

## Next Topic

→ [T03 — Cross-Cloud IAM Federation](T03-Cross-Cloud-IAM.md)
