# L07/C07 — Cloud Networking Primitives

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-VPC-Subnets.md) | VPC, Subnets, Route Tables (Across Clouds) | 1 hr |
| [T02](T02-Load-Balancers.md) | Load Balancers (L4, L7) | 1 hr |
| [T03](T03-DNS-CDN.md) | DNS, CDN | 0.5 hr |
| [T04](T04-Cross-Region.md) | Cross-Region Networking | 0.5 hr |

## VPC Concepts Across Clouds

| | AWS | GCP | Azure |
|---|---|---|---|
| Top-level network | VPC | VPC (global!) | VNet |
| Subnet | Per AZ | Per region | Per AZ-subnet |
| Internet path | IGW + NAT GW | Default route to Internet + Cloud NAT | Internet (default) |
| Private connectivity | VPC endpoints | Private Service Connect | Private endpoints |
| Hub model | Transit Gateway | NCC / VPC Network Peering | vWAN |
| ACL | Security Groups + NACLs | Firewall rules (per VPC, applied via tags/SAs) | NSGs |

**Notable GCP difference**: VPC is global. A single VPC spans regions; subnets are regional. AWS VPC is regional; subnets are AZ-scoped.

## Subnets

```
VPC CIDR 10.0.0.0/16
├── public subnet  10.0.1.0/24 → route 0/0 to IGW
├── private subnet 10.0.10.0/24 → route 0/0 to NAT
└── isolated       10.0.20.0/24 → no Internet route
```

Reserve enough space:
- /16 for production VPC
- /20 minimum per subnet
- Plan for growth, not start small

AWS reserves 5 IPs per subnet (first 4, last 1).

## Load Balancers

### Layer 4 (TCP/UDP)
- Routes based on connection (4-tuple)
- Faster, less feature-rich
- Sticky source IP optional
- Examples: AWS NLB, GCP TCP LB, Azure LB

### Layer 7 (HTTP/HTTPS)
- Routes based on URL, method, headers, host
- TLS termination
- Path-based routing
- Authentication, WAF integration
- Examples: AWS ALB, GCP HTTP(S) LB, Azure Application Gateway

### Health Checks
- Active (LB probes targets) — most common
- Passive (count failed requests)
- TCP, HTTP, gRPC, custom

### When L4 vs L7

| Need | Pick |
|---|---|
| WebSocket, raw TCP | L4 (NLB) |
| HTTPS with path/host routing | L7 (ALB) |
| Lowest latency | L4 (NLB; no L7 inspection) |
| WAF integration | L7 (ALB + WAF) |
| Hybrid (some L7, some L4) | Both; or use ALB → NLB chain |

## DNS as a Service

- **Route 53 (AWS)** — extensive routing policies (geo, latency, weighted, failover)
- **Cloud DNS (GCP)** — basic + private zones
- **Azure DNS** — basic + private zones

Use cases:
- Public DNS for your domain
- Private DNS for internal services (often integrated with VPC)
- Failover routing
- Geo-routing

## CDN

| | AWS | GCP | Azure |
|---|---|---|---|
| CDN | CloudFront | Cloud CDN | Azure CDN, Front Door |
| WAF | AWS WAF | Cloud Armor | Front Door WAF |
| DDoS | Shield (free std, paid adv) | Cloud Armor | DDoS Protection |
| Edge compute | Lambda@Edge, CF Functions | Cloud Run on Edge | Front Door rules engine |

## Cross-Region Networking

- **Inter-region VPC peering** (AWS) — works, costs egress
- **Transit Gateway peering** — for hub-and-spoke
- **GCP global VPC** — same VPC spans regions; no peering needed
- **Azure Global VNet Peering** — connects VNets across regions

Egress cost ~$0.02/GB cross-region within same cloud. Cross-cloud egress: full Internet rates.

## Private Connectivity

### AWS PrivateLink / VPC Endpoints
- Connect VPC to AWS services without going through Internet
- Free for Gateway endpoints (S3, DynamoDB)
- Hourly + data charge for Interface endpoints

### Azure Private Endpoint / Private Link
- Same concept

### GCP Private Service Connect
- Same concept

These are how you keep traffic to AWS APIs / S3 inside your VPC (not over NAT GW).

## Bandwidth Limits

- **Within AZ**: ~10–25 Gbps per instance (instance-class dependent)
- **Within region (cross-AZ)**: same
- **Across regions**: depends on egress instance + LB
- **NAT GW**: ~45 Gbps per gateway
- **Per-region egress**: varies, but you can ask AWS for increases

## Interview Themes

- "Compare L4 and L7 load balancing"
- "How is GCP VPC different from AWS VPC?"
- "When PrivateLink vs NAT GW?"
- "Design a multi-region network architecture"
- "Where does TLS terminate in your design?"
