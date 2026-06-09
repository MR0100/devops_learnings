# L07/C07/T04 — Cross-Region Networking

## Learning Objectives

- Connect resources across regions
- Manage costs and latency

## Why Cross-Region

- DR (active-passive)
- Active-active for low latency to users globally
- Data sovereignty (data per region)
- Acquisitions (different teams in different regions)

## Latency Reality

| Path | RTT |
|---|---|
| Same AZ | <1ms |
| Same region (cross-AZ) | 1-2ms |
| US-East to US-West | ~70ms |
| US to Europe | ~80-100ms |
| US to Asia | ~150-200ms |

Each round-trip across regions: expensive.

## Cost Reality

Data transfer:
- Same region intra-AZ: free (most services)
- Same region cross-AZ: $0.01/GB each way
- Cross-region: $0.02-0.09/GB
- Egress to Internet: $0.09/GB

For 1 TB/day cross-region: $20-90/day = $7k-32k/year.

## Connection Options

### VPC Peering
- Direct connection between 2 VPCs (any region)
- Free traffic in same region; cross-region pricing for inter-region
- Non-transitive

### Transit Gateway
- Hub connects many VPCs
- Cross-region TGW peering
- More cost; more flexible

### CloudWAN
- AWS managed wide-area network
- Connects branches, on-prem, multi-region

### Direct Connect / ExpressRoute / Interconnect
- Dedicated line; cross-region if needed

### VPN over Internet
- Cheapest; variable latency

## Data Replication

### S3 Cross-Region Replication
Async copy to bucket in another region.
- Cost: storage in both + replication API + xregion bandwidth
- RPO: minutes typical

### DynamoDB Global Tables
Multi-region active-active. Last-writer-wins. RPO: seconds.

### Aurora Global Database
Cross-region async replica; <1s RPO. Promote on failover.

### RDS Cross-Region Read Replica
Async; manually promote.

### EBS Snapshot Copy
Copy snapshot to another region for restore.

## DR Patterns

### Backup-Restore
- Snapshots, DB dumps to other region
- RTO: hours
- RPO: depends on backup frequency
- Cheapest

### Pilot Light
- Minimal infra in DR region (DB replica, dormant compute)
- Activate on disaster
- RTO: 10s of minutes
- RPO: minutes

### Warm Standby
- Scaled-down version running in DR
- Scale up on disaster
- RTO: minutes
- RPO: seconds

### Multi-Site Active-Active
- Full capacity in both regions
- Route traffic to nearest or distribute
- RTO: seconds (DNS failover)
- RPO: ~0
- Most expensive; most complex

## Active-Active Considerations

- Data conflict resolution (multi-master writes)
- Cost: 2× compute
- Operational: change in both
- Routing: latency or weighted
- Testing: regularly fail one over

## DNS Failover

Route53 health checks → failover record:
```
Primary: us-east-1 LB
Secondary: us-west-2 LB
```

If primary unhealthy → secondary served. ~60s.

## Global Accelerator

AWS service: 2 anycast IPs serve traffic globally; route to optimal region. Low latency; better than DNS-based.

Cost: $0.025/hour + data.

## GCP Global Load Balancing

One anycast IP serves globally. Routes to nearest healthy region. Built-in.

Often simpler than AWS Global Accelerator + Route53 latency routing.

## Edge Locations

CDN POPs reduce cross-region needs:
- Static content cached at edge
- Origin in fewer regions
- Edge compute for personalization

Reduces inter-region calls.

## Service Mesh Across Regions

Istio multi-cluster, Linkerd multicluster, Cilium ClusterMesh:
- Cross-cluster service discovery
- mTLS across regions
- Failover

Adds operational complexity.

## CDN as DR

CDN can serve static when origin down:
- Stale-while-revalidate
- Custom error pages
- Limited but useful

## Database Strategies

### Single Region (Multi-AZ)
HA within region. DR via cross-region replica.

### Multi-Region Read
Primary in one region; reads global. Writes go to primary.

### Multi-Region Active-Active
Hard. Conflict resolution. DynamoDB Global Tables, CockroachDB, Spanner make easier.

### Sharded by Region
Each region's users on regional shard. Simplifies; locks users to region.

## Cost Optimization

- CDN at edge (avoid full inter-region traffic)
- Compress data
- Batch writes
- Read locally; write globally
- Avoid chatty cross-region calls
- Use endpoints where possible

## Anti-Patterns

- App in US calls DB in EU (200ms per query × 10 queries = 2s)
- Hot region failover with no testing
- Cross-region calls in tight loop
- No CDN; raw egress at scale

## Active-Active Architectures

- Each region full stack
- Data replication
- Conflict resolution
- Global DNS / Accelerator routes users

Example: Netflix, Spotify, Slack each have multi-region active-active.

## Network Path Analysis

Track:
- Where is data?
- Where is compute?
- How many round-trips per user action?
- What goes cross-region?

Minimize cross-region per user request.

## Multi-Region Anti-Pattern: Active-Active DB Without Plan

Writes happen in both regions; conflicts (alice@email taken in both). Resolution: vendor's last-writer-wins → data loss.

Real solution: regional shards (alice's account region-locked) OR consensus DB (Spanner/CockroachDB; latency cost).

## Monitoring

Cross-region:
- Latency between regions
- Replication lag
- Data transfer cost per service

## When Multi-Region

- Tier-0 service with <1 hr RTO required
- Global users with latency targets
- Compliance per region
- Massive scale exceeding one region

If not these: single-region multi-AZ is enough.

## Interview Prep

**Mid**: "DR strategies — RTO/RPO."

**Senior**: "Multi-region active-active database."

**Staff**: "Tier-0 service cross-region — design."

## Next Topic

→ Move to [L07/C08 — IAM](../C08/README.md)
