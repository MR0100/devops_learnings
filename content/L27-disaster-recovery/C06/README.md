# L27/C06 — Region Evacuation

## Topics

- **T01 Pre-Drained Regions** — Always-ready DR
- **T02 Traffic Steering** — How to shift load

## Region Evacuation

> A planned or emergency removal of all traffic from a region.

### When
- Major regional issue (network, power, cloud provider outage)
- Cloud provider degraded service (announced or detected)
- Game day testing
- Maintenance (rare in cloud; common on-prem)
- Capacity rebalancing

## Pre-Drained Region

Concept: keep DR region pre-provisioned and traffic-ready, but not actively serving.

```
Region A (us-east-1): 100% traffic
Region B (us-west-2): 0% traffic; pre-warmed; ready to receive
```

### Why
- Cold DR fails when needed (capacity not pre-warmed; configs out of sync)
- Active-active is expensive (full 2× capacity)
- Pre-drained = warm + verified, ready in minutes

### Maintenance
- Periodically: shift 5-10% traffic to DR to verify
- Daily synthetics: prove DR is ready
- Configuration sync verified

## Traffic Steering

### DNS-Based
Route 53 weighted records. Shift weights:
```
Day 0: us-east 100, us-west 0
Day 1: us-east 90, us-west 10  (canary DR)
Day 2: us-east 50, us-west 50  (half-and-half)
```

Slow due to DNS TTLs.

### Anycast
AWS Global Accelerator endpoint weights:
- Adjust endpoint weights between regions
- Sub-minute global propagation

### Service Mesh
Istio VirtualService cross-cluster routing:
- Shift % between regional services
- L7 routing
- Per-route control

### LB Weights
Each region has its own LB; LB selects backends. For cross-region: requires LB that can route to backends in other region (Global Accelerator, Front Door).

## Evacuation Process

### Planned
1. Announce
2. Shift 10% traffic (canary)
3. Verify metrics (DR handles correctly)
4. Shift 50%
5. Verify
6. Shift 100%
7. Hold for stabilization
8. Verify
9. Done (until failback)

Each step: monitor SLOs, error rates, latency.

### Emergency
1. Confirm disaster (not flapping)
2. IC declares region evacuation
3. Switch DNS / weights to DR
4. Monitor traffic shift
5. Verify SLOs in DR
6. Communicate to leadership + customers

Compress: 5-15 minutes.

## Pre-Conditions for Evacuation

For DR region to absorb traffic:
- **Capacity**: scaled to handle peak (not just current)
- **Data**: replicated and current (RPO met)
- **Connectivity**: BGP / DNS / mesh routes operational
- **Auth**: tokens / sessions valid in DR
- **Dependencies**: upstreams accessible

If any of these fail → evacuation degrades or fails.

## Common Evacuation Failures

- **DR scaled smaller** → can't absorb peak load
- **Stale config in DR** → routes to wrong endpoints
- **Data not replicated** → app errors on missing data
- **Auth tokens region-specific** → users logged out en masse
- **Cross-region IAM permissions missing** → app can't reach AWS APIs
- **Pre-existing connections to primary** → take time to drain
- **DNS cached at clients** → ignore failover

Game day exercises find these before reality does.

## Capacity Math for Evacuation

```
Steady state: 60% utilization per region
On evacuation: surviving region absorbs 100%
Needed capacity: > 100% peak in single region

So pre-drained region must be 100% of peak capacity, not 50%.
This is the cost of active/passive multi-region.
```

Active-active at lower utilization (each at 30-40%) can be cheaper because each absorbs only 60-80% on failover.

## Failback

After incident resolved:
1. Verify primary region healthy
2. Replicate DR → primary
3. Sync caches
4. Cutover slowly (DNS / weights back)
5. Monitor
6. Stay on DR for next maintenance window (sometimes preferred)

## Multi-Region Cell Architecture (Combined)

Best of all worlds: cells + multi-region.
- Cells slice users
- Each cell has primary + DR region
- One cell evacuation = small blast radius

Amazon does this internally.

## Operational Practice

### Quarterly: Practice Evacuations
- Pick a region; shift traffic
- Monitor; revert
- Document findings

### Monthly: DR Readiness Check
- Capacity sufficient?
- Configs synced?
- Data current?
- Runbook correct?

### Continuous: Synthetic Traffic
- Small amount of real traffic to DR continuously
- Proves DR works for real requests, not just health checks

## Tools

- **AWS Route 53 + Global Accelerator** for steering
- **AWS Resilience Hub** assesses + manages
- **AWS Failover GameDay** (formerly AWS Fault Injection Simulator scenarios)
- **Custom dashboards** showing per-region SLOs
- **Multi-cluster service mesh** for fine-grained control

## Interview Themes

- "Region evacuation procedure"
- "Pre-drained region — value"
- "Capacity math for active-passive"
- "Game day for region evacuation"
- "Why evacuations fail in practice"
