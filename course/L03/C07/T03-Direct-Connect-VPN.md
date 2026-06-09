# L03/C07/T03 — Direct Connect & Site-to-Site VPN

## Learning Objectives

- Choose between DX and VPN
- Understand BGP for hybrid
- Plan resilience

## Direct Connect (DX)

Dedicated fiber from on-prem (or colo) to AWS.

- Bandwidth: 1, 10, 100 Gbps
- Lower, consistent latency than Internet
- Lower egress costs (~$0.02/GB vs $0.09/GB Internet)
- Setup time: weeks (physical install)

### Variants
- **Dedicated**: full port; you order from AWS
- **Hosted**: from a partner; share their port

### Direct Connect Locations
~100 globally. You bring (or rent) a router in the location; cross-connect to AWS port.

### Virtual Interface (VIF)
A logical connection on top of physical port:
- **Private VIF**: connects to a single VPC
- **Public VIF**: access to AWS public services (S3, etc.) without traversing Internet
- **Transit VIF**: connects to Transit Gateway (multiple VPCs)

### Direct Connect Gateway (DX GW)
- Global; connects DX VIFs to TGWs in multiple regions
- One DX → multiple regions

## VPN (Site-to-Site)

IPSec tunnel over Internet.

- Cheaper than DX
- Slower setup (configure firewall on-prem; AWS endpoint)
- Up to 1.25 Gbps per tunnel
- Two tunnels per connection for HA

### AWS Side
- VPN Gateway (attached to VPC)
- OR TGW VPN attachment

### On-Prem Side
- Customer Gateway: your router (Cisco, Juniper, Palo Alto, etc.)
- Pre-shared key (or certificate-based)

### BGP for VPN
Recommended:
- Dynamic routing
- Advertise prefixes
- Faster failover

Static routing is supported but less flexible.

## When DX vs VPN

| Need | DX | VPN |
|---|---|---|
| Bandwidth > 1.25 Gbps | Yes | No |
| Consistent low latency | Yes | No |
| Cost | Higher upfront | Pay as you go |
| Setup time | Weeks | Hours |
| Internet outage tolerance | Doesn't matter | Affected |

Common pattern: DX as primary; VPN as backup.

## DX Resilience

- Single port: outage = down
- Multiple ports (different DX locations): resilient
- Multiple AWS regions: AWS handles internal failover
- Active/Active with BGP

## Bandwidth Per Connection

```
1 Gbps port → max 1 Gbps
10 Gbps → can split across multiple VIFs
100 Gbps → premium tier
```

For more bandwidth: LAG (Link Aggregation Group) bundles multiple ports.

## Egress Cost

| Path | Cost |
|---|---|
| AWS → Internet | $0.09/GB (first 10TB tier) |
| AWS → DX (private VIF) | $0.02/GB |
| AWS → DX (public VIF) | $0.02/GB (still cheaper) |
| AWS → VPN | $0.05/GB (over Internet) |

For high egress (DBs replicating to on-prem, etc.), DX pays for itself.

## Operating

### Monitoring
- CloudWatch metrics: ConnectionBpsEgress, ConnectionBpsIngress
- BGP session state
- VIF state

### Alerts
- BGP session down
- High utilization (> 70%)
- Tunnel down

## VPN Performance

For higher bandwidth:
- VPN with Equal-Cost Multi-Path (multiple tunnels)
- Up to ~1.25 Gbps per tunnel × multiple = aggregate

But still less consistent than DX.

## Failover Strategies

### DX with VPN Backup
- DX primary (lower cost path)
- VPN ready; BGP routes shift if DX down
- AS-PATH prepending or MED to prefer DX

### DX Multi-Site
- Two DX locations
- Different DX providers
- Bidirectional Forwarding Detection (BFD) for fast detection

## Resilience Patterns

```
Single DX                  No redundancy (one outage = down)
Two DX same location       Some HW resilience
Two DX different locations Better
Two DX + VPN backup        Best (most teams)
```

## Common Issues

- **Single point of failure**: cross-connect at DX location
- **Maintenance windows**: AWS notifies; plan
- **Asymmetric routing**: BGP misconfig leads to flow trapped
- **Latency creep**: route changes increase RTT
- **Bandwidth saturation**: no headroom for spikes

## Hybrid Architecture Examples

### Database Replication
On-prem Oracle → AWS DynamoDB via DMS over DX. Real-time CDC.

### Backup
On-prem files to S3 over DX. High throughput.

### Migrations
Lift-and-shift: app on-prem; DB on AWS. Latency matters; use DX.

### Hybrid Apps
Some services on-prem, some in cloud. DX for service-to-service.

## Multi-Cloud / Inter-Cloud

For AWS ↔ GCP / Azure:
- Through Internet (expensive)
- Through DX provider that supports multiple clouds (Megaport, Equinix Fabric)
- Configure private peering

## Interview Prep

**Mid**: "DX vs VPN."

**Senior**: "Design hybrid with HA."

**Staff**: "Cost analysis: on-prem DB replicates 10 TB/day to cloud."

## Next Topic

→ [T04 — BGP and Anycast](T04-BGP-Anycast.md)
