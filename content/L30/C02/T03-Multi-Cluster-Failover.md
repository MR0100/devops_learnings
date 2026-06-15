# L30/C02/T03 — Cross-Region Failover

## Learning Objectives

- Implement failover
- Test

## Why Failover Is the Whole Point

This is the topic that *proves* the multi-region project — a demo where you kill
a region and traffic shifts is the single most memorable thing on the resume. It
forces you to confront the two numbers every interviewer probes: **RTO** (how
long until service is restored) and **RPO** (how much data you can lose). The
architecture is mostly a set of decisions that trade those two against cost and
complexity.

### The Levers (and Their Trade-offs)

- **Detection** — Route 53 health checks (3 failures × 30s ≈ 90s) plus synthetic
  monitoring. Faster checks detect sooner but flap more.
- **Traffic shift** — DNS failover is simple but bounded by TTL + client caching
  (~2–3 min realistic); anycast (Global Accelerator) shifts in seconds at higher
  cost.
- **Data** — Aurora Global (~1s replication lag → small RPO, manual/automated
  promotion) vs. DynamoDB Global Tables (multi-active, near-zero RPO, but
  last-writer-wins conflict semantics). The DB choice *is* your RPO.
- **App** — stateless apps failover trivially; anything stateful is where the
  hard RPO trade-offs live.

The honest senior framing: you don't "achieve zero RTO/RPO," you *choose* a
point on the curve and justify it against the SLA and the bill.

## Failover Strategy

```
us-east-1 → unhealthy
  ↓
Detection (CloudWatch / Synthetic)
  ↓
DNS update (Route 53)
  ↓
Traffic to us-west-2
  ↓
DB primary promotion
  ↓
App functions
```

## Components

### Health Check
- Route 53 health check
- Synthetic monitoring
- Multi-source

### DNS
- Failover record
- TTL 60s

### App
- Stateless (easy failover)
- Connection retries

### DB
- Aurora Global (1-sec lag)
- Promote on failure

### Cache
- Cross-region replication or rebuild

## Aurora Global

```bash
aws rds create-global-cluster \
  --global-cluster-identifier global-app \
  --source-db-cluster-identifier primary
```

Promote:
```bash
aws rds failover-global-cluster \
  --global-cluster-identifier global-app \
  --target-db-cluster-identifier secondary
```

## App

Connection string:
```
primary.us-east-1.example.com → fail
secondary.us-west-2.example.com → succeed
```

Or single endpoint with failover.

## Testing

Quarterly drill:
- Block primary
- Verify auto-failover
- Measure RTO

## Best Practices

- Automated detection
- DNS or anycast
- DB replication
- Stateless apps
- Drill quarterly

## Common Mistakes

- Manual failover (slow)
- No DB replication (data loss)
- Sync cross-region (slow writes)
- Never tested

## Acceptance Criteria

- A scripted, repeatable failure injection (scale primary to 0 / block its
  health endpoint)
- Health check fails and traffic shifts to the secondary automatically — no
  human DNS edit
- A **measured** RTO (wall-clock from failure to recovery) recorded in the demo
- DB promotion works and you can state the RPO (replication lag at cutover)
- Recovery: primary restored, traffic returns, no manual cleanup

## Quick Refs

```
Detection: Route 53 health check (≈90s)   DNS: failover, ~2–3 min w/ TTL+caching
Faster: Global Accelerator (anycast, seconds, $$$)
DB: Aurora Global (small RPO) | DynamoDB Global Tables (multi-active, LWW)
App: stateless = trivial failover         Drill: quarterly, measure RTO each time
```

## Interview Prep

**Junior**: "What are RTO and RPO?" — RTO is how long it takes to recover service
after a failure (downtime). RPO is how much data you can afford to lose, measured
in time (e.g. 'up to 5 seconds of writes'). DR designs are mostly about hitting
target RTO and RPO numbers.

**Mid**: "How does cross-region failover actually shift traffic?" — A health
check (e.g. Route 53) detects the primary is down, and a failover DNS record
points users at the secondary region. Realistically that's a couple of minutes
because of DNS TTL and client-side caching. For seconds-level failover you use
anycast with Global Accelerator instead of DNS, at higher cost.

**Senior**: "Your failover took 3 minutes. Walk me through the budget and how
you'd cut it." — Roughly 90s detection (3 health-check failures × 30s) plus DNS
TTL (60s) plus client caching (~60s). To cut it: lower the health-check interval
and TTL (more sensitive, risk of flapping), or switch the traffic layer from DNS
to Global Accelerator anycast so the shift is near-instant and independent of
client DNS caching. The detection floor is the health-check math, so there's a
practical limit with DNS — beyond that you change mechanisms, not just tune
numbers. And I'd be explicit that faster failover means more false positives, so
the right target depends on the SLA.

**Staff**: "How do you make sure this failover actually works when you need it,
not just in the demo?" — Untested DR is theater — the failure mode is discovering
at 3am that promotion has a permissions gap or the secondary's capacity was
scaled down to save money. So I'd institutionalize it: a quarterly game day that
injects the failure on a schedule, measures RTO/RPO against the documented
targets, and treats any miss as an incident with a follow-up. I'd automate the
runbook so failover isn't a human remembering ten steps under pressure, and I'd
keep the secondary warm enough that it can actually take full load (a cold
standby that can't scale in time is a false sense of security). The deliverable
isn't 'we have a DR region,' it's 'we proved last quarter we can fail over in N
minutes losing under M seconds of data.'

## Next Topic

→ Move to [L30/C03 — Project 3: Observability Stack](../C03/README.md)
