# L07/C01/T04 — Regions, Availability Zones, Edge Locations

## Learning Objectives

- Understand geographic abstractions
- Design for failure domains

## Region

Geographic area. Examples:
- AWS: `us-east-1` (N. Virginia), `eu-west-1` (Ireland)
- GCP: `us-central1` (Iowa), `europe-west1` (Belgium)
- Azure: `East US`, `West Europe`

Each region:
- Independent (failure isolation)
- Different services available
- Different pricing
- Latency between is real (5-200ms)

Region selection criteria:
- Close to users (latency)
- Compliance (data residency)
- Pricing
- Service availability
- DR pairing (cross-region)

## Availability Zone (AZ)

Failure-isolated facility within a region.
- AWS: 3-6 AZs per region (`us-east-1a`, `us-east-1b`, ...)
- GCP: 3 zones per region
- Azure: 3 zones in supported regions

Each AZ:
- Separate power
- Separate cooling
- Separate network
- Connected via low-latency links (<10ms)

Design rule: critical services in 3+ AZs. If one AZ fails, others continue.

## Edge Location / PoP

Smaller facility for content delivery (CDN, DNS):
- AWS: 600+ edge locations (CloudFront)
- Cloudflare: 320+ cities
- GCP: 200+ edge nodes

Used for:
- CDN content
- DNS (Route53, etc.)
- Edge compute (Lambda@Edge, Workers)
- DDoS absorption

Not for full compute (no DBs, no full VMs).

## Local Zones / Outposts

Bring cloud closer:
- AWS Local Zones: cities for low-latency
- AWS Outposts: AWS gear in your DC
- Azure Edge Zones, GCP Distributed Cloud

For when even nearest region is too far (real-time gaming, media production).

## Latency Matrix (Sample, AWS)

| | us-east-1 | us-west-2 | eu-west-1 | ap-southeast-1 |
|---|---|---|---|---|
| us-east-1 | <1ms | 70ms | 75ms | 230ms |
| us-west-2 | 70ms | <1ms | 145ms | 165ms |
| eu-west-1 | 75ms | 145ms | <1ms | 175ms |
| ap-southeast-1 | 230ms | 165ms | 175ms | <1ms |

Within AZ in region: <1ms (microseconds).
Cross-AZ within region: 1-2ms.

## Service Tiering by Geography

**Global**: IAM, Route53, CloudFront, S3 buckets (but data in region).

**Regional**: most everything else (EC2, RDS, SQS, VPC).

**Zonal**: EC2 instance is in one AZ; EBS volume is in one AZ.

Replicate across AZs/regions for HA/DR.

## Replication Strategies

### Within Region (HA)
- RDS Multi-AZ: synchronous replica in another AZ; auto failover
- DynamoDB: replicated to multiple AZs automatically
- S3: 11 9s durability across multiple AZs
- ALB: routes across AZs

Goal: AZ failure ≠ user impact.

### Cross Region (DR)
- S3 Cross-Region Replication (async)
- RDS read replica in another region (async)
- DynamoDB Global Tables (multi-region active-active)
- Route53 health checks for failover

Goal: regional failure ≠ business down.

## Choosing Region

For latency-sensitive: closest to most users.
For DR: pair (us-east-1 + us-west-2; not 2 in same area).
For data residency: in country.
For cost: some regions cheaper (us-east-1 cheapest in AWS).
For new services: some regions get features first (typically us-east-1).

## Distance From Region

Speed of light: ~200km/ms one-way; ~100km/ms round-trip in fiber.

Tokyo → London: ~9000 km → ~180ms RTT minimum. Real: 220ms.

If users are in Tokyo and your DB is in US, every query = 200ms. Multiply by query count.

## Multi-Region Patterns

**Active-Passive**: primary handles all; secondary on standby. RTO: minutes.

**Active-Active**: traffic split between regions. RTO: seconds.

**Read-Local Write-Global**: reads local; writes go to one primary region.

