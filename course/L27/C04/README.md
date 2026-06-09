# L27/C04 — Failover Mechanics

## Topics

- **T01 DNS-Based Failover** — Slowest but simplest
- **T02 Health Checks** — Trigger of failover
- **T03 Failover Automation** — Reduce human latency

## DNS Failover

### How
- DNS records have multiple targets
- Health checks determine which are returned
- Failover by changing what DNS returns

### Route 53 Example
```
api.example.com (failover routing policy)
  - Primary: ALB in us-east-1 (TTL 60)
  - Secondary: ALB in us-west-2 (TTL 60)
  Health check on primary; if fails, secondary returned
```

### Caveats
- DNS resolvers cache (TTL not always respected)
- JVMs cache forever by default
- Real cutover: 1-5 minutes typical
- Pre-existing connections continue to primary (until they close)

### Use
- Tier 2-3 services where minutes are OK

## Anycast Failover

Withdraw anycast advertisement from failing region; internet routing shifts.

- Faster than DNS (seconds)
- TCP connections survive most of the time
- Used by Cloudflare, Global Accelerator

## Application-Level Failover

App detects backend unhealthy; switches to alternative.

### Patterns
- Circuit breaker (mentioned in L25)
- Multi-region client library (try region A, fail to region B)
- Backend pool with health-aware load balancing

### Pros
- Fastest (sub-second)
- App in control
- No DNS dependency

### Cons
- Client logic complexity
- App must know about all regions

## DB Failover

### RDS Multi-AZ
- Sync standby
- Auto-failover (~60s)
- DNS endpoint repoints

### Aurora
- Storage shared; failover ~30s
- Multiple readers; promote one

### Aurora Global Database
- Cross-region; ~1s replication lag
- Manual promote in DR region

### Custom (Postgres + Patroni)
- Patroni elects new leader via DCS
- Promote replica; new leader becomes primary
- Updates DNS or load balancer

### Multi-Region DB
- App writes locally; replicates async
- On region failure: traffic to surviving region
- App must tolerate eventual consistency

## Health Checks

### Active
LB / health check service pings target.
```
GET /healthz
  return 200 if healthy
  return 503 if unhealthy
```

### Health Endpoint Design
- Lightweight (no expensive DB queries)
- Check critical dependencies (or use separate /readyz)
- Return reason on failure

### Liveness vs Readiness
- **Liveness**: am I alive?
- **Readiness**: am I ready for traffic?

### Cascading Failure Risk
If health check depends on DB:
- DB blip → health check fails → LB removes all backends → outage
- Fix: shallow health check; deeper checks separate

## Auto vs Manual Failover

### Auto
- Health check fails N times → cut over
- Risk: false positive

### Semi-Auto
- Health check fails → page on-call
- On-call reviews + triggers
- More accurate but slower

### Manual
- Human assesses
- Triggers via runbook
- Safest, slowest

### Hybrid (Common)
- AZ-level: automatic (Multi-AZ DB failover)
- Region-level: semi-auto (human + bot)
- Major changes: manual approval

## Failover Time Components

```
Detection (health check fails) ............. T_detect
   ↓
Decision (auto or human) ................... T_decide
   ↓
Cutover (DNS update / promote / LB switch).. T_cutover
   ↓
Propagation (DNS resolvers, client caches).. T_propagate
   ↓
Service restored to users
```

Each component contributes. Optimize each.

## Pre-Tested Failover

Test failover regularly (Game Days). Ensure:
- DR region can absorb load
- Data is synced
- Runbook works
- Personnel know steps

Untested DR usually fails.

## Failback

After primary recovers:
1. Verify primary healthy
2. Replicate DR → primary
3. Wait for catch-up
4. Schedule failback window (low traffic)
5. Cut traffic back
6. Verify

Often: stay on DR until next planned window.

## Common Failover Failures

- DNS TTL too long
- App caches old endpoint
- DB replica wasn't promoted properly
- Authentication tokens region-specific
- Cross-region IAM permissions missing
- DR region scaled down (can't absorb load)
- Failover takes longer than RTO

## Multi-Region Stateful App Gotchas

- Session state in region-specific cache → user logged out
- Pending writes in primary not replicated → data loss
- Long-running connections (WebSocket) → broken
- Cross-region replication paused due to throttling → stale

Design with failover in mind from day 1.

## Interview Themes

- "DNS failover — speed and pitfalls"
- "Anycast vs DNS for failover"
- "Health check design"
- "Auto vs manual failover — when each?"
- "Failback procedure"