**Cell-Based**: independent cells; users mapped to one cell.

Tradeoff: complexity (active-active) vs RTO/RPO.

## Failure Reality

Cloud failures span every domain — AZ, region, and provider-global. Notable cases:
- 2017 AWS S3 (us-east-1): a typo during a debugging command took down the S3 control plane — a **regional service disruption** (not a single-AZ failure); it cascaded to other us-east-1 services for hours
- 2019 GCP global: bad config; multi-region failure
- 2021 Facebook BGP: global outage
- 2023 multiple us-east-1 disruptions

Note: the 2017 S3 event is a *regional* outage, not an AZ one — multi-AZ alone would not have saved you, which is exactly why tier-0 systems need multi-region.

Don't bet on cloud being up. Multi-AZ minimum; multi-region for tier-0.

## Failure Domains

Smaller → bigger:
- Rack
- Row
- Data center (AZ)
- Region
- Provider
- Internet (BGP)

Design knows the boundary you're protecting against.

## Network Inside vs Outside

In-region/AZ: free or cheap.
Cross-region: $0.01-0.09/GB
Cross-cloud: $0.09/GB+
To Internet: $0.05-0.15/GB

Egress is where cloud bills inflate.

## Service Mesh Across Regions

Mesh (Istio, Linkerd) often per-cluster.
For cross-cluster: Istio Multi-Cluster, Cilium Cluster Mesh.
Complexity high; do only if needed.

## Common Mistakes

- Deploying everything in a single AZ — one facility's power/cooling/network failure takes the whole app down; spread across 3+ AZs.
- Assuming multi-AZ protects against regional outages — the 2017 us-east-1 S3 event hit the whole region; tier-0 systems need multi-region.
- Hard-coding `us-east-1` "because it's cheapest/has new services first" without considering user latency or its outage history.
- Ignoring the speed-of-light floor — no architecture removes the ~180ms+ RTT between Tokyo and London; put data near users instead.
- Forgetting that EC2 instances and EBS volumes are *zonal* — losing the AZ loses both unless you replicated/snapshotted across AZs.
- Underestimating cross-region/egress charges in multi-region designs — replication traffic at $0.01–0.09/GB adds up fast.

## Best Practices

- Run stateless tiers in 3+ AZs behind a load balancer; use AZ-aware managed services (RDS Multi-AZ, DynamoDB) for stateful tiers.
- Pick a DR region that is geographically distinct (e.g. us-east-1 + us-west-2), not two regions in the same area.
- Choose the primary region by user latency and data-residency first, cost second.
- Define explicit RTO/RPO targets and match the multi-region pattern to them (active-passive for minutes, active-active for seconds).
- Keep the source of truth regional and push read-heavy/latency-sensitive content to edge locations and CDNs.
- Budget and monitor cross-AZ, cross-region, and internet egress as first-class cost lines.

## Quick Refs

Failure domains, smallest to largest — design to the boundary you're protecting against:

| Domain | Protect with |
|---|---|
| Rack / row | Multiple instances |
| AZ (data center) | Multi-AZ deployment |
| Region | Multi-region replication / failover |
| Provider | Multi-cloud (only if justified) |
| Internet / BGP | CDN + multiple providers/anycast |

Scope of resources (interview classic):

| Scope | Examples |
|---|---|
| Global | IAM, Route 53, CloudFront, S3 bucket namespace |
| Regional | VPC, RDS, SQS, ELB |
| Zonal | EC2 instance, EBS volume |

Latency rules of thumb: within AZ <1ms, cross-AZ 1–2ms, cross-region 70–230ms. Fiber RTT ≈ 1ms per ~100km round trip.

## Interview Prep

**Junior**: "AZ vs region."

**Mid**: "Why design across AZs?"

**Senior**: "Active-Active multi-region tradeoffs."

**Staff**: "Cell-based architecture."

## Next Topic

→ Move to [L07/C02 — Cloud Economics](../C02/README.md)
